# Circadian Lighting — Match Outside Colour Temperature

Automatically updates the colour temperature of your lights to match outside daylight based on `sun.sun` elevation — cool daylight during the day, warming gradually around sunset and overnight.

- **Forum Discussion (Blueprint)**: [Automatic circadian lighting - match your lights' color temperature to the sun!](https://community.home-assistant.io/t/automatic-circadian-lighting-match-your-lights-color-temperature-to-the-sun/472105)
- **Forum Discussion (Template Formula)**: [Template entity to guess the outside colour temperature](https://community.home-assistant.io/t/template-entity-to-guess-the-outside-colour-temperature/402510)

---

## Files in This Folder

### 1. [`match-color-temp-kelvin.yaml`](./match-color-temp-kelvin.yaml) *(Recommended — HA 2022.10+)*

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Fcircadian-lighting%2Fmatch-color-temp-kelvin.yaml)

Uses `color_temp_kelvin` (compatible with Home Assistant 2026.1+ after `kelvin` deprecation) and Kelvin `color_temp` sliders (`1500K`–`7000K`). Triggers when any targeted light turns on, when `sun.sun` elevation changes, and every 5 minutes.

### 2. [`match-color-temp-mireds.yaml`](./match-color-temp-mireds.yaml) *(Legacy — Pre-2022.9 Mireds)*

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Fcircadian-lighting%2Fmatch-color-temp-mireds.yaml)

Legacy Mireds (`color_temp`) version preserved for historical reference and older Home Assistant installations.

### 3. [`sun-color-temp-template.yaml`](./sun-color-temp-template.yaml) *(Standalone Template Sensor)*

Standalone `template` sensor (`sensor.sun_colour_temp`) exposing the calculated outside colour temperature derived from `sun.sun` elevation.

For Kelvin output instead of Mireds, adjust `2200` and `4000` to your bulbs' range:

```jinja2
{{ [ [ (4791.67 - 3290.66/(1 + 0.222 * [ [ 0, state_attr('sun.sun', 'elevation') ] | max, 90 ] | min**0.81)) | int, 2200 ] | max, 4000 ] | min }}
```

---

## Requirements & Notes

1. **Working `sun.sun` integration** (enabled by default in Home Assistant).
2. **Colour-temperature capable bulbs** reporting `color_temp` in `attributes.supported_color_modes`.
3. **Brightness restoration**: On some Zigbee bulbs (e.g. IKEA Tradfri via ZHA), setting colour temperature as a bulb turns on can interrupt turn-on brightness. A configurable `brightness_action` runs 500ms later to restore brightness.
4. **Light groups**: Avoid targeting a light group if you turn on individual lamps in that room — calling `light.turn_on` on a group turns on every member of the group. (For multi-bulb ceiling fixtures, targeting the group can be desirable.)
