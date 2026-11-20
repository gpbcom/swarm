from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_THRESHOLD = 0.05
USAGE = "Usage: bench_gate.py --criterion-dir <dir> [--threshold <fraction>]."


def parse_threshold(text: str) -> float:
    """Parse the threshold, which must be a finite number that is not negative.

    Args:
        text (str): The value given after ``--threshold``.

    Returns:
        float: The threshold as a fraction.

    Raises:
        ValueError: If the text is not a finite number, or is negative.
    """
    try:
        value = float(text)
    except ValueError as error:
        raise ValueError(f"Invalid threshold: {text!r}. It must be a number.") from error
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"Invalid threshold: {text!r}. It must not be negative.")
    return value


def parse_arguments(argv: List[str]) -> Dict[str, str]:
    """Read the command line into its two options.

    Args:
        argv (List[str]): The arguments, without the program name.

    Returns:
        Dict[str, str]: The values of ``criterion-dir`` and ``threshold`` that were given.

    Raises:
        ValueError: If an argument is unknown, an option has no value, or ``--criterion-dir`` is missing.
    """
    options: Dict[str, str] = {}
    index = 0
    while index < len(argv):
        name = argv[index]
        if name not in ("--criterion-dir", "--threshold"):
            raise ValueError(f"Unknown argument: {name!r}. {USAGE}")
        if index + 1 >= len(argv):
            raise ValueError(f"Missing value for {name}. {USAGE}")
        options[name[2:]] = argv[index + 1]
        index += 2
    if "criterion-dir" not in options:
        raise ValueError(f"Missing --criterion-dir. {USAGE}")
    return options


def read_change(path: Path) -> float:
    """Read ``mean.point_estimate`` from one change file.

    Args:
        path (Path): The ``change/estimates.json`` file.

    Returns:
        float: The relative change of the mean.

    Raises:
        ValueError: If the file is not valid JSON or has no numeric ``mean.point_estimate``.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError(f"Cannot read {path.as_posix()}. It is not valid JSON.") from error
    mean = data.get("mean") if isinstance(data, dict) else None
    value = mean.get("point_estimate") if isinstance(mean, dict) else None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"Invalid {path.as_posix()}. It has no numeric mean.point_estimate.")
    return float(value)


def collect_changes(directory: Path) -> Dict[str, float]:
    """Collect the change of every benchmark under a directory.

    Args:
        directory (Path): The criterion output folder.

    Returns:
        Dict[str, float]: The change of each benchmark, by id.
    """
    changes: Dict[str, float] = {}
    for path in directory.rglob("change/estimates.json"):
        bench_id = path.parent.parent.relative_to(directory).as_posix()
        changes[bench_id] = read_change(path)
    return changes


def main(argv: Optional[List[str]] = None) -> int:
    """Run the gate.

    Args:
        argv (Optional[List[str]]): The arguments, ``sys.argv[1:]`` when omitted.

    Returns:
        int: 0 when the gate passes, 1 on a regression, 2 on a usage or data error.
    """
    try:
        options = parse_arguments(list(sys.argv[1:] if argv is None else argv))
        threshold = parse_threshold(options["threshold"]) if "threshold" in options else DEFAULT_THRESHOLD
        directory = Path(options["criterion-dir"])
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory.as_posix()}.")
        changes = collect_changes(directory)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    if not changes:
        print("No benchmark was compared with a baseline: the gate passes.")
        return 0
    regressions = 0
    for bench_id in sorted(changes):
        change = changes[bench_id]
        if change > threshold:
            regressions += 1
            print(f"{bench_id}: {change * 100:+.2f} % regression")
        else:
            print(f"{bench_id}: {change * 100:+.2f} % ok")
    if regressions:
        print(f"Benchmark gate failed: {regressions} regression(s) of more than {threshold * 100:.2f} %.")
        return 1
    print(f"Benchmark gate passed: {len(changes)} benchmark(s) compared.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
