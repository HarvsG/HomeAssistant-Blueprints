# Roborock Q5 Pro Smart Cleaning Script

A Home Assistant `script` for Roborock vacuums with non-lifting mops (such as the **Roborock Q5 Pro**) that automatically selects between separate **Mop** and **Vacuum** floor maps, checks household conditions, and resolves targeted room names dynamically to segment IDs via `roborock.get_maps`.

- **Forum Discussion**: [My Robovac Roborock Q5 Pro Cleaning Automation and script](https://community.home-assistant.io/t/my-robovac-roborock-q5-pro-cleaning-automation-and-script/896307)

---

## Script

### [`roborock_clean_script.yaml`](./roborock_clean_script.yaml)

### What It Does

1. **Pre-flight checks**: Ensures `input_boolean.manual_mode` is off, the vacuum is docked, `binary_sensor.everyone_sleeping` is off, current time is within sociable hours (`08:00`–`21:40`), and `input_boolean.guest_mode` is off (sending mobile notifications if skipped due to guests).
2. **Automatic Mop vs. Vacuum map switching**: Checks `binary_sensor.q5_pro_water_box_attached` and selects either `Home Mop` (with carpeted rooms/rugs blocked by invisible walls/no-go zones) or `Home Vacuum`.
3. **Dynamic room-to-segment resolution**: Accepts an optional `rooms` field (`area` selector). Queries `roborock.get_maps` so room names match the active map's segment IDs automatically (even when segment IDs differ between maps), normalising room aliases (e.g. mapping `Kitchen` → `Living Room`). If no rooms are passed, runs a full-map clean.
4. **Completion notification**: Waits for cleaning to finish and sends a status notification.

> **Adapting to your setup**: Replace the device IDs, entity IDs (`vacuum.q5_pro`, `select.q5_pro_selected_map`, `notify.mobile_app_*`, `input_boolean.*`), and `room_map` dictionary in [`roborock_clean_script.yaml`](./roborock_clean_script.yaml) to match your Home Assistant entities and Roborock map/room names.
