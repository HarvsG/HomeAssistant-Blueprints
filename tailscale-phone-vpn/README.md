# Automate Tailscale Connection on Android with Home Assistant

A Home Assistant `automation` that automatically connects **Tailscale VPN** on an Android phone when leaving home Wi-Fi and disconnects it upon returning home, using Home Assistant Companion App broadcast intents.

- **Forum Discussion**: [Automate Tailscale connection with home assistant](https://community.home-assistant.io/t/automate-tailscale-connection-with-home-assistant/576826)

---

## Automation

### [`tailscale_away_from_home_automation.yaml`](./tailscale_away_from_home_automation.yaml)

### How It Works

- **Leaving home (`to: not_home`)**: Sends `command_launch_app` (`package_name: com.tailscale.ipn`) to ensure Tailscale is running, followed by `command_broadcast_intent` (`com.tailscale.ipn.CONNECT_VPN`).
- **Arriving home (`from: not_home` → `to: home`)**: Sends `com.tailscale.ipn.DISCONNECT_VPN` twice (5 seconds apart) to reliably disconnect the VPN.

### Adapting to Your Device

Replace `device_tracker.pixel_3a` and `notify.mobile_app_pixel_3a` with your own phone's tracker and Companion App notification service, and grant the Home Assistant Companion App permission to send background intents / launch apps on Android.
