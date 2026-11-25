#!/usr/bin/env python3
"""Sync blueprints, scripts, automations, and templates from this repo to legacy Gist & Forum mirrors.

Includes pre-sync drift/conflict detection so out-of-band edits made directly to a Gist or Forum
YAML block are never silently overwritten unless FORCE_OVERWRITE=true is explicitly passed.
"""

from __future__ import annotations

from datetime import datetime
import difflib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FORUM_BASE = "https://community.home-assistant.io"

# Repo path -> list of (gist_id, gist_filename)
GIST_MIRRORS: dict[str, list[tuple[str, str]]] = {
    "circadian-lighting/match-color-temp-kelvin.yaml": [
        ("cc86381dc99169159d6d4cd870c36e46", "match-color-temp-kelvin.yaml"),
    ],
    "circadian-lighting/match-color-temp-mireds.yaml": [
        ("e01d589e2eadd056521101ea98a44ac4", "match-color-temp-mireds.yaml"),
        ("b14309ca061c549fa677b159808b40db", "deprecated_match_color_temp.yaml"),
    ],
    "toggle-scene/toggle-scene.yaml": [
        ("493595880d45f2ed5e82f762b12980fa", "toggle-scene.yaml"),
    ],
    "bayesian-probability-sensor/bayesian_probability_sensor.yaml": [
        ("6fff58238fa7b2f8217d9326f6bc997f", "bayesian_probability_sensor.yaml"),
    ],
    "tradfri-binding-backup/tradfri-on-off-binding-backup.yaml": [
        ("f56ddd55d03e4c3fcfdf513b4cea3ece", "tradfri-on-off-binding-backup.yaml"),
    ],
    "tradfri-binding-backup/heal_ikea_zha_bindings.yaml": [
        ("b1508cc130d514ef690418a612ee9d47", "heal_ikea_zha_bindings.yaml"),
    ],
}

# Repo path -> (topic_id, post_id) for forum posts with inline YAML code blocks
FORUM_INLINE_MIRRORS: dict[str, tuple[int, int]] = {
    "tradfri-shortcut-button/zha-ikea-tradfri-shortcut-button-firmware-2-3-075-or-greater.yaml": (402565, 1809043),
    "tradfri-shortcut-button/beta-zha-ikea-tradfri-shortcut-button.yaml": (587663, 2456356),
    "roborock-cleaning/roborock_clean_script.yaml": (896307, 3467610),
    "tailscale-phone-vpn/tailscale_away_from_home_automation.yaml": (576826, 2418030),
    "circadian-lighting/sun-color-temp-template.yaml": (402510, 1808892),
}

YAML_FENCE_RE = re.compile(r"(```(?:yaml|yml)\n)(.*?)(\n```)", re.DOTALL)
ZERO_SHA = "0" * 40


class CloudflareChallengeError(RuntimeError):
    """Raised when Cloudflare serves an anti-bot challenge to a cloud runner IP."""


def normalize_yaml(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def format_diff(expected: str, actual_remote: str, expected_label: str, remote_label: str) -> str:
    lines = list(
        difflib.unified_diff(
            expected.strip().splitlines(),
            actual_remote.strip().splitlines(),
            fromfile=expected_label,
            tofile=remote_label,
            n=2,
            lineterm="",
        )
    )
    return "\n    ".join(lines[:60]) + ("\n    ... (diff truncated)" if len(lines) > 60 else "")


def git_file_at(rev: str, rel_path: str) -> str | None:
    res = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"{rev}:{rel_path}"],
        capture_output=True,
        text=True,
    )
    return res.stdout if res.returncode == 0 else None


def git_file_history(rel_path: str) -> tuple[datetime | None, set[str]]:
    """Return (latest_commit_datetime, set_of_normalized_prior_contents) for rel_path."""
    res = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "log", "--format=%H %cI", "--", rel_path],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0 or not res.stdout.strip():
        return None, set()
    entries = [line.strip().split(" ", 1) for line in res.stdout.strip().splitlines() if " " in line]
    head_dt = datetime.fromisoformat(entries[0][1])
    prior_contents: set[str] = set()
    for sha, _ in entries[1:]:
        blob = git_file_at(sha, rel_path)
        if blob is not None:
            prior_contents.add(normalize_yaml(blob))
    return head_dt, prior_contents


def verify_target_not_modified_out_of_band(
    *,
    rel_path: str,
    target_label: str,
    remote_content: str,
    remote_updated_at: datetime | None,
    before_sha: str | None,
    force_overwrite: bool,
) -> tuple[bool, str]:
    """Check if remote_content is safe to overwrite with current HEAD of rel_path.

    Returns (is_safe, reason_message).
    """
    norm_remote = normalize_yaml(remote_content)

    # Case A: Push event with a known pre-push commit SHA
    if before_sha and before_sha != ZERO_SHA:
        before_blob = git_file_at(before_sha, rel_path)
        if before_blob is None:
            # Newly added file in this push; remote shouldn't already have divergent content unless forced
            if not norm_remote or force_overwrite:
                return True, "new file"
            diff = format_diff("", remote_content, f"repo:{before_sha[:7]}:{rel_path} (absent)", target_label)
            return (
                False,
                f"{target_label} already has unexpected content before new file {rel_path} was synced:\n    {diff}",
            )

        norm_before = normalize_yaml(before_blob)
        if norm_remote == norm_before:
            return True, f"matches pre-push commit {before_sha[:7]}"

        if force_overwrite:
            return True, f"out-of-band change overridden by FORCE_OVERWRITE=true"

        diff = format_diff(before_blob, remote_content, f"expected (repo {before_sha[:7]})", f"actual ({target_label})")
        return (
            False,
            f"{target_label} was modified out-of-band (does not match pre-push commit {before_sha[:7]} of {rel_path}). "
            f"Refusing to overwrite!\n    {diff}",
        )

    # Case B: Manual workflow_dispatch or local run without before_sha
    head_dt, prior_contents = git_file_history(rel_path)
    if norm_remote in prior_contents:
        if remote_updated_at is not None and head_dt is not None and remote_updated_at > head_dt:
            if force_overwrite:
                return True, "out-of-band timestamp overridden by FORCE_OVERWRITE=true"
            return (
                False,
                f"{target_label} was updated at {remote_updated_at.isoformat()} (after latest repo commit "
                f"{head_dt.isoformat()} for {rel_path}). Refusing to overwrite!",
            )
        return True, "matches ancestor commit in git history"

    if force_overwrite:
        return True, "out-of-band change overridden by FORCE_OVERWRITE=true"

    head_blob = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
    diff = format_diff(head_blob, remote_content, f"repo HEAD ({rel_path})", f"actual ({target_label})")
    return (
        False,
        f"{target_label} contains changes not found in {rel_path}'s git history. "
        f"Refusing to overwrite!\n    {diff}",
    )


def curl_json(method: str, url: str, headers_file: str | None = None, payload: dict | None = None) -> dict:
    cmd = ["curl", "-sS", "-X", method, "-w", "\n%{http_code}"]
    if headers_file:
        cmd += ["-H", f"@{headers_file}"]
    payload_file = None
    try:
        if payload is not None:
            fd, payload_file = tempfile.mkstemp(suffix=".json")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f)
            cmd += ["-H", "Content-Type: application/json", "--data-binary", f"@{payload_file}"]
        cmd.append(url)
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        body, _, status = res.stdout.rpartition("\n")
        if status == "403" and ("Just a moment..." in body or "cf-mitigated" in body):
            raise CloudflareChallengeError(f"Cloudflare anti-bot challenge gated {url} from this runner IP.")
        if not status.startswith("2"):
            raise RuntimeError(f"HTTP {status} for {method} {url}: {body[:300]}")
        return json.loads(body) if body.strip() else {}
    finally:
        if payload_file and os.path.exists(payload_file):
            os.remove(payload_file)


def get_changed_files(before_sha: str | None) -> set[str] | None:
    """On push events, return changed repo-relative paths; return None to check all files."""
    if os.environ.get("GITHUB_EVENT_NAME") != "push":
        return None
    base = before_sha if (before_sha and before_sha != ZERO_SHA) else "HEAD~1"
    res = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "diff", "--name-only", base, "HEAD"],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        return None
    return {line.strip() for line in res.stdout.splitlines() if line.strip()}


def sync_gists(
    gist_token: str,
    *,
    before_sha: str | None = None,
    force_overwrite: bool = False,
    dry_run: bool = False,
) -> int:
    print("=== Syncing Gist Mirrors ===")
    conflicts = 0
    fd, hdr_path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(
                f"Authorization: Bearer {gist_token}\n"
                "Accept: application/vnd.github+json\n"
                "X-GitHub-Api-Version: 2022-11-28\n"
            )
        os.chmod(hdr_path, 0o600)

        for rel_path, targets in GIST_MIRRORS.items():
            local_content = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            norm_local = normalize_yaml(local_content)
            for gist_id, gist_fname in targets:
                label = f"Gist {gist_id} ({gist_fname})"
                gist = curl_json("GET", f"https://api.github.com/gists/{gist_id}", headers_file=hdr_path)
                remote_content = gist.get("files", {}).get(gist_fname, {}).get("content", "")
                if normalize_yaml(remote_content) == norm_local:
                    print(f"  [up-to-date] {label}")
                    continue

                updated_str = gist.get("updated_at")
                remote_dt = datetime.fromisoformat(updated_str.replace("Z", "+00:00")) if updated_str else None
                ok, reason = verify_target_not_modified_out_of_band(
                    rel_path=rel_path,
                    target_label=label,
                    remote_content=remote_content,
                    remote_updated_at=remote_dt,
                    before_sha=before_sha,
                    force_overwrite=force_overwrite,
                )
                if not ok:
                    print(f"::error title=Out-of-band Gist edit detected::{label} has unmerged external changes.")
                    print(f"  [CONFLICT] {reason}")
                    conflicts += 1
                    continue

                if dry_run:
                    print(f"  [would-update] {label} from {rel_path} ({reason})")
                    continue
                curl_json(
                    "PATCH",
                    f"https://api.github.com/gists/{gist_id}",
                    headers_file=hdr_path,
                    payload={"files": {gist_fname: {"content": local_content}}},
                )
                print(f"  [updated] {label} from {rel_path} ({reason})")
    finally:
        if os.path.exists(hdr_path):
            os.remove(hdr_path)
    return conflicts


def sync_forum_posts(
    api_key: str,
    *,
    client_id: str | None = None,
    changed_files: set[str] | None = None,
    before_sha: str | None = None,
    force_overwrite: bool = False,
    dry_run: bool = False,
) -> int:
    targets = {
        rel_path: ids
        for rel_path, ids in FORUM_INLINE_MIRRORS.items()
        if changed_files is None or rel_path in changed_files
    }
    if not targets:
        print("=== Syncing Forum Inline YAML Blocks ===\n  No inline-forum YAML files changed in this push; skipping.")
        return 0

    print("=== Syncing Forum Inline YAML Blocks ===")
    conflicts = 0
    fd, hdr_path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"User-Api-Key: {api_key}\nAccept: application/json\n")
            if client_id:
                f.write(f"User-Api-Client-Id: {client_id}\n")
        os.chmod(hdr_path, 0o600)

        commit_sha = os.environ.get("GITHUB_SHA", "")[:7]
        reason_suffix = f" (commit {commit_sha})" if commit_sha else ""

        for rel_path, (topic_id, post_id) in targets.items():
            label = f"Forum topic #{topic_id} (post {post_id})"
            local_yaml = (REPO_ROOT / rel_path).read_text(encoding="utf-8").strip()
            try:
                post = curl_json("GET", f"{FORUM_BASE}/posts/{post_id}.json", headers_file=hdr_path)
            except CloudflareChallengeError as exc:
                affected = ", ".join(f"#{tid}" for tid, _ in targets.values())
                print(
                    f"::warning title=Cloudflare blocked GitHub runner IP::"
                    f"{exc} Forum topic(s) {affected} were not synced automatically; "
                    f"re-run later or run .github/scripts/sync_downstream.py locally."
                )
                return conflicts

            raw = post.get("raw", "")
            matches = list(YAML_FENCE_RE.finditer(raw))
            if len(matches) != 1:
                raise RuntimeError(
                    f"Expected exactly 1 ```yaml fence in {label}, found {len(matches)}"
                )
            m = matches[0]
            current_yaml = m.group(2).strip()
            if normalize_yaml(current_yaml) == normalize_yaml(local_yaml):
                print(f"  [up-to-date] {label}")
                continue

            # Note: post['updated_at'] also changes on prose-only edits, so pass None for remote_updated_at
            # and rely on exact git-blob ancestry matching (or pre-push before_sha matching).
            ok, reason = verify_target_not_modified_out_of_band(
                rel_path=rel_path,
                target_label=label,
                remote_content=current_yaml,
                remote_updated_at=None,
                before_sha=before_sha,
                force_overwrite=force_overwrite,
            )
            if not ok:
                print(f"::error title=Out-of-band Forum YAML edit detected::{label} has unmerged external changes.")
                print(f"  [CONFLICT] {reason}")
                conflicts += 1
                continue

            new_raw = raw[: m.start()] + m.group(1) + local_yaml + m.group(3) + raw[m.end() :]
            if dry_run:
                print(f"  [would-update] {label} from {rel_path} ({reason})")
                continue
            try:
                curl_json(
                    "PUT",
                    f"{FORUM_BASE}/posts/{post_id}.json",
                    headers_file=hdr_path,
                    payload={
                        "post": {
                            "raw": new_raw,
                            "edit_reason": f"Auto-synced from HarvsG/HomeAssistant-Blueprints{reason_suffix}",
                        }
                    },
                )
            except CloudflareChallengeError as exc:
                print(
                    f"::warning title=Cloudflare blocked GitHub runner IP::"
                    f"{exc} {label} could not be updated from this cloud runner IP."
                )
                return conflicts
            print(f"  [updated] {label} from {rel_path} ({reason})")
    finally:
        if os.path.exists(hdr_path):
            os.remove(hdr_path)
    return conflicts


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    force_overwrite = "--force" in sys.argv or os.environ.get("FORCE_OVERWRITE", "false").strip().lower() == "true"
    before_sha = os.environ.get("GITHUB_EVENT_BEFORE", "").strip() or None
    gist_token = os.environ.get("GIST_TOKEN", "").strip()
    discourse_key = os.environ.get("DISCOURSE_USER_API_KEY", "").strip()
    discourse_client_id = os.environ.get("DISCOURSE_USER_API_CLIENT_ID", "").strip() or None
    sync_forum_flag = os.environ.get("SYNC_FORUM", "true").strip().lower() != "false"

    if not gist_token and not discourse_key:
        print("Notice: Neither GIST_TOKEN nor DISCOURSE_USER_API_KEY is set; nothing to sync.")
        return 0

    conflicts = 0
    if gist_token:
        conflicts += sync_gists(
            gist_token,
            before_sha=before_sha if os.environ.get("GITHUB_EVENT_NAME") == "push" else None,
            force_overwrite=force_overwrite,
            dry_run=dry_run,
        )
    else:
        print("Skipping Gist sync (GIST_TOKEN not configured).")

    if discourse_key and sync_forum_flag:
        changed_files = get_changed_files(before_sha)
        conflicts += sync_forum_posts(
            discourse_key,
            client_id=discourse_client_id,
            changed_files=changed_files,
            before_sha=before_sha if os.environ.get("GITHUB_EVENT_NAME") == "push" else None,
            force_overwrite=force_overwrite,
            dry_run=dry_run,
        )
    elif not sync_forum_flag:
        print("Skipping Forum sync (disabled via workflow input).")
    else:
        print("Skipping Forum sync (DISCOURSE_USER_API_KEY not configured).")

    if conflicts:
        print(
            f"\nAborted {conflicts} target(s) due to out-of-band modifications! "
            "Port those external changes into this repository first, or run the workflow manually "
            "with 'force_overwrite: true' if you intend to overwrite them."
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
