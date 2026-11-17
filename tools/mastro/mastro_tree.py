"""Shared strict parser and literal matching used by pilot/cohort analysis."""
from decimal import Decimal as D
import re

LINE = re.compile(r"([0-9A-Fa-f]+)\t([0-9]+)\t(.*) \(([0-9]+(?:\.[0-9]+)?)\)$")


def parse_tree(text):
    """Parse the verified one-level native TreeView syntax without trimming labels."""
    lines = text.splitlines()
    if not lines or not re.fullmatch(r"nodes=[0-9]+", lines[0]):
        raise ValueError("Missing complete node count")
    declared = int(lines[0].split("=")[1])
    result = []
    for line in lines[1:]:
        if not line:
            raise ValueError("Unexpected blank node row")
        match = LINE.fullmatch(line)
        if not match or match[2] != "0" or not match[3]:
            raise ValueError("Malformed or non-root tree record: " + line)
        result.append({"word": match[3], "weight": D(match[4])})
    if len(result) != declared:
        raise ValueError("Node count mismatch")
    return result


def first_matches(words, records):
    first = {}
    for record in records:
        first.setdefault(record["word"].lower(), record["weight"])
    return [first.get(word.lower(), D(0)) for word in words]
