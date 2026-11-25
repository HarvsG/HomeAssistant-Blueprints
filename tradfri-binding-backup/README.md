# ZHA IKEA Tradfri On/Off Switch — Binding Backup & Self-Healing

Direct Zigbee bindings between switches and bulbs keep lights working even if Home Assistant is offline — however, IKEA Tradfri bindings can occasionally drop over time. This folder contains a **paired two-blueprint solution**:

1. An **automation blueprint** that detects when bound bulbs fail to respond to a switch command, sends a fallback Home Assistant `light.turn_on` / `light.turn_off` command after 1.5s, and notifies you.
2. A **script blueprint** (using [ZHA Toolkit](https://github.com/mdeweerd/zha-toolkit)) called automatically by the automation to remove stale bindings and re-bind the switch and bulb.

- **Forum Discussion**: [ZHA IKEA Tradfri on/off switch binding backup and self healing](https://community.home-assistant.io/t/zha-ikea-tradfri-on-off-switch-binding-backup-and-self-healing/934393)

---

## Files in This Folder

### 1. [`tradfri-on-off-binding-backup.yaml`](./tradfri-on-off-binding-backup.yaml) *(Automation Blueprint)*

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Ftradfri-binding-backup%2Ftradfri-on-off-binding-backup.yaml)

Create one automation from this blueprint per IKEA Tradfri On/Off switch, selecting the ZHA switch device and its bound light entities.

### 2. [`heal_ikea_zha_bindings.yaml`](./heal_ikea_zha_bindings.yaml) *(Script Blueprint)*

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Ftradfri-binding-backup%2Fheal_ikea_zha_bindings.yaml)

Import once and create a single script (`script.heal_ikea_zha_bindings`). Requires [ZHA Toolkit](https://github.com/mdeweerd/zha-toolkit?tab=readme-ov-file#setup) installed via HACS and enabled in `configuration.yaml`.

---

## Setup Steps

1. Import **`tradfri-on-off-binding-backup.yaml`** and create an automation for each bound Tradfri On/Off switch. *(If you only want backup control + notifications without automatic re-binding, clear the `Post-action` input and stop here.)*
2. Install and configure **[ZHA Toolkit](https://github.com/mdeweerd/zha-toolkit?tab=readme-ov-file#setup)** (remember to add `zha_toolkit:` to your `configuration.yaml`).
3. Import **`heal_ikea_zha_bindings.yaml`** and save the script with its default entity ID (`script.heal_ikea_zha_bindings`). If you use a different script name, update `Post-action` in your backup automations to match.
