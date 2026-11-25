# Bayesian Numeric Probability Sensor

A `template` sensor blueprint that exposes the numeric `probability` attribute (`0.0`–`1.0`) of a [Bayesian](https://www.home-assistant.io/integrations/bayesian/) `binary_sensor` as its own standalone `sensor` entity — useful for graphing probability history over time or triggering different automations at different probability thresholds.

- **Related Core PR**: [`home-assistant/core#130376`](https://github.com/home-assistant/core/pull/130376)

---

## Blueprint

### [`bayesian_probability_sensor.yaml`](./bayesian_probability_sensor.yaml) *(Domain: `template`)*

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Fbayesian-probability-sensor%2Fbayesian_probability_sensor.yaml)

> **Home Assistant `template` blueprint notes:**
> 1. You must have at least one **Template** helper (UI or `template:` in `configuration.yaml`) loaded in Home Assistant before clicking **Import Blueprint** — otherwise HA hasn't registered the `template` blueprint domain yet and returns `Unsupported domain`.
> 2. Once imported (to `/config/blueprints/template/HarvsG/bayesian_probability_sensor.yaml`), `template` blueprints do not appear in the **Settings → Automations & scenes → Blueprints** UI (which only lists `automation` and `script` domains); instantiate it in `configuration.yaml` below.

---

## Usage

After importing the blueprint, configure a template sensor in `configuration.yaml` (or via UI Template Blueprints where supported):

```yaml
template:
  - use_blueprint:
      path: HarvsG/bayesian_probability_sensor.yaml
      input:
        original_entity: binary_sensor.my_bayesian_sensor
    name: My Bayesian Probability
    unique_id: my_bayesian_probability
```

> **Version history**: Git history preserves both the initial November 2024 version (`bayesian_binary_sensor` input) and the June 2025 v2 update (`original_entity` input).
