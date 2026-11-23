from __future__ import annotations

# Standard library imports
from functools import partial
from logging import Logger, getLogger
from typing import ClassVar, Dict, List, Optional

# Third-party imports
from fastapi import APIRouter, FastAPI
from pydantic import JsonValue

# First-party imports
from swarm_rest.api.rest.idempotency_middleware import IdempotencyMiddleware
from swarm_rest.api.rest.problem_handlers import ProblemHandlers
from swarm_rest.models.config.rest_config import RestConfig
from swarm_rest.models.problems.problem import Problem
from swarm_rest.service.factories.idempotency_service_factory import IdempotencyServiceFactory


class RestAppBuilder:
    """Builds the FastAPI application of a service, with the REST conventions of Swarm.

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
        PROBLEM_SCHEMA (ClassVar[str]): The name of the problem schema in the components.
        PROBLEM_REF (ClassVar[str]): The reference to the problem schema.
        PROBLEM_DESCRIPTION (ClassVar[str]): The description of the default response.
        config (RestConfig): The settings of the layer.
        logger (Logger): Logger instance.

    Notes:
        - The document is deterministic: the problem schema comes from the model and the schemas are sorted, so the
          published documents do not change from one run to the next.
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
    PROBLEM_SCHEMA: ClassVar[str] = "Problem"
    PROBLEM_REF: ClassVar[str] = "#/components/schemas/Problem"
    PROBLEM_DESCRIPTION: ClassVar[str] = "The problem document of any error."

    def __init__(self, config: RestConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the builder.

        Args:
            config (RestConfig): The settings of the layer.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _default_response(self) -> Dict[str, JsonValue]:
        """Build the ``default`` response of an operation.

        Returns:
            Dict[str, JsonValue]: A response that refers to the problem schema, as ``application/problem+json``.
        """
        media: Dict[str, JsonValue] = {self.SCHEMA_KEY: {self.REF_KEY: self.PROBLEM_REF}}
        return {self.DESCRIPTION_KEY: self.PROBLEM_DESCRIPTION, self.CONTENT_KEY: {Problem.MEDIA_TYPE: media}}

    def _document(self, app: FastAPI) -> Dict[str, JsonValue]:
        """Build the OpenAPI document of an application, with the problem schema and responses.

        Args:
            app (FastAPI): The application.

        Returns:
            Dict[str, JsonValue]: The document, kept on the application after the first call.
        """
        document: Dict[str, JsonValue] = dict(FastAPI.openapi(app))
        components = document.setdefault(self.COMPONENTS_KEY, {})
        if isinstance(components, dict):
            schemas = components.setdefault(self.SCHEMAS_KEY, {})
            if isinstance(schemas, dict):
                schemas[self.PROBLEM_SCHEMA] = Problem.model_json_schema()
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
                            responses[self.DEFAULT_KEY] = self._default_response()
                    else:
                        self.logger.debug("Skipped a path item entry that is not an operation.")
        else:
            self.logger.debug("The document has no paths.")
        return document

    ############################
    # Publicly Exposed Methods #
    ############################

    def build(self, title: str, version: str, routers: List[APIRouter]) -> FastAPI:
        """Build an application.

        Args:
            title (str): The title of the API.
            version (str): The version of the API.
            routers (List[APIRouter]): The routers, each served under ``/v1``.

        Returns:
            FastAPI: The application, with its problem handlers, its idempotency middleware and its document.
        """
        app = FastAPI(
            title=title, version=version, openapi_url=self.OPENAPI_PATH, docs_url=self.DOCS_PATH, redoc_url=None
        )
        for router in routers:
            app.include_router(router, prefix=self.PREFIX)
        ProblemHandlers().install(app)
        app.add_middleware(IdempotencyMiddleware, service=IdempotencyServiceFactory(self.config).create())
        setattr(app, self.OPENAPI_ATTRIBUTE, partial(self._document, app))
        self.logger.info("Built the application %s %s with %d routers.", title, version, len(routers))
        return app
