from __future__ import annotations

# Standard library imports
import ast
from typing import ClassVar, List

# First-party imports
from tests.conventions.rules.convention_rule import ConventionRule
from tests.conventions.rules.service_tree import ServiceTree


class NoLoggerArgument(ConventionRule):
    """Code that creates an object never hands it a logger: the object falls back to its own module logger.

    Attributes:
        NAME (str): The short name of the rule.
        LOGGER (str): The name of the optional logger parameter, and of the attribute that holds a logger.
        GET_LOGGER (str): The function that returns a named logger.
        INIT (str): The constructor name, called through ``super()`` by a subclass.
        CLS (str): The first argument of a ``@classmethod``, which creates an object of its class.

    Notes:
        - A call creates an object when it names a class (a capitalised name or attribute) or ``cls``.
        - It hands a logger when it passes ``logger=``, or an argument that is ``logger``, ``<anything>.logger`` or a
          ``getLogger(...)`` call.
        - ``super().__init__(..., logger)`` creates nothing: a subclass still hands its logger to its base class
          (AGENT.md, Lifecycle and factories).
        - Only ``src/`` is checked: a test may pass a logger to test that parameter, or to capture the logs.
    """

    NAME: ClassVar[str] = "no_logger_argument"
    LOGGER: ClassVar[str] = "logger"
    GET_LOGGER: ClassVar[str] = "getLogger"
    INIT: ClassVar[str] = "__init__"
    CLS: ClassVar[str] = "cls"

    ############################
    # Internal Helpers Methods #
    ############################

    def _creates(self, call: ast.Call) -> bool:
        """Tell whether a call creates an object of a class.

        Args:
            call (ast.Call): The call to read.

        Returns:
            bool: True for ``Name(...)``, ``module.Name(...)`` and ``cls(...)``, False for ``__init__`` and the rest.
        """
        function = call.func
        if isinstance(function, ast.Attribute):
            return function.attr != self.INIT and function.attr[:1].isupper()
        if isinstance(function, ast.Name):
            return function.id == self.CLS or function.id[:1].isupper()
        return False

    def _is_logger(self, node: ast.expr) -> bool:
        """Tell whether an argument is a logger.

        Args:
            node (ast.expr): The argument.

        Returns:
            bool: True for ``logger``, ``<anything>.logger`` and ``getLogger(...)``.
        """
        if isinstance(node, ast.Name):
            return node.id == self.LOGGER
        if isinstance(node, ast.Attribute):
            return node.attr == self.LOGGER
        if isinstance(node, ast.Call):
            function = node.func
            name = function.attr if isinstance(function, ast.Attribute) else getattr(function, "id", "")
            return name == self.GET_LOGGER
        return False

    def _hands_a_logger(self, call: ast.Call) -> bool:
        """Tell whether a call passes a logger.

        Args:
            call (ast.Call): The call to read.

        Returns:
            bool: True when a keyword is ``logger`` or an argument is a logger.
        """
        if any(keyword.arg == self.LOGGER for keyword in call.keywords):
            return True
        return any(self._is_logger(argument) for argument in [*call.args, *(k.value for k in call.keywords)])

    ############################
    # Publicly Exposed Methods #
    ############################

    def violations(self, service: ServiceTree) -> List[str]:
        """List the calls of a service's ``src/`` that create an object and hand it a logger.

        Args:
            service (ServiceTree): The service to check.

        Returns:
            List[str]: One message per call.
        """
        messages: List[str] = []
        for path in service.python_files():
            if service.source_root not in path.parents:
                continue
            for node in ast.walk(self.parse(path)):
                if isinstance(node, ast.Call) and self._creates(node) and self._hands_a_logger(node):
                    messages.append(
                        self.violation(service, path, node.lineno, "A logger is handed to a new object: leave it out.")
                    )
        return messages
