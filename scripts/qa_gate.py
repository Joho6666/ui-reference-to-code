#!/usr/bin/env python3
"""Validate a declared visual QA report; does not inspect images or calculate scores."""
import argparse
import json
import math
from pathlib import Path
import sys

DIMENSIONS = ("layout", "typography", "color", "component", "responsive", "interaction")
EXIT_CODES = {"verified": 0, "needs-repair": 1, "unverified": 2, "invalid-report": 3}


class ReportError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ReportError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def object_field(obj, key):
    value = obj.get(key)
    require(isinstance(value, dict), key + " must be an object")
    return value


def evaluate(report):
    """Return status and reasons without averaging away defects or missing evidence."""
    require(isinstance(report, dict), "report must be an object")
    require(type(report.get("schema_version")) is int and report["schema_version"] == 1,
            "schema_version must be 1")
    require(report.get("mode") in ("B", "C", "D"), "QA gate is for implementation modes B/C/D")
    require(nonempty(report.get("scope")), "scope must describe the modified region")
    require(type(report.get("iteration")) is int and report["iteration"] >= 1,
            "iteration must be a positive integer")
    modifiers = report.get("modifiers")
    require(isinstance(modifiers, list) and all(x in ("E", "F") for x in modifiers)
            and len(set(modifiers)) == len(modifiers), "modifiers must be unique E/F entries")
    missing, repair = [], []
    for key in ("code_checks", "preservation"):
        require(report.get(key) in ("passed", "failed", "unverified"), key + " has invalid status")
        if report[key] == "failed":
            repair.append(key + " failed")
        elif report[key] == "unverified":
            missing.append(key + " needs evidence")

    browser = object_field(report, "browser")
    for device in ("desktop", "mobile"):
        sample = object_field(browser, device)
        require(type(sample.get("observed")) is bool, device + ".observed must be boolean")
        require(isinstance(sample.get("screenshot"), str), device + ".screenshot must be a string")
        viewport = sample.get("viewport")
        require(isinstance(viewport, list) and len(viewport) == 2
                and all(type(n) is int and n > 0 for n in viewport), device + ".viewport must be [width, height]")
        if not sample["observed"] or not nonempty(sample["screenshot"]):
            missing.append(device + " screenshot must be captured and actually observed")

    comparison = object_field(report, "comparison")
    require(type(comparison.get("reviewed")) is bool, "comparison.reviewed must be boolean")
    require(comparison.get("kind") in ("reference", "design-spec"), "comparison.kind is invalid")
    require(type(comparison.get("same_conditions")) is bool, "comparison.same_conditions must be boolean")
    require(isinstance(comparison.get("baseline"), str)
            and isinstance(comparison.get("implemented"), str), "comparison evidence must be strings")
    if not comparison["reviewed"] or not nonempty(comparison["baseline"]) or not nonempty(comparison["implemented"]):
        missing.append("visual comparison needs baseline and implementation evidence")
    if "E" in modifiers and (comparison["kind"] != "reference" or not comparison["same_conditions"]):
        missing.append("Pixel Fidelity requires a reference comparison under matched conditions")

    dimensions = object_field(report, "dimensions")
    require(set(dimensions) == set(DIMENSIONS), "dimensions must contain exactly the six fidelity dimensions")
    for name in DIMENSIONS:
        dimension = object_field(dimensions, name)
        require(type(dimension.get("applicable")) is bool, name + ".applicable must be boolean")
        score = dimension.get("score")
        if not dimension["applicable"]:
            require(name not in ("layout", "responsive"), name + " cannot be exempted")
            require(score is None and nonempty(dimension.get("reason")), name + " N/A needs null score and reason")
            continue
        evidence = dimension.get("evidence")
        require(isinstance(evidence, list) and all(nonempty(x) for x in evidence), name + ".evidence must be string references")
        if score is None:
            missing.append(name + " score is unknown")
        else:
            require(type(score) in (int, float) and math.isfinite(score) and 0 <= score <= 10,
                    name + " score must be finite and between 0 and 10")
            if score < 7:
                repair.append(name + " is below 7/10")
        if not evidence:
            missing.append(name + " has no observation evidence")

    differences = report.get("differences")
    require(isinstance(differences, list), "differences must be a list")
    seen = set()
    for item in differences:
        require(isinstance(item, dict), "difference must be an object")
        identifier = item.get("id")
        require(nonempty(identifier) and identifier not in seen, "difference IDs must be nonempty and unique")
        seen.add(identifier)
        require(item.get("severity") in ("Critical", "Major", "Minor"), identifier + " has invalid severity")
        require(type(item.get("resolved")) is bool, identifier + ".resolved must be boolean")
        require(all(nonempty(item.get(key)) for key in ("location", "evidence", "description")),
                identifier + " needs location, evidence and description")
        if not item["resolved"] and item["severity"] in ("Critical", "Major"):
            repair.append(identifier + " unresolved " + item["severity"])

    status = "needs-repair" if repair else ("unverified" if missing else "verified")
    return {"status": status, "scope": report["scope"], "iteration": report["iteration"],
            "repair_reasons": repair, "missing_evidence": missing,
            "note": "Checks declared evidence and thresholds, not screenshots or report authenticity."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="Path to a QA JSON report")
    args = parser.parse_args(argv)
    try:
        result = evaluate(json.loads(args.report.read_text(encoding="utf-8")))
    except (OSError, ValueError, ReportError) as error:
        result = {"status": "invalid-report", "error": str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return EXIT_CODES[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
