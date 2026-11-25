# Home Assistant Blueprints, Scripts & Automations

A collection of Home Assistant **blueprints**, **scripts**, **automations**, and **templates** created by [@HarvsG](https://github.com/HarvsG), consolidated with full edit history from the [Home Assistant Community Forum](https://community.home-assistant.io/u/harvsg/activity/topics) and [GitHub Gists](https://gist.github.com/HarvsG).

---

## Blueprints (One-Click Import)

| Folder | Blueprint | Domain | Forum Thread | Import |
|---|---|---|---|---|
| [`circadian-lighting/`](./circadian-lighting/) | **Match Outside Colour Temperature (Kelvin)** *(HA 2022.10+)* | `automation` | [Thread #472105](https://community.home-assistant.io/t/automatic-circadian-lighting-match-your-lights-color-temperature-to-the-sun/472105) | [![Import](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Fcircadian-lighting%2Fmatch-color-temp-kelvin.yaml) |
| [`circadian-lighting/`](./circadian-lighting/) | **Match Outside Colour Temperature (Mireds)** *(Legacy pre-2022.9)* | `automation` | [Thread #472105](https://community.home-assistant.io/t/automatic-circadian-lighting-match-your-lights-color-temperature-to-the-sun/472105) | [![Import](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Fcircadian-lighting%2Fmatch-color-temp-mireds.yaml) |
| [`tradfri-binding-backup/`](./tradfri-binding-backup/) | **ZHA — IKEA Tradfri On/Off Switch Binding Backup** | `automation` | [Thread #934393](https://community.home-assistant.io/t/zha-ikea-tradfri-on-off-switch-binding-backup-and-self-healing/934393) | [![Import](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Ftradfri-binding-backup%2Ftradfri-on-off-binding-backup.yaml) |
| [`tradfri-binding-backup/`](./tradfri-binding-backup/) | **Heal IKEA ZHA Bindings** *(paired self-healing script; requires ZHA Toolkit)* | `script` | [Thread #934393](https://community.home-assistant.io/t/zha-ikea-tradfri-on-off-switch-binding-backup-and-self-healing/934393) | [![Import](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Ftradfri-binding-backup%2Fheal_ikea_zha_bindings.yaml) |
| [`tradfri-shortcut-button/`](./tradfri-shortcut-button/) | **ZHA — IKEA Tradfri Shortcut Button (Firmware ≥ 2.3.075)** *(Release)* | `automation` | [Thread #402565](https://community.home-assistant.io/t/zha-ikea-tradfri-shortcut-button-firmware-2-3-075-or-greater/402565) | [![Import](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Ftradfri-shortcut-button%2Fzha-ikea-tradfri-shortcut-button-firmware-2-3-075-or-greater.yaml) |
| [`tradfri-shortcut-button/`](./tradfri-shortcut-button/) | **BETA ZHA — IKEA Tradfri Shortcut Button** *(Beta)* | `automation` | [Thread #587663](https://community.home-assistant.io/t/beta-testing-zha-ikea-tradfri-shortcut-button-firmware-2-3-075-or-greater/587663) | [![Import](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Ftradfri-shortcut-button%2Fbeta-zha-ikea-tradfri-shortcut-button.yaml) |
| [`toggle-scene/`](./toggle-scene/) | **Toggle Scenes (Toggle Between Scene & Pre-Scene State)** | `automation` | [Thread #493484](https://community.home-assistant.io/t/toggle-between-a-scene-and-the-pre-scene-state/493484) | [![Import](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Ftoggle-scene%2Ftoggle-scene.yaml) |
| [`bayesian-probability-sensor/`](./bayesian-probability-sensor/) | **Numeric Probability from a Bayesian Sensor** | `template` | [Core PR #130376](https://github.com/home-assistant/core/pull/130376) | [![Import](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Fbayesian-probability-sensor%2Fbayesian_probability_sensor.yaml) |

---

## Standalone Scripts, Automations & Templates

| Folder | File | Type | Forum Thread |
|---|---|---|---|
| [`roborock-cleaning/`](./roborock-cleaning/) | [`roborock_clean_script.yaml`](./roborock-cleaning/roborock_clean_script.yaml) | `script` | [My Robovac Roborock Q5 Pro Cleaning Automation and script (#896307)](https://community.home-assistant.io/t/my-robovac-roborock-q5-pro-cleaning-automation-and-script/896307) |
| [`tailscale-phone-vpn/`](./tailscale-phone-vpn/) | [`tailscale_away_from_home_automation.yaml`](./tailscale-phone-vpn/tailscale_away_from_home_automation.yaml) | `automation` | [Automate Tailscale connection with home assistant (#576826)](https://community.home-assistant.io/t/automate-tailscale-connection-with-home-assistant/576826) |
| [`circadian-lighting/`](./circadian-lighting/) | [`sun-color-temp-template.yaml`](./circadian-lighting/sun-color-temp-template.yaml) | `template` | [Template entity to guess the outside colour temperature (#402510)](https://community.home-assistant.io/t/template-entity-to-guess-the-outside-colour-temperature/402510) |

---

## License

Copyright © [HarvsG](https://github.com/HarvsG).

This repository is licensed under the **[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)](./LICENSE)**:
- **Attribution (`BY`)** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial (`NC`)** — You may **not** use the material for commercial purposes or monetary profit.
- **ShareAlike (`SA`)** — If you remix, transform, or build upon the material, you must distribute your contributions under the **same license** as the original.
