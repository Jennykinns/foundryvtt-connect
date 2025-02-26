# Foundry VTT Integration for Home Assistant

This integration allows you to receive data from your Foundry Virtual Tabletop games in Home Assistant.

## Features

- Track character stats like HP and AC
- Monitor combat status and turns
- Create automations based on game events
- Use smart home devices to enhance your tabletop experience

## Installation

### HACS (Home Assistant Community Store)

1. Make sure [HACS](https://hacs.xyz/) is installed
2. Go to HACS > Integrations
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add the URL of this repository
6. Select "Integration" as the category
7. Click "ADD"
8. Search for "Foundry VTT" and install it

### Manual Installation

1. Copy the `custom_components/foundry_vtt` directory to your Home Assistant `config/custom_components` directory
2. Restart Home Assistant
3. Go to Settings > Devices & Services > Add Integration
4. Search for "Foundry VTT" and set it up

## Configuration

1. After installing the integration, add it through the Home Assistant UI
2. A webhook URL will be provided during setup
3. In Foundry VTT, install the "Home Assistant Connect" module
4. Enter the webhook URL in the module settings
5. Check "Enable Home Assistant Integration"

## Automations

### Example: Flash Lights When Combat Starts

```yaml
automation:
  - alias: "Combat Alert Lights"
    trigger:
      - platform: state
        entity_id: sensor.foundry_vtt_combat_status
        to: "In Combat"
    action:
      - service: light.turn_on
        target:
          entity_id: light.game_room
        data:
          effect: flash
          brightness_pct: 100
          rgb_color: [255, 0, 0]
```

### Example: Notification When Character is Low on HP

```yaml
automation:
  - alias: "Low HP Warning"
    trigger:
      - platform: template
        value_template: >
          {% set hp = states('sensor.foundry_vtt_current_hp') | int %}
          {% set max_hp = states('sensor.foundry_vtt_max_hp') | int %}
          {% if max_hp > 0 %}
            {{ (hp / max_hp) < 0.25 }}
          {% else %}
            false
          {% endif %}
    condition:
      - condition: template
        value_template: "{{ states('sensor.foundry_vtt_combat_status') != 'No Combat' }}"
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Low HP Warning!"
          message: "Your character is below 25% health!"
```

## Lovelace UI Examples

### Game Status Card

```yaml
type: entities
title: Foundry VTT Game Status
entities:
  - entity: sensor.foundry_vtt_combat_status
  - entity: sensor.foundry_vtt_current_turn
  - type: custom:bar-card
    entity: sensor.foundry_vtt_current_hp
    title: HP
    severity:
      - color: '#ff0000'
        value: 25
      - color: '#ffff00'
        value: 50
      - color: '#00ff00'
        value: 100
    max: sensor.foundry_vtt_max_hp
  - entity: sensor.foundry_vtt_armor_class
```

## Troubleshooting

- Check that the Home Assistant URL and webhook ID in Foundry VTT module settings are correct
- Verify that your Home Assistant instance is reachable from the server running Foundry VTT
- Look at Home Assistant logs for any webhook errors

## Support

For issues, feature requests, or questions, please [open an issue](https://github.com/yourusername/home-assistant-connect/issues) on GitHub.