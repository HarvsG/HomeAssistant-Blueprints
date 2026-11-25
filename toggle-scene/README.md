# Toggle Scenes — Toggle Between a Scene and Pre-Scene State

Allows you to toggle a Home Assistant `scene` on and off ("undoing" the scene) from a single button or trigger, with a configurable session timeout.

- **Forum Discussion**: [Toggle between a scene and the pre-scene state](https://community.home-assistant.io/t/toggle-between-a-scene-and-the-pre-scene-state/493484)

---

## Blueprint

### [`toggle-scene.yaml`](./toggle-scene.yaml)

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FHarvsG%2FHomeAssistant-Blueprints%2Fblob%2Fmain%2Ftoggle-scene%2Ftoggle-scene.yaml)

---

## How It Works

1. When triggered initially (or after the configurable `Timeout` has elapsed), the automation snapshots the current state of all entities in `scene.my_scene` into a dynamic scene `scene.my_scene_store_previous_state`, then activates `scene.my_scene`.
2. When triggered again within the timeout window, it activates `scene.my_scene_store_previous_state` to restore the pre-scene state.
3. Subsequent triggers alternate between the two scenes by comparing their last-activated timestamps. *(Note: dynamically created scenes reset across Home Assistant restarts, so the first trigger after a restart always activates `scene.my_scene`.)*

## Triggering It

Either call **`automation.trigger`** on the created automation (from a button, script, or another automation), or fire a `scene_toggle` event:

```yaml
event: scene_toggle
event_data:
  entity_id: scene.my_scene
```
