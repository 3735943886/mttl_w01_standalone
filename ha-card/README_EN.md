# MTTL-W01 2.0 Home Assistant Card

[한국어](README.md) | English

A Lovelace card for standalone firmware 2.0.x, displaying total/per-channel sensors and timers. The card version does not need to match each firmware patch release.

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

When migrating from the old card, update both the resource URL and YAML `type`.

## Remaining time and timer settings

Each channel shows a single `Timer` row.

- Displays `sensor.mttl_<last 7 MAC digits>_timer_remaining1` through `timer_remaining4` as `HH:MM:SS`, updating about every five seconds while running. With firmware 2.0.16 or later, OFF channels show their configured duration, or `00:00:00` when disabled. The card does not simulate a countdown.
- Tap the row to open HA's native more-info dialog for the matching `number.mttl_<last 7 MAC digits>_timer1` through `timer4`. View and set the configured **0–1440 minutes** there; zero disables the timer.
- A missing, unknown or unavailable remaining-time sensor displays `—`. The row is enabled whenever the matching number is available, so settings remain accessible independently of the sensor state.
- Requires firmware with timer Discovery and default entity IDs. A schedule-owned channel rejects nonzero timer settings and keeps its configured timer at zero.

If the old display remains after replacing the JS, add a version query to the resource URL and refresh, for example `/local/mttl-w01-2.0-card.js?v=timer`. Keep the existing YAML `type` and `mac`.
