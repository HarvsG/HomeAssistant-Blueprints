# Downstream Mirror Sync Setup (Gists & Forum)

[`sync-downstream.yml`](./workflows/sync-downstream.yml) keeps legacy **GitHub Gists** and **Home Assistant Community Forum** inline YAML blocks automatically in sync whenever `.yaml` files on `main` are updated.

This preserves:
1. All existing **Discourse download/click counters** on `my.home-assistant.io` import badges.
2. Seamless **Re-import blueprint** updates for users who originally imported from a Gist or Forum URL.

## Required Repository Secrets

Configure these under **[Settings → Secrets and variables → Actions](https://github.com/HarvsG/HomeAssistant-Blueprints/settings/secrets/actions)**:

| Secret Name | Purpose | Status / How to Create |
|---|---|---|
| `GIST_TOKEN` | Updates your Gist mirrors via `PATCH /gists/{id}` | Create a **Fine-grained Personal Access Token** with only the **`Gists: Read and write`** account permission ([pre-filled creation link](https://github.com/settings/personal-access-tokens/new?name=HomeAssistant-Blueprints+Gist+Sync&description=Auto-sync+blueprints+from+HomeAssistant-Blueprints+to+Gist+mirrors&expires_in=none&gists=write)), then paste it into **[New repository secret](https://github.com/HarvsG/HomeAssistant-Blueprints/settings/secrets/actions/new)** named `GIST_TOKEN`. |
| `DISCOURSE_USER_API_KEY` | Updates inline ```` ```yaml ```` blocks on `community.home-assistant.io` | Already configured via Discourse encrypted User API Key (`read,write` scope). |
| `DISCOURSE_USER_API_CLIENT_ID` | Matching `client_id` for the Discourse User API Key | Already configured alongside `DISCOURSE_USER_API_KEY`. |
