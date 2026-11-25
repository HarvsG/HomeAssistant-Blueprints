#!/usr/bin/env python3
"""Sync blueprints, scripts, automations, and templates from this repo to legacy Gist & Forum mirrors.

Preserves existing Home Assistant Community Forum import link counters and 'Re-import blueprint'
compatibility while keeping this GitHub repository as the single source of truth.
"""

from __future__ import annotations

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
        if not status.startswith("2"):
            raise RuntimeError(f"HTTP {status} for {method} {url}: {body[:300]}")
        return json.loads(body) if body.strip() else {}
    finally:
        if payload_file and os.path.exists(payload_file):
            os.remove(payload_file)


def sync_gists(gist_token: str, dry_run: bool = False) -> None:
    print("=== Syncing Gist Mirrors ===")
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
            for gist_id, gist_fname in targets:
                gist = curl_json("GET", f"https://api.github.com/gists/{gist_id}", headers_file=hdr_path)
                remote_content = gist.get("files", {}).get(gist_fname, {}).get("content", "")
                if remote_content.rstrip() == local_content.rstrip():
                    print(f"  [up-to-date] Gist {gist_id} ({gist_fname})")
                    continue
                if dry_run:
                    print(f"  [would-update] Gist {gist_id} ({gist_fname}) from {rel_path}")
                    continue
                curl_json(
                    "PATCH",
                    f"https://api.github.com/gists/{gist_id}",
                    headers_file=hdr_path,
                    payload={"files": {gist_fname: {"content": local_content}}},
                )
                print(f"  [updated] Gist {gist_id} ({gist_fname}) from {rel_path}")
    finally:
        if os.path.exists(hdr_path):
            os.remove(hdr_path)


def sync_forum_posts(api_key: str, client_id: str | None = None, dry_run: bool = False) -> None:
    print("=== Syncing Forum Inline YAML Blocks ===")
    fd, hdr_path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"User-Api-Key: {api_key}\nAccept: application/json\n")
            if client_id:
                f.write(f"User-Api-Client-Id: {client_id}\n")
        os.chmod(hdr_path, 0o600)

        commit_sha = os.environ.get("GITHUB_SHA", "")[:7]
        reason_suffix = f" (commit {commit_sha})" if commit_sha else ""

        for rel_path, (topic_id, post_id) in FORUM_INLINE_MIRRORS.items():
            local_yaml = (REPO_ROOT / rel_path).read_text(encoding="utf-8").strip()
            post = curl_json("GET", f"{FORUM_BASE}/posts/{post_id}.json", headers_file=hdr_path)
            raw = post.get("raw", "")
            matches = list(YAML_FENCE_RE.finditer(raw))
            if len(matches) != 1:
                raise RuntimeError(
                    f"Expected exactly 1 ```yaml fence in topic #{topic_id} (post {post_id}), found {len(matches)}"
                )
            m = matches[0]
            current_yaml = m.group(2).strip()
            if current_yaml == local_yaml:
                print(f"  [up-to-date] Forum topic #{topic_id} (post {post_id})")
                continue
            new_raw = raw[: m.start()] + m.group(1) + local_yaml + m.group(3) + raw[m.end() :]
            if dry_run:
                print(f"  [would-update] Forum topic #{topic_id} (post {post_id}) from {rel_path}")
                continue
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
            print(f"  [updated] Forum topic #{topic_id} (post {post_id}) from {rel_path}")
    finally:
        if os.path.exists(hdr_path):
            os.remove(hdr_path)


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    gist_token = os.environ.get("GIST_TOKEN", "").strip()
    discourse_key = os.environ.get("DISCOURSE_USER_API_KEY", "").strip()
    discourse_client_id = os.environ.get("DISCOURSE_USER_API_CLIENT_ID", "").strip() or None

    if not gist_token and not discourse_key:
        print("Notice: Neither GIST_TOKEN nor DISCOURSE_USER_API_KEY is set; nothing to sync.")
        return 0

    if gist_token:
        sync_gists(gist_token, dry_run=dry_run)
    else:
        print("Skipping Gist sync (GIST_TOKEN not configured).")

    if discourse_key:
        sync_forum_posts(discourse_key, client_id=discourse_client_id, dry_run=dry_run)
    else:
        print("Skipping Forum sync (DISCOURSE_USER_API_KEY not configured).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
