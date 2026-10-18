# MTTL-W01 2.0 Home Assistant Card

[한국어](README.md) | English

A Lovelace card for standalone firmware 2.0.x. It retains the entity mapping and features of the backend 1.0.68 card, with separate 2.0 file and registration names. The card version does not need to match each firmware patch release.

![Home Assistant card](HA_card.png)

## Installation

1. Copy [mttl-w01-2.0-card.js](mttl-w01-2.0-card.js) to Home Assistant's `/config/www/`.
2. Under **Settings → Dashboards → Resources**, add `/local/mttl-w01-2.0-card.js` as a **JavaScript Module**. Enable advanced mode in your user profile if the resource menu is hidden.
3. Refresh the browser and add a card.

```yaml
type: custom:mttl-w01-2-0-card
mac: 97c0123
mobile_two_rows: true
```

- `mac`: Last seven hexadecimal characters of the device MAC. Separators and case are normalized.
- `name`: Optional title; defaults to `MTTL XXXXXXX`.
- `mobile_two_rows`: Keep channels in a 2×2 layout on mobile when `true`. Default: one mobile column.
- `channel_names`, `channel_icons`: Arrays for four channel names/icons, also configurable in the visual editor.

Displays total power/energy/voltage/current and per-channel power/energy/current/temperature. Tap a channel header to toggle power or a sensor row to open more-info. Top sensors use a three-plus-two layout on mobile.

Enable MQTT in the device web UI first to create HA Discovery entities. Default entity IDs are required, for example `switch.mttl_97c0123_sw1` and `sensor.mttl_97c0123_current1`. Manually renamed entity IDs will not map automatically.

When migrating from the old card, update both the resource URL and YAML `type`. Continuing to use the existing 1.0.68 card is also supported.

## Remaining time and timer settings (2.0.15)

Each channel shows a single `Timer` row.

- Displays `sensor.mttl_<last 7 MAC digits>_timer_remaining1` through `timer_remaining4` as `HH:MM:SS`, updating about every five seconds while running. With firmware 2.0.16 or later, OFF channels show their configured duration, or `00:00:00` when disabled. Firmware 2.0.15 shows `00:00:00` when idle, expired or cancelled. The card does not simulate a countdown. No card JS replacement is required for this firmware change.
- Tap the row to open HA's native more-info dialog for the matching `number.mttl_<last 7 MAC digits>_timer1` through `timer4`. View and set the configured **0..1440 minutes** there; zero disables the timer.
- A missing, unknown or unavailable remaining-time sensor displays `—`. The row is enabled whenever the matching number is available, so settings remain accessible independently of the sensor state.
- Requires firmware with timer Discovery and default entity IDs. A schedule-owned channel rejects nonzero timer settings and keeps its configured timer at zero.

Replace the JS and update the existing resource URL to `/local/mttl-w01-2.0-card.js?v=2.0.15-timer-label`, then refresh. Keep the existing YAML `type` and `mac`. Firmware files are unchanged.
