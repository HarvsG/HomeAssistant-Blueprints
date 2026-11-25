#!/usr/bin/env python3
"""Validate all YAML files and Home Assistant blueprints in the repository.

Checks:
1. Valid YAML syntax across all .yaml/.yml files (supporting Home Assistant tags like !input).
2. No duplicate keys in any YAML mapping.
3. Valid Home Assistant blueprint metadata & !input references on blueprint files.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
VALID_BLUEPRINT_DOMAINS = {"automation", "script", "template"}
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


class UniqueKeyHALoader(yaml.SafeLoader):
    """YAML SafeLoader that rejects duplicate mapping keys and tracks !input references."""

    def __init__(self, stream):
        super().__init__(stream)
        self.used_inputs: set[str] = set()


def _construct_mapping_no_dupes(loader: UniqueKeyHALoader, node: yaml.MappingNode, deep: bool = False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.MarkedYAMLError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


def _construct_input_tag(loader: UniqueKeyHALoader, node: yaml.Node) -> str:
    val = loader.construct_scalar(node)
    loader.used_inputs.add(val)
    return f"!input {val}"


def _construct_generic_ha_tag(loader: UniqueKeyHALoader, tag_suffix: str, node: yaml.Node):
    if isinstance(node, yaml.ScalarNode):
        return f"!{tag_suffix} {loader.construct_scalar(node)}"
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


UniqueKeyHALoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping_no_dupes,
)
UniqueKeyHALoader.add_constructor("!input", _construct_input_tag)
for _tag in ("!secret", "!include", "!include_dir_list", "!include_dir_named", "!include_dir_merge_list", "!include_dir_merge_named", "!env_var"):
    UniqueKeyHALoader.add_constructor(
        _tag,
        lambda loader, node, t=_tag[1:]: _construct_generic_ha_tag(loader, t, node),
    )


def collect_defined_inputs(input_block: dict) -> set[str]:
    defined: set[str] = set()
    for key, val in input_block.items():
        if isinstance(val, dict) and "input" in val and isinstance(val["input"], dict):
            defined.update(val["input"].keys())
        else:
            defined.add(key)
    return defined


def validate_blueprint(rel_path: Path, data: dict, used_inputs: set[str]) -> list[str]:
    errors: list[str] = []
    bp = data.get("blueprint")
    if not isinstance(bp, dict):
        return ["'blueprint' key must be a mapping"]

    for req in ("name", "domain"):
        if not isinstance(bp.get(req), str) or not bp[req].strip():
            errors.append(f"blueprint.{req} must be a non-empty string")

    domain = bp.get("domain")
    if isinstance(domain, str) and domain not in VALID_BLUEPRINT_DOMAINS:
        errors.append(f"blueprint.domain {domain!r} is not one of {sorted(VALID_BLUEPRINT_DOMAINS)}")

    ha_meta = bp.get("homeassistant")
    if ha_meta is not None:
        if not isinstance(ha_meta, dict):
            errors.append("blueprint.homeassistant must be a mapping")
        elif "min_version" in ha_meta:
            mv = ha_meta["min_version"]
            if not isinstance(mv, str) or not VERSION_RE.match(mv):
                errors.append("blueprint.homeassistant.min_version must be formatted as 'YYYY.M.P'")

    raw_inputs = bp.get("input") or {}
    if not isinstance(raw_inputs, dict):
        errors.append("blueprint.input must be a mapping")
    else:
        defined_inputs = collect_defined_inputs(raw_inputs)
        missing = sorted(used_inputs - defined_inputs)
        if missing:
            errors.append(f"!input reference(s) missing from blueprint.input: {', '.join(missing)}")

    return errors


def validate_file(path: Path) -> list[str]:
    rel = path.relative_to(REPO_ROOT)
    text = path.read_text(encoding="utf-8")
    loader = UniqueKeyHALoader(text)
    try:
        docs = []
        while loader.check_data():
            docs.append(loader.get_data())
    except yaml.YAMLError as exc:
        return [f"YAML syntax error: {exc}"]
    finally:
        loader.dispose()

    if not docs or all(d is None for d in docs):
        return ["YAML file is empty"]

    errors: list[str] = []
    for doc in docs:
        if not isinstance(doc, dict):
            errors.append(f"Top-level YAML document must be a mapping, got {type(doc).__name__}")
            continue
        if rel.parts[0] != ".github" and "blueprint" in doc:
            errors.extend(validate_blueprint(rel, doc, loader.used_inputs))
    return errors


def main() -> int:
    yaml_files = sorted(
        p for p in REPO_ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in {".yaml", ".yml"} and ".git" not in p.parts
    )
    if not yaml_files:
        print("No YAML files found.")
        return 1

    failed = 0
    for path in yaml_files:
        rel = path.relative_to(REPO_ROOT)
        errs = validate_file(path)
        if errs:
            failed += 1
            for err in errs:
                print(f"::error file={rel}::{err}")
                print(f"FAIL  {rel}: {err}")
        else:
            print(f"OK    {rel}")

    print(f"\nValidated {len(yaml_files)} YAML file(s) ({len(yaml_files) - failed} passed, {failed} failed).")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
