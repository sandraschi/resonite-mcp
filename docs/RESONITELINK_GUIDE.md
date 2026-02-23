# ResoniteLink Technical Guide

ResoniteLink is a high-performance, real-time WebSocket JSON protocol for interacting with Resonite worlds. It provides a more robust and lower-latency alternative to OSC for complex data model manipulation.

## Overview

Unlike OSC, which sends individual packets, ResoniteLink maintains a persistent state-aware connection. It allows you to:
- **Spawn objects** using template URLs.
- **Set component values** directly by unique ID.
- **Get component values** asynchronously with reliable delivery.

## Getting Started

### 1. Prerequisites
- Resonite client running.
- **ResoniteLink Mod** installed in Resonite (requires [ResoniteModLoader](https://github.com/resonite-modding-group/ResoniteModLoader)).
- Default ResoniteLink port: **4242**.

### 2. Connection
First, establish a connection to the ResoniteLink server:

```python
await resonite_link_connect(host="localhost", port=4242)
```

## Available Tools

### `resonite_link_spawn`
Spawns an object from the Resonite inventory or a public URL.

```python
await resonite_link_spawn(
    template_url="resonite:///items/ExampleCube.7pb",
    position={"x": 5.0, "y": 1.0, "z": 0.0}
)
```

### `resonite_link_set`
Sets a field on a specific component using its unique ID.

```python
await resonite_link_set(
    component_id="ID_OF_THE_COMPONENT",
    field="Color",
    value=[1.0, 0.0, 0.0, 1.0] # Red RGBA
)
```

### `resonite_link_get`
Requests the current value of a component field.

```python
await resonite_link_get(
    component_id="ID_OF_THE_COMPONENT",
    field="IsActive"
)
```

## Best Practices

1. **ID Management**: Capture component IDs during spawn or by using the Resonite inspector to target specific elements.
2. **Batching**: While ResoniteLink is fast, avoid spamming `set` commands in high-frequency loops (above 60Hz) to prevent network congestion.
3. **Template URLs**: Use standard `resonite:///` URIs for inventory items to ensure reliable spawning across different world instances.

---
**Note**: ResoniteLink is currently in Beta. Protocol changes may occur.
