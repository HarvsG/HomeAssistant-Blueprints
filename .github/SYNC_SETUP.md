# Downstream Mirror Sync Setup (Gists & Forum)

[`sync-downstream.yml`](./workflows/sync-downstream.yml) keeps legacy **GitHub Gists** and **Home Assistant Community Forum** inline YAML blocks automatically in sync whenever `.yaml` files on `main` are updated.

This preserves:
1. All existing **Discourse download/click counters** on `my.home-assistant.io` import badges.
2. Seamless **Re-import blueprint** updates for users who originally imported from a Gist or Forum URL.

## Out-of-Band Edit Protection (Conflict Check)

Before overwriting any Gist or Forum ```` ```yaml ```` block, [`sync_downstream.py`](./scripts/sync_downstream.py) verifies that the downstream target has **not** been modified out-of-band:
- **On `push` events**: The remote Gist / Forum YAML must match the file's content at the pre-push commit (`github.event.before`). If anyone edited the Gist or Forum YAML directly (even on a file untouched by the push), the script **refuses to overwrite it**, logs a unified diff of the external edits, and fails the workflow run so you get notified.
- **On manual `workflow_dispatch` runs**: Any remote target that differs from `HEAD` must match an ancestor commit in that file's git history (and, for Gists, have an `updated_at` timestamp older than the latest repo commit for that file).
- **Intentional override**: After merging or discarding external changes, you can manually dispatch the workflow with **`force_overwrite: true`** if you explicitly want `main` to overwrite a drifted mirror.

## Required Repository Secrets

Configured under **[Settings → Secrets and variables → Actions](https://github.com/HarvsG/HomeAssistant-Blueprints/settings/secrets/actions)**:

| Secret Name | Purpose | Status / How to Create |
|---|---|---|
| `GIST_TOKEN` | Updates your Gist mirrors via `PATCH /gists/{id}` | Create a **Fine-grained Personal Access Token** with only the **`Gists: Read and write`** account permission ([pre-filled creation link](https://github.com/settings/personal-access-tokens/new?name=HomeAssistant-Blueprints+Gist+Sync&description=Auto-sync+blueprints+from+HomeAssistant-Blueprints+to+Gist+mirrors&expires_in=none&gists=write)), then paste it into **[New repository secret](https://github.com/HarvsG/HomeAssistant-Blueprints/settings/secrets/actions/new)** named `GIST_TOKEN`. |
| `DISCOURSE_USER_API_KEY` | Updates inline ```` ```yaml ```` blocks on `community.home-assistant.io` | Configured via Discourse encrypted User API Key (`read,write` scope). |
| `DISCOURSE_USER_API_CLIENT_ID` | Matching `client_id` for the Discourse User API Key | Configured alongside `DISCOURSE_USER_API_KEY`. |
