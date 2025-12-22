# 🔗 ProtoFlux: Resonite's Visual Programming System

**A comprehensive guide to ProtoFlux - Resonite's revolutionary node-based visual programming system that makes complex VR experiences accessible to everyone.**

---

## 📚 Table of Contents

1. [What is ProtoFlux?](#what-is-protoflux)
2. [Why ProtoFlux Matters](#why-protoflux-matters)
3. [Core Concepts](#core-concepts)
4. [Basic Components](#basic-components)
5. [Data Types & Flow](#data-types--flow)
6. [Common Patterns](#common-patterns)
7. [Advanced Features](#advanced-features)
8. [MCP Integration](#mcp-integration)
9. [Examples & Tutorials](#examples--tutorials)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)
12. [Resources](#resources)

---

## What is ProtoFlux?

ProtoFlux is Resonite's **visual programming system** that allows you to create interactive experiences, automate behaviors, and build complex logic without writing traditional code. Instead of typing lines of text, you connect visual "nodes" with "wires" to create programs.

### Key Characteristics:
- **Node-Based**: Drag-and-drop programming with visual nodes
- **Real-Time**: Changes take effect immediately while the world runs
- **Collaborative**: Multiple users can edit the same ProtoFlux logic simultaneously
- **Performance**: Optimized for VR environments with low latency
- **Extensible**: Supports custom nodes and complex data structures

### How It Works:
1. **Nodes** represent operations, values, or logic elements
2. **Wires** connect nodes to pass data and control flow
3. **Execution** happens automatically based on node connections
4. **Debugging** is visual - you can see data flowing through wires

---

## Why ProtoFlux Matters

### 🎯 Democratizes Programming

**Traditional Programming:**
```csharp
// Complex logic in text form
public class DoorController : MonoBehaviour {
    public float openAngle = 90f;
    public float speed = 2f;
    private bool isOpen = false;

    void Update() {
        if (Input.GetKeyDown(KeyCode.E)) {
            StartCoroutine(ToggleDoor());
        }
    }

    IEnumerator ToggleDoor() {
        float targetAngle = isOpen ? 0f : openAngle;
        float startAngle = transform.localEulerAngles.y;
        float time = 0;

        while (time < 1f) {
            time += Time.deltaTime * speed;
            float angle = Mathf.Lerp(startAngle, targetAngle, time);
            transform.localEulerAngles = new Vector3(0, angle, 0);
            yield return null;
        }
        isOpen = !isOpen;
    }
}
```

**ProtoFlux Equivalent:**
```
[Key Press E] → [Toggle Bool] → [Lerp Float] → [Set Rotation]
```

**The difference:** What takes 30+ lines of complex code in traditional programming becomes a simple 4-node visual flow in ProtoFlux.

### 🚀 Advantages Over Traditional Coding

| Aspect | Traditional Code | ProtoFlux |
|--------|------------------|-----------|
| **Learning Curve** | Steep - requires programming knowledge | Gentle - visual and intuitive |
| **Iteration Speed** | Edit → Compile → Test → Repeat | Edit → See results immediately |
| **Collaboration** | Code conflicts, merge issues | Real-time collaborative editing |
| **Debugging** | Breakpoints, logging, IDE required | Visual data flow inspection |
| **Maintenance** | Code can become complex and brittle | Visual logic is self-documenting |
| **Performance** | Manual optimization required | Built-in optimization |

### 🎮 Perfect for VR

ProtoFlux is specifically designed for VR environments:
- **Spatial Programming**: Nodes exist in 3D space around you
- **Multi-User Editing**: See other users' cursors while editing
- **Live Debugging**: Watch data flow through wires in real-time
- **Gesture-Based Editing**: Use VR controllers for intuitive interaction

---

## Core Concepts

### 🧩 Nodes

Nodes are the building blocks of ProtoFlux programs. Each node performs a specific function:

**Types of Nodes:**
- **Value Nodes**: Store and provide data (numbers, text, colors, etc.)
- **Operation Nodes**: Perform calculations, logic, or transformations
- **Flow Control Nodes**: Control program execution (if/then, loops, etc.)
- **Input/Output Nodes**: Interface with the world (buttons, triggers, etc.)
- **Utility Nodes**: Debugging, timing, and helper functions

### 🔗 Wires

Wires connect nodes and carry data between them:

**Wire Types:**
- **Data Wires** (usually blue/white): Carry values between nodes
- **Execution Wires** (usually yellow): Control when nodes execute
- **Reference Wires** (usually purple): Point to objects or components

**Wire Behavior:**
- Data flows from outputs (right side) to inputs (left side)
- Execution flows from outputs to inputs, triggering nodes
- Wires can branch and merge for complex logic

### 📦 Components

Components are reusable ProtoFlux programs that you can save and reuse:

- **ProtoFlux Components**: Self-contained logic units
- **Interface Components**: Define inputs/outputs for the component
- **Nested Components**: Components can contain other components

---

## Basic Components

### 🎛️ Essential Node Categories

#### 1. **Value Nodes**
Store and provide data of different types:

```
[Integer Value] - Whole numbers (-2,147,483,648 to 2,147,483,647)
[String Value] - Text data ("Hello World")
[Float Value] - Decimal numbers (3.14159)
[Bool Value] - True/False values
[Color Value] - RGBA color data
[Vector3 Value] - 3D position/rotation/scale
```

#### 2. **Math Operations**
Perform calculations:

```
[Add] - Addition of numbers
[Subtract] - Subtraction
[Multiply] - Multiplication
[Divide] - Division
[Modulo] - Remainder of division
[Power] - Exponentiation
[Square Root] - Square root calculation
[Absolute Value] - Remove negative sign
```

#### 3. **Logic Operations**
Make decisions and comparisons:

```
[Equal] - Check if values are equal
[Not Equal] - Check if values are different
[Greater Than] - Compare magnitudes
[Less Than] - Compare magnitudes
[And] - Both conditions must be true
[Or] - Either condition can be true
[Not] - Reverse true/false
```

#### 4. **Flow Control**
Control program execution:

```
[If] - Execute different paths based on condition
[Switch] - Choose from multiple options
[Sequence] - Execute nodes in order
[Delay] - Wait before continuing
[Loop] - Repeat execution
[Break] - Exit a loop early
```

#### 5. **Input/Output**
Interface with the world:

```
[Button Press] - Detect button interactions
[Trigger Enter] - Detect when objects enter a trigger zone
[Key Press] - Detect keyboard input
[Value Changed] - React to value changes
[Log] - Output debug information
```

---

## Data Types & Flow

### 📊 ProtoFlux Data Types

ProtoFlux uses a rich type system for different kinds of data:

| Type | Description | Example Use |
|------|-------------|-------------|
| **int** | 32-bit integer | Player count, item quantities |
| **float** | 32-bit floating point | Positions, scales, timers |
| **double** | 64-bit floating point | Precise calculations |
| **bool** | True/false | States, conditions |
| **string** | Text data | Names, messages |
| **char** | Single character | Key presses |
| **color** | RGBA color | Object colors, UI elements |
| **colorX** | HDR color | Lighting, special effects |
| **float2** | 2D vector | UV coordinates, screen positions |
| **float3** | 3D vector | Positions, directions, scales |
| **float4** | 4D vector | Rotations (quaternions), colors with alpha |
| **floatQ** | Quaternion | 3D rotations |
| **slot** | Object reference | Reference to scene objects |
| **user** | User reference | Reference to specific users |

### 🌊 Data Flow Principles

#### 1. **Pull vs Push**
- **Pull System**: Nodes request data when they need it
- **Push System**: Data is sent to nodes when it changes
- **Hybrid**: Most ProtoFlux uses pull, but some nodes push updates

#### 2. **Execution Flow**
```
Input Event → Process Data → Make Decisions → Execute Actions
```

#### 3. **Type Safety**
- Wires only connect compatible types
- Automatic type conversion when possible
- Clear visual feedback for type mismatches

---

## Common Patterns

### 🔄 Basic Patterns

#### 1. **Toggle System**
Create on/off switches:

```
[Button Press] → [Toggle Bool] → [If True/False] → [Enable/Disable Object]
```

#### 2. **Value Interpolation**
Smooth transitions between values:

```
[Start Value] → [Lerp] ← [End Value] ← [Progress 0-1] → [Set Property]
```

#### 3. **Timer System**
Time-based behaviors:

```
[Start Timer] → [Current Time] → [Subtract Start] → [Compare Duration] → [Trigger Event]
```

#### 4. **State Machine**
Manage different object states:

```
[Current State] → [Switch] → [State A Logic] | [State B Logic] | [State C Logic]
```

### 🎯 Advanced Patterns

#### 1. **Event-Driven Architecture**
Respond to world events:

```
[Player Join] → [Get Player Data] → [Update UI] → [Play Sound] → [Log Event]
```

#### 2. **Data Processing Pipeline**
Transform and process data:

```
[Raw Input] → [Validate] → [Transform] → [Filter] → [Output Result]
```

#### 3. **Recursive Structures**
Self-referencing logic:

```
[Input Data] → [Process] → [Check Complete] → [If Not Done] → [Process Again]
```

---

## Advanced Features

### 🔧 Advanced Node Types

#### 1. **Drivers**
Control object properties dynamically:

```
[Float Driver] - Animate float values over time
[Vector3 Driver] - Animate 3D transformations
[Color Driver] - Animate color changes
[Material Driver] - Change material properties
```

#### 2. **Constraints**
Maintain relationships between objects:

```
[Look At] - Object always faces a target
[Follow] - Object follows another object
[Distance Constraint] - Maintain distance between objects
[Rotation Constraint] - Constrain rotation ranges
```

#### 3. **Physics Integration**
Interact with the physics system:

```
[Apply Force] - Push objects with physics
[Get Velocity] - Read object movement
[Raycast] - Detect objects in a line
[Collision Detection] - React to collisions
```

#### 4. **Networking & Multi-User**
Handle multiple users:

```
[Get All Users] - List all users in session
[User Joined] - Detect new user connections
[Sync Variable] - Share data between users
[Authority Check] - Control who can modify what
```

### 🎨 Creative Applications

#### 1. **Interactive Art**
- Dynamic color changes based on user proximity
- Sound-reactive visual effects
- Physics-based particle systems

#### 2. **Game Mechanics**
- Custom physics behaviors
- Procedural content generation
- Complex AI behaviors

#### 3. **Social Features**
- Custom gesture systems
- Interactive furniture
- Collaborative drawing tools

#### 4. **Live Performances**
- Real-time lighting control
- Synchronized animations
- Interactive stage elements

---

## MCP Integration

### 🤖 Controlling ProtoFlux with MCP

The Resonite MCP server provides tools to interact with ProtoFlux programs:

#### Available MCP Tools:

```bash
# Execute ProtoFlux scripts
resonite_protoflux_execute(script_name, parameters)

# Monitor ProtoFlux performance
resonite_protoflux_analyze_script(script_name)

# Debug ProtoFlux execution
resonite_protoflux_debug_session(script_name, debug_mode)

# Optimize ProtoFlux performance
resonite_protoflux_optimize_script(script_name, optimization_level)

# Generate ProtoFlux documentation
resonite_protoflux_document_script(script_name)
```

#### Integration Examples:

**Execute a ProtoFlux Animation:**
```python
# Trigger a complex animation sequence
result = resonite_protoflux_execute("dance_sequence", {
    "speed": 1.5,
    "intensity": 0.8,
    "loop": True
})
```

**Debug ProtoFlux Logic:**
```python
# Start debugging session for a script
debug_info = resonite_protoflux_debug_session("door_controller", "step_through")
```

**Optimize Performance:**
```python
# Analyze and optimize a complex script
optimization = resonite_protoflux_optimize_script("particle_system", "moderate")
```

### 🔗 OSC Integration

ProtoFlux can be controlled via OSC from external applications:

**OSC Address Pattern:**
```
/avatar/parameters/ProtoFlux/[script_name]/[parameter_name]
```

**Example OSC Messages:**
```
/avatar/parameters/ProtoFlux/lighting/intensity 0.8
/avatar/parameters/ProtoFlux/camera/mode 1
/avatar/parameters/ProtoFlux/effect/enable 1
```

---

## Examples & Tutorials

### 📖 Basic Examples

#### Example 1: Interactive Door
**Goal:** Create a door that opens when you approach it

**ProtoFlux Setup:**
```
[Player Distance] → [Less Than 2.0] → [If True] → [Set Door Rotation to 90°]
                                                            → [Play Open Sound]
```

**Step-by-Step:**
1. Add a `Distance` node to measure player proximity
2. Connect to a `Less Than` comparison node
3. Use an `If` node to check the condition
4. Connect `True` output to rotation and sound nodes

#### Example 2: Color-Changing Object
**Goal:** Object changes color based on time of day

**ProtoFlux Setup:**
```
[World Time] → [Sin Wave] → [Map to Color Range] → [Set Material Color]
```

**Step-by-Step:**
1. Get current world time
2. Create smooth oscillation with sine wave
3. Map the value to a color gradient
4. Apply to object material

#### Example 3: Teleportation Pad
**Goal:** Teleport player to another location

**ProtoFlux Setup:**
```
[Trigger Enter] → [Get Teleport Target] → [Set Player Position] → [Play Effect]
```

**Step-by-Step:**
1. Detect when player steps on pad
2. Get target location coordinates
3. Move player to new position
4. Add particle effect or sound

### 🎮 Advanced Examples

#### Example 4: Rhythm Game
**Goal:** Create a rhythm-based interaction

**ProtoFlux Setup:**
```
[Audio Analysis] → [Beat Detection] → [Timing Check] → [Success/Failure] → [Score Update]
```

#### Example 5: Collaborative Drawing
**Goal:** Allow multiple users to draw together

**ProtoFlux Setup:**
```
[User Input] → [Validate Permission] → [Sync to Network] → [Apply to Canvas] → [Update All Users]
```

### 📚 Tutorial Series

#### Beginner Tutorials:
1. **Hello ProtoFlux** - Your first node connection
2. **Interactive Objects** - Making objects respond to players
3. **Simple Animations** - Basic movement and color changes
4. **User Interface** - Creating buttons and menus

#### Intermediate Tutorials:
1. **State Machines** - Managing complex object states
2. **Data Processing** - Working with lists and collections
3. **Multi-User Logic** - Handling multiple players
4. **Performance Optimization** - Making scripts run smoothly

#### Advanced Tutorials:
1. **Custom Components** - Building reusable logic
2. **Physics Integration** - Advanced physical interactions
3. **Network Synchronization** - Multi-user experiences
4. **OSC Integration** - External application control

---

## Best Practices

### 🎯 Design Principles

#### 1. **Keep It Simple**
- Start with basic functionality
- Add complexity gradually
- Avoid over-engineering

#### 2. **Organize Your Logic**
- Group related nodes together
- Use comments to explain complex sections
- Create sub-components for reusable logic

#### 3. **Performance Matters**
- Minimize unnecessary calculations
- Use efficient data types
- Cache frequently used values

#### 4. **Test Thoroughly**
- Test with multiple users
- Check edge cases
- Monitor performance impact

### 🔧 Technical Best Practices

#### Node Organization:
```
├── Input Section (left side)
├── Processing Logic (center)
├── Output Actions (right side)
└── Debug/Utility nodes (bottom)
```

#### Naming Conventions:
- Use descriptive names for important nodes
- Group related functionality
- Add comments for complex logic

#### Error Handling:
- Validate input data
- Provide fallback behaviors
- Log errors for debugging

#### Performance Tips:
- Avoid tight loops without delays
- Use event-driven logic when possible
- Minimize floating-point operations
- Cache object references

### 🤝 Collaboration Guidelines

#### Working with Others:
- Communicate changes you're making
- Use descriptive commit messages for ProtoFlux changes
- Test changes with collaborators before publishing
- Document complex logic for team members

#### Version Control:
- Save incremental versions of complex scripts
- Document what each version changes
- Keep backup copies of working versions

---

## Troubleshooting

### 🔍 Common Issues

#### 1. **Nodes Not Connecting**
**Problem:** Wires won't connect between nodes
**Solutions:**
- Check data types are compatible
- Ensure you're connecting output to input
- Try refreshing the ProtoFlux interface

#### 2. **Logic Not Executing**
**Problem:** ProtoFlux program doesn't run
**Solutions:**
- Check that input nodes are properly triggered
- Verify execution wires are connected
- Look for infinite loops or blocking operations

#### 3. **Performance Problems**
**Problem:** ProtoFlux causing lag or low framerate
**Solutions:**
- Reduce calculation frequency
- Optimize math operations
- Use more efficient node types
- Break complex logic into smaller components

#### 4. **Multi-User Sync Issues**
**Problem:** Logic behaves differently for different users
**Solutions:**
- Use proper networking nodes
- Check authority settings
- Ensure all users have the same ProtoFlux version

### 🐛 Debugging Techniques

#### Visual Debugging:
- Add `Log` nodes to output values
- Use `Debug Visualizer` nodes to see data
- Watch wire colors for data flow

#### Step-by-Step Debugging:
1. Isolate the problematic section
2. Add debug outputs at each step
3. Test with simple inputs first
4. Gradually increase complexity

#### Performance Profiling:
- Use the built-in profiler
- Monitor frame rate impact
- Identify bottleneck operations

---

## Resources

### 📚 Official Documentation

#### Resonite Documentation:
- [ProtoFlux Manual](https://wiki.resonite.com/ProtoFlux) - Official ProtoFlux documentation
- [ProtoFlux Tutorials](https://wiki.resonite.com/Category:ProtoFlux_Tutorials) - Step-by-step guides
- [Node Reference](https://wiki.resonite.com/Category:ProtoFlux_Nodes) - Complete node documentation

#### Community Resources:
- [Resonite Discord](https://discord.gg/resonite) - Active community support
- [ProtoFlux Showcase](https://www.youtube.com/results?search_query=resonite+protoflux) - YouTube tutorials
- [ProtoFlux Examples](https://github.com/resonite-community) - Community examples

### 🛠️ Development Tools

#### Built-in Tools:
- **ProtoFlux Debugger** - Step through execution
- **Performance Profiler** - Monitor resource usage
- **Node Browser** - Find and organize nodes
- **Component Library** - Save and reuse components

#### External Tools:
- **ProtoFlux Importer/Exporter** - Backup and share logic
- **ProtoFlux Minifier** - Optimize for performance
- **ProtoFlux Documenter** - Auto-generate documentation

### 🎓 Learning Paths

#### For Complete Beginners:
1. Watch "ProtoFlux Basics" video series
2. Complete "Hello ProtoFlux" tutorial
3. Build simple interactive objects
4. Join community Discord for questions

#### For Programmers:
1. Learn ProtoFlux node equivalents to code concepts
2. Study advanced patterns and data flow
3. Explore multi-user and networking features
4. Create complex systems and games

#### For Artists/Content Creators:
1. Focus on visual and interactive elements
2. Learn animation and material control
3. Study user experience patterns
4. Create engaging social experiences

### 🌟 Showcase Examples

#### Notable ProtoFlux Creations:
- **Complex Ragdoll Systems** - Realistic physics simulations
- **Procedural Cities** - Generated urban environments
- **Interactive Music Visualizers** - Real-time audio reactive art
- **Collaborative Whiteboards** - Multi-user drawing tools
- **Advanced Avatar Controllers** - Complex animation systems

---

## 🎮 ProtoFlux in Action

ProtoFlux represents a fundamental shift in how we think about programming in VR. Instead of abstracting the world into code, ProtoFlux lets you **directly manipulate the world around you** using intuitive visual tools.

**The future of programming isn't lines of text—it's visual, spatial, and collaborative.**

Whether you're creating simple interactive objects or building complex virtual worlds, ProtoFlux gives you the power to bring your imagination to life in Resonite. 🚀✨

**For practical script examples and implementations, see the [Useful ProtoFlux Scripts Guide](./USEFUL_PROTOFLUX_SCRIPTS.md).**

---

*This guide covers ProtoFlux as of Resonite 2025.1. Check the official wiki for the latest updates and new features.*
