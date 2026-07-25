#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


class JaCoCoParseError(Exception):
    """Raised when the XML is not a valid JaCoCo report."""


@dataclass
class CounterData:
    missed: int
    covered: int


@dataclass
class MethodData:
    name: str
    desc: str                    # JVM descriptor (params_string)
    offset: int                  # line number offset
    lines_covered_status: str    # JSON: {line_no: 0|1|2}
    counters: dict[str, CounterData] = field(default_factory=dict)


@dataclass
class ClassData:
    name: str
    source_file_name: str
    methods: list[MethodData] = field(default_factory=list)
    counters: dict[str, CounterData] = field(default_factory=dict)
    file_content: str | None = None
    source_path: str | None = None
    md5: str | None = None


@dataclass
class PackageData:
    name: str
    classes: list[ClassData] = field(default_factory=list)
    counters: dict[str, CounterData] = field(default_factory=dict)


@dataclass
class ParseResult:
    report_name: str
    packages: list[PackageData] = field(default_factory=list)
    package_count: int = 0
    class_count: int = 0
    method_count: int = 0
    coverage_rate: str = "0.0%"


def _parse_counter(element: ET.Element) -> tuple[str, CounterData]:
    """Parse a <counter> element into (type, CounterData)."""
    counter_type = element.get("type", "")
    missed = int(element.get("missed", "0"))
    covered = int(element.get("covered", "0"))
    return counter_type, CounterData(missed=missed, covered=covered)


def _parse_method(element: ET.Element) -> MethodData:
    """Parse a <method> element into MethodData."""
    name = element.get("name", "")
    desc = element.get("desc", "")
    offset = int(element.get("line", "0"))
    counters: dict[str, CounterData] = {}
    for counter_el in element.findall("counter"):
        ctype, cdata = _parse_counter(counter_el)
        counters[ctype] = cdata
    # lines_covered_status is populated as empty JSON object at parse time;
    # it is enriched later when source file content is available.
    lines_covered_status = json.dumps({})
    return MethodData(
        name=name,
        desc=desc,
        offset=offset,
        lines_covered_status=lines_covered_status,
        counters=counters,
    )


def _parse_class(element: ET.Element) -> ClassData:
    """Parse a <class> element into ClassData."""
    name = element.get("name", "")
    source_file_name = element.get("sourcefilename", "")
    methods: list[MethodData] = []
    counters: dict[str, CounterData] = {}
    for child in element:
        if child.tag == "method":
            methods.append(_parse_method(child))
        elif child.tag == "counter":
            ctype, cdata = _parse_counter(child)
            counters[ctype] = cdata
    return ClassData(
        name=name,
        source_file_name=source_file_name,
        methods=methods,
        counters=counters,
    )


def _parse_package(element: ET.Element) -> PackageData:
    """Parse a <package> element into PackageData."""
    name = element.get("name", "")
    classes: list[ClassData] = []
    counters: dict[str, CounterData] = {}
    for child in element:
        if child.tag == "class":
            classes.append(_parse_class(child))
        elif child.tag == "counter":
            ctype, cdata = _parse_counter(child)
            counters[ctype] = cdata
    return PackageData(name=name, classes=classes, counters=counters)


def _compute_coverage_rate(packages: list[PackageData]) -> str:
    """Compute overall instruction coverage rate from all packages."""
    total_missed = 0
    total_covered = 0
    for pkg in packages:
        instr = pkg.counters.get("INSTRUCTION")
        if instr:
            total_missed += instr.missed
            total_covered += instr.covered
    total = total_missed + total_covered
    if total == 0:
        return "0.0%"
    rate = round(total_covered / total * 100, 1)
    return f"{rate}%"


class JaCoCoParser:
    """Parser for JaCoCo XML coverage reports."""

    def validate(self, xml_content: bytes) -> bool:
        """
        Validate that the XML is a valid JaCoCo report.

        Checks for <report> root element and at least one <package> child.
        Returns False for malformed XML or non-JaCoCo documents.
        """
        try:
            root = ET.fromstring(xml_content)
            return root.tag == "report" and root.find("package") is not None
        except ET.ParseError:
            return False

    def parse(self, xml_content: bytes) -> ParseResult:
        """
        Parse JaCoCo XML bytes into structured coverage data.

        Returns a ParseResult with packages, classes, methods, and counters.
        Raises JaCoCoParseError if the XML is not a valid JaCoCo report.
        """
        if not self.validate(xml_content):
            raise JaCoCoParseError("Invalid JaCoCo XML: missing <report> root or <package> children")

        root = ET.fromstring(xml_content)
        report_name = root.get("name", "")
        packages: list[PackageData] = []

        for child in root:
            if child.tag == "package":
                packages.append(_parse_package(child))

        package_count = len(packages)
        class_count = sum(len(pkg.classes) for pkg in packages)
        method_count = sum(
            len(cls.methods) for pkg in packages for cls in pkg.classes
        )
        coverage_rate = _compute_coverage_rate(packages)

        return ParseResult(
            report_name=report_name,
            packages=packages,
            package_count=package_count,
            class_count=class_count,
            method_count=method_count,
            coverage_rate=coverage_rate,
        )


# ---------------------------------------------------------------------------
# Serialization helper (used for round-trip property testing)
# ---------------------------------------------------------------------------

def serialize_to_xml(result: ParseResult) -> bytes:
    """
    Serialize a ParseResult back to JaCoCo XML format.

    This is the inverse of JaCoCoParser.parse and is used for round-trip
    property testing (Property 1).
    """
    report_el = ET.Element("report", name=result.report_name)

    for pkg in result.packages:
        pkg_el = ET.SubElement(report_el, "package", name=pkg.name)

        for cls in pkg.classes:
            cls_attrs: dict[str, str] = {"name": cls.name}
            if cls.source_file_name:
                cls_attrs["sourcefilename"] = cls.source_file_name
            cls_el = ET.SubElement(pkg_el, "class", **cls_attrs)

            for method in cls.methods:
                method_attrs: dict[str, str] = {
                    "name": method.name,
                    "desc": method.desc,
                    "line": str(method.offset),
                }
                method_el = ET.SubElement(cls_el, "method", **method_attrs)
                for ctype, cdata in method.counters.items():
                    ET.SubElement(
                        method_el,
                        "counter",
                        type=ctype,
                        missed=str(cdata.missed),
                        covered=str(cdata.covered),
                    )

            # Class-level counters
            for ctype, cdata in cls.counters.items():
                ET.SubElement(
                    cls_el,
                    "counter",
                    type=ctype,
                    missed=str(cdata.missed),
                    covered=str(cdata.covered),
                )

        # Package-level counters
        for ctype, cdata in pkg.counters.items():
            ET.SubElement(
                pkg_el,
                "counter",
                type=ctype,
                missed=str(cdata.missed),
                covered=str(cdata.covered),
            )

    tree = ET.ElementTree(report_el)
    ET.indent(tree, space="  ")
    return ET.tostring(report_el, encoding="utf-8", xml_declaration=True)
