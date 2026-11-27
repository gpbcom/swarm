//! The `swarm-synthetic-drones` binary: a fleet of synthetic Drones that speak `MAVLink` over UDP.
//!
//! Drone `i` listens on `--bind:--base-port + i`. When every socket is bound the binary prints `ready` on its
//! standard output, then runs until it is killed. An invalid argument exits with the code 2 and a message on the
//! standard error.

use std::env;
use std::io::{self, Write};
use std::net::IpAddr;
use std::process::ExitCode;
use std::str::FromStr;

use opentelemetry::trace::{Span, Tracer};
use swarm_observability::{Signals, SignalsConfig};
use swarm_synthetic_drones::link::{Fleet, FleetConfig};

/// The `service.name` of the signals of this process.
const SERVICE_NAME: &str = "swarm-synthetic-drones";

/// The name of the span that covers the flight run.
const RUN_SPAN: &str = "swarm.synthetic_drones.run";

/// The name of the counter of the `MAVLink` frames the Drones sent.
const FRAMES_SENT_METRIC: &str = "swarm.mavlink.frames_sent";

/// The exit code of a refused argument or a fleet that could not start.
const EXIT_REFUSED: u8 = 2;

/// The usage printed by `--help` and after a refused argument.
const USAGE: &str = "usage: swarm-synthetic-drones [--count N] [--bind ADDR] [--base-port P] [--system-id-base S] \
[--home-lat-e7 N] [--home-lon-e7 N] [--spacing-m M] [--speed-m-s M] [--tick-ms MS]";

/// What the command line asks for.
#[derive(Debug, PartialEq)]
enum Command {
    /// Print the usage and stop.
    Help,
    /// Run a fleet.
    Run(FleetConfig),
}

/// Parses the value of `flag`, or says why it cannot.
fn value<T: FromStr>(flag: &str, text: &str) -> Result<T, String> {
    text.parse()
        .map_err(|_| format!("invalid {flag}: {text:?} is not a valid value"))
}

/// Parses the arguments, without the program name, into a command.
fn parse(arguments: impl IntoIterator<Item = String>) -> Result<Command, String> {
    let mut config = FleetConfig::default();
    let mut arguments = arguments.into_iter();
    while let Some(flag) = arguments.next() {
        if flag == "--help" || flag == "-h" {
            return Ok(Command::Help);
        }
        let Some(text) = arguments.next() else {
            return Err(format!("missing the value of {flag}"));
        };
        match flag.as_str() {
            "--count" => config.count = value::<u8>(&flag, &text)?,
            "--bind" => config.bind = value::<IpAddr>(&flag, &text)?,
            "--base-port" => config.base_port = value::<u16>(&flag, &text)?,
            "--system-id-base" => config.system_id_base = value::<u8>(&flag, &text)?,
            "--home-lat-e7" => config.home_lat_e7 = value::<i32>(&flag, &text)?,
            "--home-lon-e7" => config.home_lon_e7 = value::<i32>(&flag, &text)?,
            "--spacing-m" => config.spacing_m = value::<f32>(&flag, &text)?,
            "--speed-m-s" => config.speed_m_s = value::<f32>(&flag, &text)?,
            "--tick-ms" => config.tick_ms = value::<u32>(&flag, &text)?,
            _ => return Err(format!("unknown argument {flag}")),
        }
    }
    config.validate().map_err(|error| error.to_string())?;
    Ok(Command::Run(config))
}

/// Prints `message` and the usage on the standard error, and returns the refusal code.
fn refuse(message: &str) -> ExitCode {
    eprintln!("swarm-synthetic-drones: {message}");
    eprintln!("{USAGE}");
    ExitCode::from(EXIT_REFUSED)
}

fn main() -> ExitCode {
    let config = match parse(env::args().skip(1)) {
        Ok(Command::Help) => {
            println!("{USAGE}");
            return ExitCode::SUCCESS;
        }
        Ok(Command::Run(config)) => config,
        Err(message) => return refuse(&message),
    };
    let mut fleet = match Fleet::new(&config) {
        Ok(fleet) => fleet,
        Err(error) => return refuse(&error.to_string()),
    };
    let mut stdout = io::stdout();
    if writeln!(stdout, "ready").and_then(|()| stdout.flush()).is_err() {
        return refuse("cannot write on the standard output");
    }
    fly(&mut fleet);
    ExitCode::SUCCESS
}

/// Runs the fleet with its signals: one span for the run and the count of the frames sent, with no `drone_id`.
///
/// A collector that is missing, unreachable or slow only costs the signals: they are exported from background
/// threads, and a signals set-up that fails is logged on the standard error and the flight goes on without it.
fn fly(fleet: &mut Fleet) {
    let signals = match Signals::start(&SignalsConfig::from_env(SERVICE_NAME)) {
        Ok(signals) => signals,
        Err(error) => {
            eprintln!("swarm-synthetic-drones: signals disabled: {error}");
            fleet.run();
        }
    };
    let mut span = signals.tracer().start(RUN_SPAN);
    let frames = signals.meter().u64_counter(FRAMES_SENT_METRIC).build();
    fleet.run_until(|fleet| {
        let sent = fleet.take_frames_sent();
        if sent > 0 {
            frames.add(sent, &[]);
        }
        true
    });
    span.end();
    signals.shutdown();
}

#[cfg(test)]
mod tests {
    use super::*;

    fn arguments(text: &str) -> Vec<String> {
        text.split_whitespace().map(str::to_owned).collect()
    }

    #[test]
    fn no_argument_runs_the_defaults() {
        assert_eq!(parse(arguments("")), Ok(Command::Run(FleetConfig::default())));
    }

    #[test]
    fn every_flag_sets_its_field() {
        let line = "--count 3 --bind 0.0.0.0 --base-port 20000 --system-id-base 7 --home-lat-e7 1 --home-lon-e7 2 \
                    --spacing-m 2.5 --speed-m-s 30 --tick-ms 20";
        let expected = FleetConfig {
            count: 3,
            bind: "0.0.0.0".parse().unwrap(),
            base_port: 20_000,
            system_id_base: 7,
            home_lat_e7: 1,
            home_lon_e7: 2,
            spacing_m: 2.5,
            speed_m_s: 30.0,
            tick_ms: 20,
        };
        assert_eq!(parse(arguments(line)), Ok(Command::Run(expected)));
    }

    #[test]
    fn bad_arguments_are_refused() {
        for line in [
            "--count 0",
            "--count 256",
            "--count x",
            "--count",
            "--bind nowhere",
            "--tick-ms 0",
            "--unknown 1",
        ] {
            assert!(parse(arguments(line)).is_err(), "{line} should be refused");
        }
    }

    #[test]
    fn help_asks_for_the_usage() {
        assert_eq!(parse(arguments("--help")), Ok(Command::Help));
    }
}
