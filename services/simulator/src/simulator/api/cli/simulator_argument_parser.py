from __future__ import annotations

# Standard library imports
from argparse import ArgumentParser
from pathlib import Path
from typing import ClassVar
from uuid import UUID

# First-party imports
from simulator.models.enums import SimulatorCommandName


class SimulatorArgumentParser(ArgumentParser):
    """The command line of ``swarm-simulator``: a command, ``--config`` and ``--mission-id``.

    Attributes:
        COMMAND_ARGUMENT (str): The name of the positional command.
        CONFIG_OPTION (str): The option that names the configuration file.
        MISSION_ID_OPTION (str): The option that names the Mission.
        DEFAULT_CONFIG (str): The default configuration file.
        LOGGER_FILE (str): The name of the logging configuration file, in the service ``conf`` folder.
        CONF_FOLDER (str): The name of the folder of the configuration files, in the service folder.
        SERVICE_FOLDER_DEPTH (int): How many folders separate this file from the service folder.
        EXIT_USAGE (int): The exit code of a command line or a configuration that is refused.
        COMMAND_HELP (str): The help of the command.
        CONFIG_HELP (str): The help of ``--config``.
        MISSION_ID_HELP (str): The help of ``--mission-id``.
        DESCRIPTION (str): The description of the program.

    Notes:
        - An argument that argparse refuses ends the program with exit code 2, which is ``EXIT_USAGE``.
    """

    COMMAND_ARGUMENT: ClassVar[str] = "command"
    CONFIG_OPTION: ClassVar[str] = "--config"
    MISSION_ID_OPTION: ClassVar[str] = "--mission-id"
    DEFAULT_CONFIG: ClassVar[str] = "conf/app.yaml"
    LOGGER_FILE: ClassVar[str] = "logger.yaml"
    CONF_FOLDER: ClassVar[str] = "conf"
    SERVICE_FOLDER_DEPTH: ClassVar[int] = 4
    EXIT_USAGE: ClassVar[int] = 2
    DESCRIPTION: ClassVar[str] = "The Swarm simulator."
    COMMAND_HELP: ClassVar[str] = "What to run: serve the commands of a Mission, or fly a route once."
    CONFIG_HELP: ClassVar[str] = "The configuration file."
    MISSION_ID_HELP: ClassVar[str] = "The Mission the flight belongs to. Required by fly."

    def __init__(self) -> None:
        """Declare the command and the two options."""
        super().__init__(description=self.DESCRIPTION)
        self.add_argument(
            self.COMMAND_ARGUMENT,
            choices=[name.value for name in SimulatorCommandName],
            help=self.COMMAND_HELP,
        )
        self.add_argument(self.CONFIG_OPTION, type=Path, default=Path(self.DEFAULT_CONFIG), help=self.CONFIG_HELP)
        self.add_argument(self.MISSION_ID_OPTION, type=UUID, default=None, help=self.MISSION_ID_HELP)

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def logger_path(cls) -> Path:
        """Return the logging configuration file of the service.

        Returns:
            Path: ``services/simulator/conf/logger.yaml``, found from this module's path.
        """
        service_folder = Path(__file__).resolve().parents[cls.SERVICE_FOLDER_DEPTH]
        return service_folder / cls.CONF_FOLDER / cls.LOGGER_FILE
