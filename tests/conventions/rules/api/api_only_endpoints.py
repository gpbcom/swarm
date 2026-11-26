from __future__ import annotations

# Standard library imports
import ast
import os
from pathlib import Path
from typing import ClassVar, List, Set, Tuple

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class ApiOnlyEndpoints(ConventionRule):
    """The ``swarm_api`` package holds only endpoints, ``Depends`` providers, middlewares and exception handlers.

    Attributes:
        NAME (str): The short name of the rule.
        BACKEND (str): The folder, under the tree root, searched for ``swarm_api`` packages.
        PACKAGE (str): The name of the API package.
        SKIPPED (Tuple[str, ...]): The folders never entered.
        FORBIDDEN_BASES (Set[str]): The base classes that make a class a runnable or a runnable factory.
        FACTORY_SUFFIX (str): The class name ending that marks a factory.
        ROUTER_BASES (Set[str]): The base classes of a router class.
        MIDDLEWARE_BASES (Set[str]): The base classes of a middleware class.
        ROUTE_DECORATORS (Set[str]): The decorator attributes that register an endpoint, a middleware or a handler.
        ROUTER (str): The router class, whose assignment is allowed.
        DEPENDS (str): The ``Depends`` marker, whose argument is a provider.
        ADD_HANDLER (str): The method that registers an exception handler.
        HANDLER_SUFFIX (str): The function name ending that marks an exception handler.
        CALL (str): The method that makes an instance a callable provider.
        ASGI_PARAMETERS (Tuple[str, ...]): The parameters of the ``__call__`` of a pure ASGI middleware.
        CONNECTIONS (Set[str]): The annotations of the connection a ``Depends`` provider class is called with.

    Notes:
        The tree root is the repository root, and every ``swarm_api`` folder under ``backend/`` is checked, in every
        file. Only top-level classes and functions are read, and the signals are these.
        - **Forbidden**: a class that subclasses ``Runnable``, ``AsyncRunnable``, or any base named ``*Factory``.
        - **A class is allowed** when it subclasses ``APIRouter`` or ``BaseHTTPMiddleware``; when it is a pure ASGI
          middleware, whose ``__call__`` takes ``scope``, ``receive`` and ``send``; when it registers exception
          handlers, with an ``add_exception_handler(...)`` call in its body; when its name is the argument of a
          ``Depends(...)`` call of its module; or when it is a ``Depends`` provider in a module of its own, whose
          ``__call__`` takes a ``Request`` or a ``WebSocket``.
        - **A function is allowed** when a decorator is a router method (``@router.get``, ``post``, ``put``,
          ``patch``, ``delete``, ``head``, ``options``, ``websocket``, ``api_route``, ``route``), ``@app.middleware``
          or ``@app.exception_handler``; when its name ends with ``_handler``; when its name is registered by an
          ``add_exception_handler(...)`` call of its module; or when its name is the argument of ``Depends(...)``.
        - Anything else at the top level is reported: it exposes no endpoint, so it belongs to the service layer.
    """

    NAME: ClassVar[str] = "api_only_endpoints"
    BACKEND: ClassVar[str] = "backend"
    PACKAGE: ClassVar[str] = "swarm_api"
    SKIPPED: ClassVar[Tuple[str, ...]] = ("__pycache__", "node_modules")
    FORBIDDEN_BASES: ClassVar[Set[str]] = {"Runnable", "AsyncRunnable"}
    FACTORY_SUFFIX: ClassVar[str] = "Factory"
    ROUTER_BASES: ClassVar[Set[str]] = {"APIRouter"}
    MIDDLEWARE_BASES: ClassVar[Set[str]] = {"BaseHTTPMiddleware"}
    ROUTE_DECORATORS: ClassVar[Set[str]] = {
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
        "websocket",
        "api_route",
        "route",
        "middleware",
        "exception_handler",
    }
    ROUTER: ClassVar[str] = "APIRouter"
    DEPENDS: ClassVar[str] = "Depends"
    ADD_HANDLER: ClassVar[str] = "add_exception_handler"
    HANDLER_SUFFIX: ClassVar[str] = "_handler"
    CALL: ClassVar[str] = "__call__"
    ASGI_PARAMETERS: ClassVar[Tuple[str, ...]] = ("self", "scope", "receive", "send")
    CONNECTIONS: ClassVar[Set[str]] = {"Request", "WebSocket"}

    ############################
    # Internal Helpers Methods #
    ############################

    def _api_files(self, service: ServiceTree) -> List[Path]:
        """List the Python files of every ``swarm_api`` package under ``backend/``.

        Args:
            service (ServiceTree): The tree whose root is the repository root.

        Returns:
            List[Path]: The sorted files, without ``__pycache__``.
        """
        files: List[Path] = []
        backend = service.root / self.BACKEND
        for folder, names, filenames in os.walk(backend):
            names[:] = [name for name in names if name not in self.SKIPPED]
            if self.PACKAGE not in Path(folder).relative_to(backend).parts:
                continue
            files.extend(Path(folder) / name for name in filenames if name.endswith(".py"))
        return sorted(files)

    def _name_of(self, node: ast.expr) -> str:
        """Return the last name of an expression.

        Args:
            node (ast.expr): A base class, a callee or a decorator.

        Returns:
            str: The identifier, the attribute, the one of a call or of a subscript, or an empty string.
        """
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        if isinstance(node, ast.Call):
            return self._name_of(node.func)
        if isinstance(node, ast.Subscript):
            return self._name_of(node.value)
        return ""

    def _provided(self, tree: ast.Module) -> Set[str]:
        """Collect the names a module hands to ``Depends`` or registers as an exception handler.

        Args:
            tree (ast.Module): The module.

        Returns:
            Set[str]: The names used as an argument of ``Depends(...)`` or ``add_exception_handler(...)``.
        """
        names: Set[str] = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            callee = self._name_of(node.func)
            if callee == self.DEPENDS:
                names.update(self._name_of(argument) for argument in node.args[:1])
            elif callee == self.ADD_HANDLER:
                names.update(self._name_of(argument) for argument in node.args[1:2])
        return names

    def _is_asgi_middleware(self, node: ast.ClassDef) -> bool:
        """Tell whether a class is a pure ASGI middleware.

        Args:
            node (ast.ClassDef): The class.

        Returns:
            bool: True when its ``__call__`` takes exactly ``scope``, ``receive`` and ``send``.
        """
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == self.CALL:
                return tuple(argument.arg for argument in item.args.args) == self.ASGI_PARAMETERS
        return False

    def _is_provider(self, node: ast.ClassDef) -> bool:
        """Tell whether a class is a ``Depends`` provider, called with the connection.

        Args:
            node (ast.ClassDef): The class.

        Returns:
            bool: True when its ``__call__`` takes a parameter annotated ``Request`` or ``WebSocket``.
        """
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == self.CALL:
                annotations = [argument.annotation for argument in item.args.args if argument.annotation is not None]
                return any(self._name_of(annotation) in self.CONNECTIONS for annotation in annotations)
        return False

    def _registers_handlers(self, node: ast.ClassDef) -> bool:
        """Tell whether a class registers exception handlers.

        Args:
            node (ast.ClassDef): The class.

        Returns:
            bool: True when its body calls ``add_exception_handler``.
        """
        return any(
            isinstance(child, ast.Call) and self._name_of(child.func) == self.ADD_HANDLER for child in ast.walk(node)
        )

    def _class_problem(self, node: ast.ClassDef, provided: Set[str]) -> str:
        """Tell what is wrong with a top-level class.

        Args:
            node (ast.ClassDef): The class.
            provided (Set[str]): The names the module hands to ``Depends``.

        Returns:
            str: The message, or an empty string when the class is allowed.
        """
        bases = {self._name_of(base) for base in node.bases}
        if bases & self.FORBIDDEN_BASES or any(base.endswith(self.FACTORY_SUFFIX) for base in bases):
            return f"Class {node.name!r} is a runnable or a factory: move it to the service layer."
        if bases & (self.ROUTER_BASES | self.MIDDLEWARE_BASES) or node.name in provided:
            return ""
        if self._is_asgi_middleware(node) or self._registers_handlers(node) or self._is_provider(node):
            return ""
        return f"Class {node.name!r} is no router, provider or middleware: move it to the service layer."

    def _function_problem(self, node: ast.FunctionDef | ast.AsyncFunctionDef, provided: Set[str]) -> str:
        """Tell what is wrong with a top-level function.

        Args:
            node (ast.FunctionDef | ast.AsyncFunctionDef): The function.
            provided (Set[str]): The names the module hands to ``Depends`` or registers as handlers.

        Returns:
            str: The message, or an empty string when the function is allowed.
        """
        decorated = any(self._name_of(decorator) in self.ROUTE_DECORATORS for decorator in node.decorator_list)
        if decorated or node.name.endswith(self.HANDLER_SUFFIX) or node.name in provided:
            return ""
        return f"Function {node.name!r} exposes no endpoint: move it to the service layer."

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, service: ServiceTree) -> List[str]:
        """List what a ``swarm_api`` package holds besides endpoints.

        Args:
            service (ServiceTree): The tree whose root is the repository root.

        Returns:
            List[str]: One message per class or function, empty when there is no ``backend/``.
        """
        messages: List[str] = []
        for path in self._api_files(service):
            tree = self.parse(path)
            provided = self._provided(tree)
            for node in tree.body:
                problem = ""
                if isinstance(node, ast.ClassDef):
                    problem = self._class_problem(node, provided)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    problem = self._function_problem(node, provided)
                if problem:
                    messages.append(self.violation(service, path, node.lineno, problem))
        return messages
