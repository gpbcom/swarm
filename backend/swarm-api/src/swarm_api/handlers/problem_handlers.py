from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from logging import Logger, getLogger
from typing import ClassVar, Optional

# Third-party imports
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException

# First-party imports
from swarm_rest.models.problems.problem import Problem
from swarm_rest.models.rest.exceptions import SERestError


class ProblemHandlers:
    """Answers every error of an application as an ``application/problem+json`` document.

    Attributes:
        VALIDATION_DETAIL (ClassVar[str]): The detail of a ``422`` for a request that does not validate.
        UNKNOWN_TITLE (ClassVar[str]): The title of a status that has no standard phrase.
        logger (Logger): Logger instance.

    Notes:
        - **The text of an unexpected error is never sent to the client**: the answer is a bare ``500``.
        - One method handles the four kinds of error, because the type of an exception handler is
          ``Callable[[Request, Exception], ...]``.
    """

    VALIDATION_DETAIL: ClassVar[str] = "The request does not match the schema of this route."
    UNKNOWN_TITLE: ClassVar[str] = "Error"

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the handlers.

        Args:
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _phrase(self, status: int) -> str:
        """Give the standard phrase of a status.

        Args:
            status (int): The HTTP status.

        Returns:
            str: The phrase, or ``UNKNOWN_TITLE`` for a status that has none.
        """
        try:
            return HTTPStatus(status).phrase
        except ValueError:
            self.logger.warning("The status %d has no standard phrase.", status)
            return self.UNKNOWN_TITLE

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def problem_response(cls, status: int, title: str, detail: Optional[str], instance: str) -> JSONResponse:
        """Build the answer for one problem.

        Args:
            status (int): The HTTP status.
            title (str): The short title.
            detail (Optional[str]): The explanation, left out when ``None``.
            instance (str): The path of the request.

        Returns:
            JSONResponse: The problem document, with the media type ``application/problem+json``.
        """
        problem = Problem(title=title, status=status, detail=detail, instance=instance)
        return JSONResponse(problem.model_dump(exclude_none=True), status_code=status, media_type=Problem.MEDIA_TYPE)

    def install(self, app: FastAPI) -> None:
        """Register the handler for every kind of error.

        Args:
            app (FastAPI): The application to install it on.
        """
        for error_type in (HTTPException, RequestValidationError, SERestError, Exception):
            app.add_exception_handler(error_type, self.handle)
        self.logger.debug("Problem handlers are installed.")

    async def handle(self, request: Request, error: Exception) -> Response:
        """Answer one error as a problem document.

        Args:
            request (Request): The request that failed.
            error (Exception): The error.

        Returns:
            Response: The problem document.
        """
        path = request.url.path
        match error:
            case HTTPException() as http_error:
                self.logger.debug("Answering an HTTP exception with status %d.", http_error.status_code)
                detail = http_error.detail if isinstance(http_error.detail, str) else None
                return self.problem_response(http_error.status_code, self._phrase(http_error.status_code), detail, path)
            case RequestValidationError():
                self.logger.debug("Answering a request that does not validate.")
                status = HTTPStatus.UNPROCESSABLE_ENTITY
                return self.problem_response(status, status.phrase, self.VALIDATION_DETAIL, path)
            case SERestError() as rest_error:
                self.logger.debug("Answering a REST error with status %d.", rest_error.STATUS)
                return self.problem_response(rest_error.STATUS, rest_error.TITLE, str(rest_error) or None, path)
            case _:
                self.logger.error("An unexpected error was raised: %s.", type(error).__name__)
                status = HTTPStatus.INTERNAL_SERVER_ERROR
                return self.problem_response(status, status.phrase, None, path)
