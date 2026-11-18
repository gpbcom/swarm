# AGENT.md

How code is written in Swarm. See `README.md` for what it does and how to use it.

When you edit a file, follow these rules even where a neighbouring file does not.

## Commands

```bash
uv sync
uv run ruff check src tests
uv run ruff format <the files you edited>
uv run mypy src
uv run pytest tests/<layer>/<package> -n 2
```

- `.github/workflows/ci.yml` runs `ruff check`, `ruff format --check`, `mypy src` and `pytest` on every push and pull
  request. All of them must pass.
- Run tests one file or one folder at a time.
- Format only the files you edited, never a whole folder.

## Layout

| Path | Holds |
| --- | --- |
| `src/api/` | The entry points: HTTP routes and the command line. They call `service` and hold no business rules |
| `src/service/` | The business rules, one package per concern |
| `src/storage/` | Reading and writing data, and nothing else: one repository per PostgreSQL entity, the other stores |
| `src/clients/` | Calls to other services and to external systems, one class per remote system |
| `src/models/` | Pydantic models, enums and their exceptions. They only load and validate, and never log |
| `conf/app.yaml` | The configuration, with every default written out |
| `conf/logger.yaml` | The logging: coloured console and coloured rotating file, written to `logs/` |
| `conf/catalogs/` | Data that would otherwise be hard-coded |
| `tests/` | Mirrors `src/` folder by folder |
| `docs/` | The `specs/`, `functional/` and `technical/` documentation |

Each layer only calls the one below it: `api` imports `service`, and `service` imports `storage` and `clients`. All of
them import `models`, and `models` imports none of them. `api` never imports `storage` or `clients`, `storage` and
`clients` never import each other, and no layer imports one above it. Every endpoint lives in `api`, every business rule
in `service`.

## Mono-repo

Swarm is meant to become a mono-repo of backend and front-end micro-services, each with its own Docker image. The repository has
not moved to this layout yet: until a service has moved, the root `src/` layout and the commands above still apply. No
test enforces this section yet.

| Path | Holds |
| --- | --- |
| `pyproject.toml` | The uv workspace root, with one `uv.lock` for the whole repository |
| `services/<service>/` | One backend service: its `Dockerfile`, `pyproject.toml`, `conf/`, `src/<service>/`, `tests/` |
| `frontends/<frontend>/` | One front end: its `Dockerfile`, `src/`, and its Playwright tests in `e2e/` |
| `packages/` | Shared code: `python/` (lifecycle base classes, logging, models), `rust/` (PyO3 crates of the hot path), `ts/` (front-end packages) |
| `tests/conventions/` | The [rules a test enforces](#rules-a-test-enforces), run against every service |
| `compose.e2e.yaml` | Starts the real images for Playwright |
| `.github/workflows/` | The CI/CD pipeline |

The Python rules in this file apply to `services/` and `packages/python/`. The front ends use React and TypeScript
with a Tauri desktop shell, images go to GHCR, and Argo CD deploys them; see `docs/specs/technical/`.

**Services**

- The layers in [Layout](#layout) sit inside each service, under its name:
  `services/<service>/src/<service>/{api,service,storage,models}/`. Elsewhere in this file, read `src/` as
  `services/<service>/src/<service>/`, and `from service.customers...` as `from <service>.service.customers...`.
- NEVER add a top-level `api`, `service`, `storage` or `models` package to a service. Services share one uv environment,
  so they would overwrite each other.
- A service never imports another service. Code they share goes in `packages/`, which holds no business rules.
- Adding a service must not need a change to `tests/conventions/`, so that its rules cover new code automatically.

**Docker images**

- Each service and front end has exactly one image, built by a multi-stage `Dockerfile` in its own folder.
- The build context is the repository root, because the shared `uv.lock` is there.

**Front-end tests**

- Front-end tests use Playwright, and live in `frontends/<frontend>/e2e/`.
- They run against the real images started by `compose.e2e.yaml`, never a development server, so that they test what
  ships.

**CI/CD**

Each step must pass before the next one starts:

1. Detect what changed, and run jobs only for those services and front ends. A change in `packages/` or `uv.lock` runs
   all of them.
2. Run `ruff check`, `ruff format --check`, `mypy` and `pytest` for each changed service.
3. Build each changed image.
4. Run Playwright against those images, and upload the HTML report if a test fails.
5. Publish the images tagged with the commit SHA, from `develop` or `master` only.

## Rules a test enforces

`tests/conventions/` fails on any of these, in `src/` and `tests/` unless stated:

- More than one top-level class in a file, whatever the kind of class.
- More than five Python files in a folder, not counting `__init__.py` and `conftest.py`.
- A nested function.
- `@staticmethod`. Use an instance method or a `@classmethod`.
- `Any`. See [Typing](#typing).
- An attribute starting with an underscore: `self.process`, never `self._process`. Methods may start with one. The only
  exception is a name a third-party protocol owns, listed in `tests/conventions/helpers.py`.
- An import that [Layout](#layout) does not allow.
- A Pydantic model outside `src/models/`.
- A class outside `src/models/` with `start` or `stop`, or with `run` but no lifecycle base class.
- A node without `__call__`, or with `run`.

## File shape

**NEVER more than one class in one file, whatever the kind of class.** This has no exceptions: it covers Pydantic
models, `Enum`, `TypedDict`, exceptions, helpers and test classes, in `src/` and in `tests/`. Each class has its own
file, named after the class: `CustomerService` in `customer_service.py`, `CustomerStatus` in `customer_status.py`.

**Classes that share a method name share a base class.** `TaskNode` has `__call__`, and `YamlCatalog` has `load`. If two
methods only happen to share a name and mean different things, rename one instead.

**NEVER more than five Python files in one folder.** When a folder would go past five, create sub-folders and dispatch
its files by entity type: `storage/customers/repositories/` for the repositories, `models/customers/enums/` for the
enums. This applies to `src/` and `tests/`, including `exceptions/` folders. `__init__.py` and `conftest.py` do not
count towards the five.

An `enums/` or `exceptions/` package's `__init__.py` re-exports everything under it, so callers keep importing from the
package. Other code is imported by its full path: `from service.customers.customer_service import CustomerService`.

Nothing else sits at module level, so there are no module constants, helper functions or module-level loggers. The
exceptions are a `main()` for a console script and `__all__`. Constants become `ClassVar` attributes in `UPPER_CASE`,
above the constructor.

Inside a class, the order is: constants and fields, `__init__`, validators, then these two banners. Leave out a banner
whose section would be empty.

```python
    ############################
    # Internal Helpers Methods #
    ############################

    def _active_customers(self, customers: List[Customer]) -> List[Customer]: ...

    ############################
    # Publicly Exposed Methods #
    ############################

    def create(self, customer: Customer) -> Customer: ...
```

`@property` and `@classmethod` constructors such as `load` are public, so they go under the second banner.

A task graph node subclasses `TaskNode`, and its work is in `async def __call__(self, state)`, never a `run` method. The
graph adds the instance itself: `graph.add_node(NodeName.CHECK.value, self.check)`. `__call__` goes under the second
banner.

## Lifecycle and factories

Every runnable class except the nodes subclasses `Runnable` or `AsyncRunnable`, and has exactly these methods:

| Method | Does |
| --- | --- |
| `initialize()` | Acquires what the work needs. A service is already serving when it returns |
| `run()` | Does the work. A service blocks here until it is closed, and a job returns when it is done |
| `close()` | Releases everything, and must be safe after a failed or partial `initialize` |

- `execute()` on the base class calls all three, and closes whatever happens. Use it unless something runs alongside.
- They take no arguments. Inputs go to the constructor, and results are read from attributes afterwards, such as
  `Command.exit_code`.
- Runnables are created by an abstract factory in their layer's `factories/` package, with concrete ones in its
  sub-folders: `ServiceFactory` in `service/factories/`, and `CommandFactory` in `api/factories/`. Do not call a
  runnable's constructor in `src/` outside a factory.

## Imports

`from __future__ import annotations` comes first in every non-empty file, after the module docstring if there is one.
Then come up to three groups, each under its own comment:

```python
from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import List, Optional

# Third-party imports
import yaml

# First-party imports
from models.customers.exceptions import SECustomerCatalogUnreadable
```

- Imports are absolute, at the top of the file, never inside a function.
- Import exceptions from their package (`models.customers.exceptions`), not from the file that defines them.
- Test files, `__init__.py` files and most exception files have no group comments.

## Typing

- Annotate every signature, including `-> None`.
- Use `Optional`, `List`, `Dict`, `Tuple`, `Set` and `Union` from `typing`, not `X | None` or `list[str]`.
- Use `JsonValue` for raw input in validators.
- Use `object` only for something truly opaque, or a parameter a third-party signature forces on you.

## Naming

- Exceptions start with `SE` (see [Exceptions](#exceptions)). Other classes write acronyms in title case: `HttpClient`,
  `SqlConfig`.
- Durations and sizes carry their unit: `start_timeout_s`, `poll_interval_ms`, `page_width_px`.
- Bounds on a field are `ClassVar`s named `<FIELD>_MIN` and `<FIELD>_MAX`.
- A field ending in `_key` names a secret store entry and never holds a secret.
- Use `error` for a caught exception and `value` for a validator's input.

## Docstrings and comments

Every class and method in `src/` has a Google-style docstring, private ones included. Types go in parentheses.

```python
class CustomerService:
    """Everything the application does with a customer.

    Attributes:
        repository (CustomerRepository): Where customers are stored.
        logger (Logger): Logger instance.

    Notes:
        Callers go through this class rather than the repository, so that each rule about a customer lives in one
        place.
    """
```

- A class summary says what the class is. A method summary starts with a verb: `Create one customer.`
- List every attribute under `Attributes:`, constants included.
- Use `Args:`, `Returns:` and `Raises:` wherever they apply.
- Put the reasoning in `Notes:`, after the other sections. Use bullets for several points, and bold the ones that would
  cause harm if missed.
- Write ``` ``double_backticks`` ``` around code.
- Avoid inline comments: `src/` has almost none. A reason belongs in `Notes:`.

## Exceptions

Each exception has its own file, and the package's `exceptions/__init__.py` re-exports it through a sorted `__all__`.

| Kind | Name | Docstring |
| --- | --- | --- |
| Layer base | `SE<Domain>Error` | `Base class for every error raised while storing a customer.` |
| Layer | `SE<Domain><Problem>Error` | `Raised when a customer cannot be found.` |
| Model base | `SEInvalid<Model>Exception` | `Exception raised when an invalid DatabaseConfig is provided.` |
| Model field | `SE<Model>Invalid<Field>` | `Exception raised when an invalid ``port`` is provided.` |
| Model, other | `SE<Model><Problem>` | `SECustomerCatalogUnreadable`, `SEDatabaseConfigNoHost` |

- Each file is the class name in snake case: `se_database_config_invalid_port.py`.
- Keep the cause: `raise SECustomerCatalogUnreadable(...) from error`.
- Outside `models`, log at `ERROR` just before raising.
- Catch specific types. A broad `except Exception` exists only where any failure must be reported rather than end the
  process.

## Messages

**Use the `exception-and-log-messages` skill whenever you write a `raise` or a log call.** A message with two or more
sentences has one sentence per source line, with no comma between them, and the first line ends with `# noqa: E501`:

```python
raise SEDatabaseConfigInvalidPort(
    f"Invalid port: {value}. "  # noqa: E501
    f"Must be in [{cls.PORT_MIN}, {cls.PORT_MAX}]."
)
```

- A field error reads `Invalid <field>: {value!r}.` then `Must be ...`
- Write full sentences that end with a full stop, and no semicolons.

## Logging

Classes outside `models` that log take the logger as their last constructor argument:

```python
def __init__(self, config: DatabaseConfig, logger: Optional[Logger] = None) -> None:
    self.config = config
    self.logger = logger if logger else getLogger(__name__)
```

- Use lazy arguments, never an f-string: `self.logger.info("Created customer %s in %d ms.", name, duration_ms)`.
- Use the levels this way:

  | Level | For |
  | --- | --- |
  | `DEBUG` | Decisions and small steps |
  | `INFO` | What was actually done |
  | `WARNING` | A degraded result the code recovers from |
  | `ERROR` | A failure, just before raising |

- **Every method logs, at each level that applies to it, except in `tests/` and `src/models/`.** Not every method has a
  failure to report, so do not invent one, but every failure path has its `WARNING` or `ERROR`.
- These stay silent, because they have nothing to report: one-line getters and predicates, data holders, and code that
  runs for every event. Log the outcome one level up instead.
- The log file holds colour codes. Read it with `tail -f` or `less -R`.
- `DEBUG` lines are written by default, because the root level in `conf/logger.yaml` is `DEBUG`. Keep them short.
- **Never log a secret or a typed value.** If an error might quote one, log `type(error).__name__`.
- `models` never logs. It raises.
- Only `api/cli/` uses `print`, because that output is for the person at the terminal.

## Pydantic models

Every field has a `Field(description=...)` and a `@field_validator` that raises its own exception. Fields with the same
rule may share a validator.

```python
class DatabaseConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_default=True)

    port: int = Field(default=5432, description="The port the database listens on.")

    @field_validator("port", mode="before")
    def validate_port(cls, value: JsonValue) -> JsonValue:
        """Validate ``port``. ..."""
        if value is None:
            return cls.model_fields["port"].get_default(call_default_factory=True)
        if isinstance(value, bool) or not isinstance(value, int):
            raise SEDatabaseConfigInvalidPort(...)
        return value
```

- Validators are named `validate_<field>` and use `mode="before"`. Do not add `@classmethod`: ruff is configured for
  `field_validator`.
- `None` becomes the default, if the field has one.
- Reject `bool` where a number is expected, because Python treats it as an `int`.
- Strip strings, and reject empty ones.
- Check rules across fields in `@model_validator(mode="after")`.
- Use `extra="forbid"`. Configuration sections add `validate_default=True`. Models that must not change use
  `frozen=True`.

## Data and enums

- Do not hard-code data in Python. It goes in `conf/catalogs/*.yaml`, loaded by a model that subclasses `YamlCatalog`,
  which provides `load(path)` and raises the model's `UNREADABLE` exception.
- A string that selects behaviour is a `StrEnum` with `@unique`, in its own file named after it, with its members
  listed under `Attributes:`.
- Use `match`/`case` to branch on an enum.
- Open files with `encoding="utf-8"`.
- Secrets live in a secret store. They never appear in configuration or logs.

## Tests

- Name files `test_<subject>.py`, in the folder that mirrors the source. There are no `__init__.py` files.
- Put each file's tests in one `Test<Subject>` class. A helper class, such as a stand-in server, gets its own file.
- When a source file needs several test classes, give it a folder of its name:
  `tests/service/customers/customer_service/`.
- In that folder, `helpers.py` holds the functions and constants several classes share, and `conftest.py` the fixtures.
  Import them by their full path: `from tests.service.customers.customer_service.helpers import a_customer`.
- Scripts that tests run as child processes load their helpers by path, so keep them in place.
- Name tests as sentences: `test_a_customer_without_a_name_is_refused`.
- Tests need no docstrings, banners or import comments. Add a docstring only if the purpose is not obvious.
- Assert the specific exception: `pytest.raises(SEDatabaseConfigInvalidPort)`.
- Use `pytest.mark.parametrize` for cases of the same behaviour.
- Async tests need no marker, because `asyncio_mode` is `auto`.
- Prefer real things to mocks. `unittest.mock` is not used: tests use real services, such as a local test server.

Every model gets this set of tests:

```python
class TestDatabaseConfig:
    def test_defaults(self) -> None: ...
    def test_full_valid_construction(self) -> None: ...
    def test_none_becomes_the_default(self, name: str) -> None: ...
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None: ...
    def test_rejects_unknown_keys(self) -> None: ...
    def test_round_trip(self) -> None: ...
```

## Formatting and prose

- Ruff handles formatting, with lines up to 120 characters and double quotes.
- Write docstrings, messages and documentation in plain British English: `Initialise`, `normalised`, `colour`,
  `catalogue`. Identifiers use `catalog`.
- Do not use em dashes.