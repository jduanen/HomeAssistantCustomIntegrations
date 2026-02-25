# HomeAssistantCustomIntegrations
Custom Integrations for Home Assistant

**WIP**

# ADSB Tracker

This integration polls my local ADS-B server (running dump1090-fa), gets back a list of ADS-B messages, creates new entities for new tracks, updates existing entities, and removes entities that are no longer valid.

## Installation

<how to install this custom integration>

## Configuration

```
adsb_tracker:
  host: "192.168.166.193"
  port: 8504
  path: "/data/aircraft.json"
```
