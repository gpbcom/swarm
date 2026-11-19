//! Command line of the schema to Rust renderer: `swarm-models-codegen [--check]`.

use std::process::ExitCode;

use swarm_models_codegen::{default_output_path, default_schema_path, is_stale, write};

/// Writes the generated file, or with `--check` reports whether it is out of date.
fn main() -> ExitCode {
    let check = std::env::args().skip(1).any(|argument| argument == "--check");
    let schema = default_schema_path();
    let output = default_output_path();
    if check {
        match is_stale(&schema, &output) {
            Ok(true) => {
                eprintln!(
                    "{} is out of date. Run cargo run -p swarm-models-codegen to regenerate it.",
                    output.display()
                );
                ExitCode::from(1)
            }
            Ok(false) => {
                println!("{} is up to date.", output.display());
                ExitCode::SUCCESS
            }
            Err(error) => {
                eprintln!("{error}");
                ExitCode::from(2)
            }
        }
    } else if let Err(error) = write(&schema, &output) {
        eprintln!("{error}");
        ExitCode::from(2)
    } else {
        ExitCode::SUCCESS
    }
}
