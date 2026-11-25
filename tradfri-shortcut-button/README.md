# ZHA IKEA Tradfri Shortcut Button (Firmware ≥ 2.3.075)

Control anything in Home Assistant using an **IKEA Tradfri Shortcut Button** paired via **ZHA** running firmware **2.3.075 or newer** (which introduced native double-press `off` events and eliminated duplicate button press messages).

- **Forum Discussion (Release)**: [ZHA IKEA Tradfri Shortcut button firmware 2.3.075 or greater](https://community.home-assistant.io/t/zha-ikea-tradfri-shortcut-button-firmware-2-3-075-or-greater/402565)
- **Forum Discussion (Beta)**: [BETA TESTING - ZHA IKEA Tradfri Shortcut button firmware 2.3.075 or greater](https://community.home-assistant.io/t/beta-testing-zha-ikea-tradfri-shortcut-button-firmware-2-3-075-or-greater/587663)

---

## Files in This Folder

### 1. [`zha-ikea-tradfri-shortcut-button-firmware-2-3-075-or-greater.yaml`](./zha-ikea-tradfri-shortcut-button-firmware-2-3-075-or-greater.yaml) *(Release Blueprint)*

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Ftradfri-shortcut-button%2Fzha-ikea-tradfri-shortcut-button-firmware-2-3-075-or-greater.yaml)

Supports **Single click**, **Double click**, **Long click**, **Release Long Click**, and configurable **Automation Mode** (`single`, `restart`, `queued`, `parallel`), filtering ZHA triggers strictly to clusters `6` and `8` so device check-ins never clutter traces.

### 2. [`beta-zha-ikea-tradfri-shortcut-button.yaml`](./beta-zha-ikea-tradfri-shortcut-button.yaml) *(Beta Blueprint)*

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Ftradfri-shortcut-button%2Fbeta-zha-ikea-tradfri-shortcut-button.yaml)

Staging blueprint used to test new features before promoting them into the release blueprint.

---

## Checking Your Shortcut Button Firmware Version in ZHA

1. Open the **Device** page for your Shortcut Button in Home Assistant.
2. Click the three-dots menu next to **Reconfigure** → **Manage Zigbee device**.
3. Under **Clusters**, select `Basic (Endpoint id: 1, Id: 0x0000, Type: in)`.
4. Under **Cluster Attributes**, select `sw_build_id (id: 0x4000)`.
5. Click **Read Attribute** while waking the button with a press — the firmware version appears in **Value**.

---

## Example: Hold-to-Dim Until Button Release

Using `automation_mode: restart`, releasing the button triggers a new run (with an empty `button_release` sequence) that cleanly interrupts the `repeat` dimming loop:

```yaml
alias: "[ZHA] Shortcut Button - Study"
description: ""
use_blueprint:
  path: HarvsG/zha-ikea-tradfri-shortcut-button-firmware-2-3-075-or-greater.yaml
  input:
    shortcut_button: cf69732507e91ead4a2f4c7ffae3e7b5
    button_short:
      - service: light.toggle
        target:
          entity_id: light.study_light
    button_double:
      - service: light.toggle
        target:
          entity_id: light.study_lamp
    button_long:
      - repeat:
          while:
            - condition: numeric_state
              entity_id: light.study_lamp
              below: 256
              above: 3
              attribute: brightness
          sequence:
            - service: light.turn_on
              data:
                brightness_step_pct: -1
              target:
                entity_id: light.study_lamp
    button_release: []
    automation_mode: restart
```
