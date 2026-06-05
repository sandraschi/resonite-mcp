# vBot OSC receiver — build in Resonite (vBoomy / vMechazilla)

In-world ProtoFlux graph that listens on **Resonite OSC input port 9000** and drives a virtual robot root. Same contract as [teleoperator-mcp VBOOMY_OSC.md](https://github.com/sandraschi/teleoperator-mcp/blob/master/docs/resonite/VBOOMY_OSC.md).

## API (resonite-mcp)

| Endpoint | Purpose |
|----------|---------|
| `GET /api/resonite/vbot/types` | yahboom, mechazilla, bumi, custom |
| `GET /api/resonite/vbot/receiver?robot_id=&robot_type=` | Full build spec + test sequence |
| `POST /api/resonite/vbot/test?robot_id=&robot_type=` | Fire spawn/move/head/stop OSC |

Example:

```powershell
Invoke-RestMethod http://127.0.0.1:8787/api/resonite/vbot/receiver?robot_type=mechazilla
Invoke-RestMethod -Method Post "http://127.0.0.1:8787/api/resonite/vbot/test?robot_type=yahboom"
```

## Build the receiver (15 min)

### 1. Enable OSC

Resonite → Settings → OSC → **Input port 9000** (must match `ROBOTICS_OSC_PORT`).

### 2. World hierarchy

```
vBotRoot          CharacterController or Rigidbody + BoxCollider
├── BodyMesh      (Boomy, Mechazilla kitbash, whatever)
└── Head          empty slot + Camera (future LiveKit)
```

### 3. ProtoFlux on vBotRoot

Create float fields on the root:

| Field | Default | Source |
|-------|---------|--------|
| `LinearCmd` | 0 | OSC `/robot/{id}/move` arg0 |
| `AngularCmd` | 0 | OSC `/robot/{id}/move` arg1 |
| `HeadYawDeg` | 0 | OSC `/robot/{id}/head` arg0 |
| `HeadPitchDeg` | 0 | OSC `/robot/{id}/head` arg1 |
| `LastMoveTime` | 0 | Update when move received |

For each OSC address, add an **OSC Data Source** (or equivalent in your Resonite version):

1. **Spawn** — `/resonite/vbot/spawn`  
   When `robot_id` string matches your id: set Position (x,y,z), Scale, zero cmds.

2. **Move** — `/robot/vbot_yahboom_01/move`  
   `LinearCmd` ← float arg0, `AngularCmd` ← float arg1, refresh `LastMoveTime`.

3. **Stop / reset / estop** — zero `LinearCmd` and `AngularCmd`.

4. **Head** — drive `Head` slot local rotation from yaw/pitch degrees.

### 4. Locomotion integrator (Update)

Each frame:

```
if (TimeNow - LastMoveTime) < 0.15:
    velocity = Forward * LinearCmd + Turn * AngularCmd * turnRate
else:
    velocity = 0
Apply to CharacterController or Rigidbody
```

Holonomic wheeled bots: `linear` m/s forward, `angular` rad/s yaw.

### 5. Mechazilla variant

Register with robotics-mcp:

```json
{
  "robot_id": "vbot_mechazilla_01",
  "robot_type": "mechazilla",
  "platform": "resonite"
}
```

Same graph — swap mesh, set scale **2.5** on spawn. Teleop: add `VboomyAdapter`-style mapper later or reuse vboomy with `TELEOP_VBOOMY_ROBOT_ID=vbot_mechazilla_01`.

## Verify without Pico

```powershell
# From teleoperator-mcp
Set-Location D:\Dev\repos\teleoperator-mcp
.\scripts\test-vboomy-osc.ps1

# Or resonite-mcp HTTP
Invoke-RestMethod -Method Post "http://127.0.0.1:8787/api/resonite/vbot/test"
```

Then start teleoperator `?robot=vboomy` for live WebXR drive.
