from __future__ import annotations

# Standard library imports
from logging import getLogger
from typing import Optional
from uuid import UUID

# First-party imports
from simulator.api.cli.commands.command import Command
from simulator.api.cli.simulator_argument_parser import SimulatorArgumentParser
from simulator.api.factories.fly.fly_command_factory import FlyCommandFactory
from simulator.api.factories.serve.serve_command_factory import ServeCommandFactory
from simulator.models.config.simulator_config import SimulatorConfig
from simulator.models.enums import SimulatorCommandName
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig


def main() -> None:
    """Parse the command line, load the configuration, then run the serve or the fly command.

    Raises:
        SystemExit: With 2 when the command line or the configuration is refused, otherwise with the exit code of
            the command when it is not 0.

    Notes:
        - Logging is configured once, here at the entry point, with the ``conf/logger.yaml`` of the service.
        - Only ``api/cli/`` prints, because this output is for the person at the terminal.
        - The broad ``except`` around the configuration reports any failure of loading it, whatever its type,
          because each section of the configuration has its own exception.
    """
    arguments = SimulatorArgumentParser().parse_args()
    logger_path = SimulatorArgumentParser.logger_path()
    LoggingConfigurator(LoggingConfig(path=str(logger_path) if logger_path.is_file() else None)).configure()
    logger = getLogger(__name__)
    name = SimulatorCommandName(arguments.command)
    try:
        config = SimulatorConfig.load(arguments.config)
    except Exception as error:
        logger.error("The configuration %s is refused by %s.", arguments.config, type(error).__name__)
        print(f"Invalid configuration {arguments.config}: {error}")
        raise SystemExit(SimulatorArgumentParser.EXIT_USAGE) from error
    command: Command
    match name:
        case SimulatorCommandName.SERVE:
            logger.debug("Serving the commands of the Simulator.")
            command = ServeCommandFactory(config).create()
        case SimulatorCommandName.FLY:
            mission_id: Optional[UUID] = arguments.mission_id
            if mission_id is None:
                logger.error("The fly command needs --mission-id.")
                print(f"The {SimulatorCommandName.FLY} command needs {SimulatorArgumentParser.MISSION_ID_OPTION}.")
                raise SystemExit(SimulatorArgumentParser.EXIT_USAGE)
            command = FlyCommandFactory(config, mission_id).create()
    command.execute()
    if command.exit_code != 0:
        logger.error("The %s command ended with exit code %d.", name, command.exit_code)
        raise SystemExit(command.exit_code)
