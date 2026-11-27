from __future__ import annotations

# Standard library imports
from functools import partial
from logging import Logger, getLogger
from typing import ClassVar, Dict, List, Literal, Optional, Tuple, Type

# Third-party imports
from fastapi import APIRouter, FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import Span
from pydantic import BaseModel, JsonValue
from starlette.types import Scope


class RestAppBuilder:
    """Builds the FastAPI application of a service, served under ``/v1`` with a deterministic OpenAPI document.

    Attributes:
        PREFIX (ClassVar[str]): The version prefix of every route.
        OPENAPI_PATH (ClassVar[str]): The path of the OpenAPI document.
        DOCS_PATH (ClassVar[str]): The path of the interactive documentation.
        OPENAPI_ATTRIBUTE (ClassVar[str]): The attribute of the application that builds the document.
        COMPONENTS_KEY (ClassVar[str]): The ``components`` key of the document.
        SCHEMAS_KEY (ClassVar[str]): The ``schemas`` key of the components.
        PATHS_KEY (ClassVar[str]): The ``paths`` key of the document.
        RESPONSES_KEY (ClassVar[str]): The ``responses`` key of an operation.
        DEFAULT_KEY (ClassVar[str]): The ``default`` key of the responses.
        DESCRIPTION_KEY (ClassVar[str]): The ``description`` key of a response.
        CONTENT_KEY (ClassVar[str]): The ``content`` key of a response.
        SCHEMA_KEY (ClassVar[str]): The ``schema`` key of a media type.
        REF_KEY (ClassVar[str]): The ``$ref`` key of a reference.
        SCHEMA_REF_PREFIX (ClassVar[str]): The prefix of a reference to a schema of the components.
        PROBLEM_DESCRIPTION (ClassVar[str]): The description of the default response.
        URL_KEYS (ClassVar[Tuple[str, ...]]): The span attributes that hold a URL, whose query string is cut.
        QUERY_KEY (ClassVar[str]): The span attribute that holds a query string, emptied.
        QUERY_SEPARATOR (ClassVar[str]): The character that starts a query string.
        EMPTY (ClassVar[str]): The empty text.
        EXCLUDED_SPANS (ClassVar[List[str]]): The internal spans of the ASGI messages, left out of the hot paths.
        logger (Logger): Logger instance.

    Notes:
        - The document is deterministic: the problem schema comes from the model and the schemas are sorted, so the
          published documents do not change from one run to the next.
        - **The kernel knows no error document of its own**: the caller names the model of the problem document and
          its media type, and installs the problem handlers and the idempotency middleware of the api layer, so that
          this kernel lib imports nothing above it.
    """

    PREFIX: ClassVar[str] = "/v1"
    OPENAPI_PATH: ClassVar[str] = "/v1/openapi.json"
    DOCS_PATH: ClassVar[str] = "/v1/docs"
    OPENAPI_ATTRIBUTE: ClassVar[str] = "openapi"
    COMPONENTS_KEY: ClassVar[str] = "components"
    SCHEMAS_KEY: ClassVar[str] = "schemas"
    PATHS_KEY: ClassVar[str] = "paths"
    RESPONSES_KEY: ClassVar[str] = "responses"
    DEFAULT_KEY: ClassVar[str] = "default"
    DESCRIPTION_KEY: ClassVar[str] = "description"
    CONTENT_KEY: ClassVar[str] = "content"
    SCHEMA_KEY: ClassVar[str] = "schema"
    REF_KEY: ClassVar[str] = "$ref"
    SCHEMA_REF_PREFIX: ClassVar[str] = "#/components/schemas/"
    PROBLEM_DESCRIPTION: ClassVar[str] = "The problem document of any error."
    URL_KEYS: ClassVar[Tuple[str, ...]] = ("url.full", "http.url", "http.target")
    QUERY_KEY: ClassVar[str] = "url.query"
    QUERY_SEPARATOR: ClassVar[str] = "?"
    EMPTY: ClassVar[str] = ""
    EXCLUDED_SPANS: ClassVar[List[Literal["receive", "send"]]] = ["receive", "send"]

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the builder.

        Args:
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _cut_query(self, span: Span, scope: Scope) -> None:
        """Remove the query string from the attributes of a server span, so that a token in it never reaches a span.

        Args:
            span (Span): The server span of the request.
            scope (Scope): The ASGI scope of the request, ignored.
        """
        if not isinstance(span, ReadableSpan):
            self.logger.debug("The span is not an SDK span, so its attributes are left as they are.")
            return
        attributes = span.attributes or {}
        for key in self.URL_KEYS:
            value = attributes.get(key)
            if isinstance(value, str) and self.QUERY_SEPARATOR in value:
                span.set_attribute(key, value.split(self.QUERY_SEPARATOR, 1)[0])
                self.logger.debug("Cut the query of %s.", key)
            else:
                self.logger.debug("No query in %s.", key)
        if self.QUERY_KEY in attributes:
            span.set_attribute(self.QUERY_KEY, self.EMPTY)
            self.logger.debug("Emptied the query attribute.")

    def _default_response(self, problem: Type[BaseModel], media_type: str) -> Dict[str, JsonValue]:
        """Build the ``default`` response of an operation.

        Args:
            problem (Type[BaseModel]): The model of the problem document.
            media_type (str): The media type of the problem document.

        Returns:
            Dict[str, JsonValue]: A response that refers to the problem schema, under its media type.
        """
        media: Dict[str, JsonValue] = {self.SCHEMA_KEY: {self.REF_KEY: self.SCHEMA_REF_PREFIX + problem.__name__}}
        return {self.DESCRIPTION_KEY: self.PROBLEM_DESCRIPTION, self.CONTENT_KEY: {media_type: media}}

    def _document(self, app: FastAPI, problem: Type[BaseModel], media_type: str) -> Dict[str, JsonValue]:
        """Build the OpenAPI document of an application, with the problem schema and responses.

        Args:
            app (FastAPI): The application.
            problem (Type[BaseModel]): The model of the problem document.
            media_type (str): The media type of the problem document.

        Returns:
            Dict[str, JsonValue]: The document, kept on the application after the first call.
        """
        document: Dict[str, JsonValue] = dict(FastAPI.openapi(app))
        components = document.setdefault(self.COMPONENTS_KEY, {})
        if isinstance(components, dict):
            schemas = components.setdefault(self.SCHEMAS_KEY, {})
            if isinstance(schemas, dict):
                schemas[problem.__name__] = problem.model_json_schema()
                components[self.SCHEMAS_KEY] = dict(sorted(schemas.items()))
                self.logger.debug("Added the problem schema to the document.")
            else:
                self.logger.debug("The schemas of the document are not a mapping.")
        else:
            self.logger.debug("The components of the document are not a mapping.")
        paths = document.get(self.PATHS_KEY)
        if isinstance(paths, dict):
            for item in paths.values():
                operations = item.values() if isinstance(item, dict) else []
                for operation in operations:
                    if isinstance(operation, dict) and isinstance(operation.get(self.RESPONSES_KEY), dict):
                        responses = operation[self.RESPONSES_KEY]
                        if isinstance(responses, dict):
                            responses[self.DEFAULT_KEY] = self._default_response(problem, media_type)
                    else:
                        self.logger.debug("Skipped a path item entry that is not an operation.")
        else:
            self.logger.debug("The document has no paths.")
        return document

    ############################
    # Publicly Exposed Methods #
    ############################

    def build(
        self, title: str, version: str, routers: List[APIRouter], problem: Type[BaseModel], problem_media_type: str
    ) -> FastAPI:
        """Build an application.

        Args:
            title (str): The title of the API.
            version (str): The version of the API.
            routers (List[APIRouter]): The routers, each served under ``/v1``.
            problem (Type[BaseModel]): The model of the problem document every error answers with.
            problem_media_type (str): The media type of the problem document.

        Returns:
            FastAPI: The application and its document, with a ``default`` problem response on every operation.
        """
        app = FastAPI(
            title=title, version=version, openapi_url=self.OPENAPI_PATH, docs_url=self.DOCS_PATH, redoc_url=None
        )
        for router in routers:
            app.include_router(router, prefix=self.PREFIX)
        FastAPIInstrumentor.instrument_app(app, server_request_hook=self._cut_query, exclude_spans=self.EXCLUDED_SPANS)
        setattr(app, self.OPENAPI_ATTRIBUTE, partial(self._document, app, problem, problem_media_type))
        self.logger.info("Built the application %s %s with %d routers.", title, version, len(routers))
        return app
