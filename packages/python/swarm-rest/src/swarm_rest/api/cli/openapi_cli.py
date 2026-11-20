from __future__ import annotations

# Standard library imports
import argparse
from logging import Logger, getLogger
from pathlib import Path
from typing import Callable, ClassVar, Optional, Sequence

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_rest.api.factories.openapi_export_command_factory import OpenApiExportCommandFactory


class OpenApiCli:
    """The command line that exports the OpenAPI document of a service.

    Attributes:
        CHECK_OPTION (ClassVar[str]): The option that compares instead of writing.
        OUTPUT_OPTION (ClassVar[str]): The option that names the file.
        CHECK_DEST (ClassVar[str]): The name under which the parser stores ``--check``.
        OUTPUT_DEST (ClassVar[str]): The name under which the parser stores ``--output``.
        STORE_TRUE (ClassVar[str]): The argparse action of a flag.
        EXIT_USAGE (ClassVar[int]): The exit code of a usage error.
        DESCRIPTION (ClassVar[str]): The description of the command.
        CHECK_HELP (ClassVar[str]): The help of ``--check``.
        OUTPUT_HELP (ClassVar[str]): The help of ``--output``.
        build_app (Callable[[], FastAPI]): Builds the application whose document is exported.
        default_output (Path): The file used without ``--output``.
        logger (Logger): Logger instance.
    """

    CHECK_OPTION: ClassVar[str] = "--check"
    OUTPUT_OPTION: ClassVar[str] = "--output"
    CHECK_DEST: ClassVar[str] = "check"
    OUTPUT_DEST: ClassVar[str] = "output"
    STORE_TRUE: ClassVar[str] = "store_true"
    EXIT_USAGE: ClassVar[int] = 2
    DESCRIPTION: ClassVar[str] = "Write the OpenAPI document of the service, or check that the file is up to date."
    CHECK_HELP: ClassVar[str] = "Fail when the file is missing or out of date, and write nothing."
    OUTPUT_HELP: ClassVar[str] = "The file to write or check."

    def __init__(self, build_app: Callable[[], FastAPI], default_output: Path, logger: Optional[Logger] = None) -> None:
        """Initialise the command line.

        Args:
            build_app (Callable[[], FastAPI]): Builds the application whose document is exported.
            default_output (Path): The file used without ``--output``.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.build_app = build_app
        self.default_output = default_output
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _parser(self) -> argparse.ArgumentParser:
        """Build the argument parser.

        Returns:
            argparse.ArgumentParser: A parser with ``--check`` and ``--output``.
        """
        parser = argparse.ArgumentParser(description=self.DESCRIPTION)
        parser.add_argument(self.CHECK_OPTION, dest=self.CHECK_DEST, action=self.STORE_TRUE, help=self.CHECK_HELP)
        parser.add_argument(self.OUTPUT_OPTION, dest=self.OUTPUT_DEST, type=Path, default=None, help=self.OUTPUT_HELP)
        return parser

    ############################
    # Publicly Exposed Methods #
    ############################

    def main(self, argv: Optional[Sequence[str]] = None) -> int:
        """Parse the arguments and export or check the document.

        Args:
            argv (Optional[Sequence[str]]): The arguments, without the program name. ``sys.argv`` when ``None``.

        Returns:
            int: ``0`` on success, ``1`` when ``--check`` finds a difference, ``2`` on a usage error.
        """
        try:
            arguments = vars(self._parser().parse_args(argv))
        except SystemExit as error:
            if isinstance(error.code, int):
                self.logger.debug("The arguments ended the program with code %d.", error.code)
                return error.code
            self.logger.debug("The arguments were refused.")
            return self.EXIT_USAGE
        output = arguments[self.OUTPUT_DEST]
        if output is None:
            self.logger.debug("No output given, using %s.", self.default_output)
            output = self.default_output
        factory = OpenApiExportCommandFactory(self.build_app(), output, bool(arguments[self.CHECK_DEST]))
        command = factory.create()
        command.execute()
        return command.exit_code
