# Downstream Mirror Sync Setup (Gists & Forum)

[`sync-downstream.yml`](./workflows/sync-downstream.yml) keeps legacy **GitHub Gists** and **Home Assistant Community Forum** inline YAML blocks automatically in sync whenever `.yaml` files on `main` are updated.

This preserves:
1. All existing **Discourse download/click counters** on `my.home-assistant.io` import badges.
2. Seamless **Re-import blueprint** updates for users who originally imported from a Gist or Forum URL.

## Required Repository Secrets

Configure these under **Settings → Secrets and variables → Actions** in `HarvsG/HomeAssistant-Blueprints`:

| Secret Name | Purpose | How to Create |
|---|---|---|
| `GIST_TOKEN` | Updates your Gist mirrors via `PATCH /gists/{id}` | GitHub **Settings → Developer settings → Personal access tokens** → create a token with **`gist`** write permission. |
| `DISCOURSE_USER_API_KEY` | Updates inline ```` ```yaml ```` blocks on `community.home-assistant.io` | Discourse encrypted User API Key (`read,write` scope). |
| `DISCOURSE_USER_API_CLIENT_ID` | *(Optional)* Matching `client_id` for the Discourse User API Key | Set alongside `DISCOURSE_USER_API_KEY`. |
