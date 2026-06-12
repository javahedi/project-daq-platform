
# Quantum DAQ Platform

A configurable data acquisition and monitoring platform designed for BeagleBone Black, Linux, C++, Python, REST APIs, WebSockets, and real-time sensor visualization.

## Current Version

Version: `v0.1-python-daq-dashboard`

This milestone implements a complete Python-based DAQ backend with simulated sensors, storage, REST API, WebSocket live streaming, and a browser dashboard.

## Architecture

```text
config.yaml
    ↓
Sensor Factory
    ↓
Sensor Simulators
    ↓
Acquisition Engines
    ↓
Broadcast Message Bus
    ├── Storage Worker → SQLite
    └── WebSocket Stream → Dashboard
````

## Features

* Configurable sensors using YAML
* Temperature and pressure simulators
* Multi-sensor acquisition
* Threaded acquisition engines
* Broadcast message bus
* SQLite data storage
* REST API using FastAPI
* WebSocket live sample streaming
* Live browser dashboard using ECharts
* Sensor-specific live streams
* Sensor statistics endpoint
* Logging to console and file

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the DAQ platform and API:

```bash
python run.py
```

Open dashboard:

```text
http://127.0.0.1:8000/dashboard
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

## Useful API Endpoints

```text
GET /status
GET /samples/count
GET /samples/latest
GET /samples/recent
GET /sensors
GET /sensors/details
GET /sensors/{sensor_id}/samples
GET /sensors/{sensor_id}/statistics
```

## WebSocket Endpoints

```text
/ws/samples
/ws/samples/{sensor_id}
/ws/statistics/{sensor_id}
```

## Example Sensor Configuration

```yaml
sensors:
  - sensor_id: TEMP_001
    type: temperature
    location: LAB_001
    sample_rate_hz: 5

  - sensor_id: TEMP_002
    type: temperature
    location: LAB_002
    sample_rate_hz: 2

  - sensor_id: PRESS_001
    type: pressure
    location: LAB_001
    sample_rate_hz: 1
```

