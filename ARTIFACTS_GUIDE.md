# 🎨 Resonite Artifacts: Import, Export & Creation Guide

**Complete guide to creating, importing, exporting, and controlling 3D artifacts in Resonite - from VRM avatars to Gaussian splats and everything in between.**

---

## 📚 Table of Contents

1. [Artifact Types in Resonite](#artifact-types-in-resonite)
2. [Import Procedures](#import-procedures)
3. [Export Procedures](#export-procedures)
4. [VRM Avatar Import](#vrm-avatar-import)
5. [3D Mesh Import](#3d-mesh-import)
6. [Gaussian Splat Import](#gaussian-splat-import)
7. [Creating Artifacts](#creating-artifacts)
8. [Controlling Artifacts](#controlling-artifacts)
9. [MCP Integration](#mcp-integration)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)
12. [Advanced Techniques](#advanced-techniques)

---

## Artifact Types in Resonite

### 🎭 Avatars
- **VRM Format**: Standard avatar format (.vrm files)
- **Resonite Native**: Optimized avatar format
- **Custom Parameters**: Blend shapes, physics, IK rigging

### 🏗️ 3D Models & Meshes
- **OBJ Format**: Simple geometry (.obj + .mtl)
- **FBX Format**: Complex animations and materials (.fbx)
- **GLTF/GLB**: Modern web-friendly format (.gltf/.glb)
- **PLY Format**: Point cloud data (.ply)

### 🎯 Gaussian Splats
- **PLY Splats**: 3D Gaussian representations (.ply)
- **Resonite Optimized**: Performance-tuned splat format
- **Collider Meshes**: Physics representation (.obj/.fbx)

### 🎵 Audio & Media
- **Audio Files**: WAV, MP3, OGG formats
- **Video Files**: MP4, WebM formats
- **Textures**: PNG, JPG, TGA, EXR formats

### 📦 Other Assets
- **ProtoFlux Components**: Reusable logic (.protoflux)
- **Materials**: Shader configurations
- **Particle Systems**: Effect templates
- **UI Components**: Interface elements

---

## Import Procedures

### 🛠️ General Import Workflow

#### Method 1: File Drop (Simplest)
1. **Locate your file** on your computer
2. **Drag and drop** the file into Resonite
3. **Wait for processing** (progress bar appears)
4. **Position and configure** the imported object

#### Method 2: Inventory Import
1. **Open Inventory** (I key or Dash → Inventory)
2. **Click "Import"** button
3. **Browse and select** your file
4. **Choose import options** (scale, materials, etc.)
5. **Confirm import**

#### Method 3: World Import
1. **Open Create menu** (B key)
2. **Select "Import"** section
3. **Browse for file**
4. **Import directly into world**

### ⚙️ Import Settings

#### Scale & Units
- **Auto Scale**: Let Resonite detect appropriate size
- **Manual Scale**: Set specific scale factor
- **Unit Conversion**: Match source software units

#### Materials & Textures
- **Import Materials**: Include material definitions
- **Embed Textures**: Bundle textures in asset
- **Compress Textures**: Reduce file size
- **Mipmap Generation**: Automatic LOD textures

#### Animation & Rigging
- **Import Animations**: Include animation data
- **Bone Constraints**: IK rigging setup
- **Blend Shapes**: Facial animation support
- **Physics**: Collision and physics setup

---

## Export Procedures

### 📤 Exporting from Resonite

#### Method 1: Object Export
1. **Select object** in world
2. **Right-click** → "Export"
3. **Choose format** (OBJ, FBX, GLTF, etc.)
4. **Configure export options**
5. **Save to file**

#### Method 2: Batch Export
1. **Open Inventory**
2. **Select multiple items**
3. **Click "Export Selected"**
4. **Choose export format**
5. **Batch export to folder**

### 🎛️ Export Options

#### Geometry Export
- **Format**: OBJ, FBX, GLTF, PLY
- **Include Materials**: Export material data
- **Embed Textures**: Bundle textures in file
- **LOD Levels**: Multiple detail levels
- **Vertex Colors**: Include vertex painting

#### Animation Export
- **Bake Animations**: Convert to keyframe animation
- **Include Constraints**: Export IK and physics
- **Optimize Keyframes**: Reduce animation size
- **Loop Settings**: Animation loop configuration

### 🌐 External Software Export

#### Blender Export
```python
# Recommended FBX export settings
 bpy.ops.export_scene.fbx(
     filepath="model.fbx",
     use_selection=True,
     bake_anim_use_all_actions=False,
     bake_anim_simplify_factor=1.0,
     use_mesh_modifiers=True,
     mesh_smooth_type='EDGE',
     use_tspace=True
 )
```

#### Unity Export
- Use FBX Exporter package
- Configure for Resonite compatibility
- Export with materials and animations

#### Other Tools
- **Maya**: FBX 2020+ compatibility
- **3ds Max**: FBX export with proper transforms
- **Cinema 4D**: GLTF/GLB export recommended

---

## VRM Avatar Import

### 📥 VRM Import Process

#### Step 1: Prepare Your VRM
1. **Create VRM** in software like VRoid Studio, Blender, or Unity
2. **Ensure VRM 1.0** specification compliance
3. **Test in VRM viewer** before importing

#### Step 2: Import to Resonite
1. **Drag VRM file** into Resonite
2. **Wait for processing** (may take time for complex avatars)
3. **Configure avatar settings**:
   - **Scale**: Adjust to comfortable size
   - **Eye Tracking**: Enable/disable
   - **Viseme**: Lip sync setup
   - **IK**: Inverse kinematics

#### Step 3: Configure Parameters
1. **Open Avatar menu** (usually ESC → Avatar)
2. **Map parameters** to VRM blend shapes
3. **Test animations** in mirror or with gestures
4. **Save avatar configuration**

### 🎭 VRM Features in Resonite

#### Blend Shapes
- **Facial Expressions**: Eye blinks, mouth shapes
- **Body Morphs**: Muscle flex, breathing
- **Custom Parameters**: User-defined controls

#### IK Rigging
- **Full Body IK**: Natural pose control
- **Finger Tracking**: Individual finger control
- **Spine IK**: Torso bending and twisting

#### Physics Integration
- **Cloth Simulation**: Clothing physics
- **Hair Dynamics**: Hair movement
- **Accessory Physics**: Moving parts

### 🔧 VRM Optimization

#### Performance Tips
- **Triangle Count**: Keep under 32K triangles
- **Texture Size**: Use 512x512 or 1024x1024
- **Material Count**: Limit to 4-8 materials
- **Blend Shape Limit**: Under 100 shapes

#### Compatibility Issues
- **VRM 0.x**: May need conversion to 1.0
- **Custom Shaders**: May not import correctly
- **Complex Rigs**: Simplify if possible

---

## 3D Mesh Import

### 📦 Supported Formats

#### OBJ Format
```obj
# Simple OBJ file structure
v 1.0 0.0 0.0
v 0.0 1.0 0.0
v 0.0 0.0 1.0
f 1 2 3
```

**Pros**: Simple, widely supported
**Cons**: No animation, basic materials

#### FBX Format
- **Version**: FBX 2014-2020 recommended
- **Features**: Animation, materials, textures
- **Compatibility**: Best for complex models

#### GLTF/GLB Format
- **Modern**: Web-optimized format
- **Features**: PBR materials, animations, skins
- **Size**: GLB is binary (smaller), GLTF is JSON

### 🔄 Import Pipeline

#### Step 1: Pre-Processing
1. **Clean geometry** in source software
2. **Apply transforms** (freeze transformations)
3. **Optimize topology** (remove unnecessary vertices)
4. **UV unwrap** properly

#### Step 2: Material Setup
1. **Use PBR materials** when possible
2. **Embed textures** or provide separate files
3. **Set up UV coordinates** correctly
4. **Test material preview**

#### Step 3: Import & Test
1. **Import to Resonite**
2. **Check scale and position**
3. **Test materials and lighting**
4. **Verify animations if present**

### 🛠️ Mesh Optimization

#### Geometry Optimization
- **Decimation**: Reduce polygon count
- **LOD Creation**: Multiple detail levels
- **Occlusion Culling**: Hide unseen geometry

#### Texture Optimization
- **Resolution**: Balance quality vs performance
- **Compression**: Use appropriate formats
- **Atlas Packing**: Combine textures
- **Mipmaps**: Automatic LOD

#### Performance Budget
- **Triangles**: < 10K for mobile, < 100K for PC
- **Textures**: < 4K resolution total
- **Materials**: < 8 per object
- **Draw Calls**: Minimize through batching

---

## Gaussian Splat Import

### 🎯 What are Gaussian Splats?

Gaussian Splats are a cutting-edge 3D representation technique that captures real-world scenes as clouds of 3D Gaussians. Unlike traditional meshes, splats can represent complex geometry, lighting, and materials in a single, efficient format.

#### Advantages:
- **Photorealistic**: Capture real lighting and materials
- **Efficient**: Fast rendering with high detail
- **Flexible**: Can represent any geometry
- **Small Files**: Compact representation

### 📥 Splat Import Process

#### Using World Labs Marble (Recommended)
1. **Sign up** for World Labs Marble account
2. **Upload photos/videos** of your scene
3. **Wait for processing** (takes 10-60 minutes)
4. **Download PLY files**:
   - `splat.ply` - The Gaussian splat data
   - `collision.obj` - Physics collision mesh
   - `thumbnail.jpg` - Preview image

#### Alternative Methods
1. **Custom Training**: Use Nerfstudio or Gaussian Splatting tools
2. **Third-party Services**: Various online splat creation services
3. **Existing Splats**: Download from community repositories

### 🔄 Resonite Integration

#### Import Process
1. **Drag PLY file** into Resonite
2. **Import collision mesh** separately if needed
3. **Position and scale** the splat
4. **Adjust rendering settings**

#### Rendering Settings
- **Quality**: Balance detail vs performance
- **LOD**: Level of detail based on distance
- **Culling**: Hide distant splats
- **Lighting**: Dynamic lighting integration

#### Physics Integration
1. **Import collision mesh** (OBJ/FBX)
2. **Align with splat** precisely
3. **Set up physics materials**
4. **Test collision behavior**

### 🎨 Creative Applications

#### Environmental Design
- **Real Locations**: Capture and recreate real places
- **Architectural Visualization**: Show designs in context
- **Historical Preservation**: Archive real locations

#### Interactive Experiences
- **Explorable Worlds**: Walk through captured scenes
- **Interactive Elements**: Combine with dynamic objects
- **Performance Spaces**: Create stages and venues

#### Artistic Creations
- **Abstract Scenes**: Artistic reinterpretations
- **Mixed Reality**: Blend real and virtual elements
- **Experimental Art**: Push boundaries of representation

### ⚡ Performance Considerations

#### Optimization Tips
- **View Distance**: Limit render distance
- **Quality Settings**: Adjust based on hardware
- **LOD System**: Use level of detail
- **Culling**: Hide occluded splats

#### Hardware Requirements
- **GPU Memory**: 4GB+ recommended
- **VRAM**: 8GB+ for complex scenes
- **CPU**: Multi-core for physics
- **Storage**: Fast SSD for loading

---

## Creating Artifacts

### 🏗️ In-World Creation Tools

#### Basic Building
1. **Primitive Shapes**: Cube, sphere, cylinder, etc.
2. **Transform Tools**: Move, rotate, scale
3. **Material Editor**: Apply colors and textures
4. **Grouping**: Combine objects hierarchically

#### Advanced Modeling
1. **Mesh Editor**: Direct geometry manipulation
2. **Sculpting Tools**: Organic shape creation
3. **UV Tools**: Texture coordinate editing
4. **Retopology**: Optimize mesh topology

### 🎨 Material Creation

#### PBR Materials
- **Base Color**: Diffuse/albedo texture
- **Metallic/Roughness**: Surface properties
- **Normal Map**: Surface detail
- **Emission**: Self-illuminating surfaces

#### Shader Types
- **Standard PBR**: Physically based rendering
- **Toon Shader**: Cartoon-style rendering
- **Glass/Transparent**: See-through materials
- **Particle Shaders**: Effect materials

### 🎭 Avatar Creation

#### From Scratch
1. **Base Mesh**: Start with primitive or import base
2. **Rigging**: Set up bone structure
3. **Blend Shapes**: Create facial expressions
4. **Materials**: Apply skin and clothing materials

#### From Existing Models
1. **Import Base Model**: Use OBJ/FBX as starting point
2. **Add VRM Components**: Convert to VRM format
3. **Parameter Mapping**: Set up controllable parameters
4. **Testing**: Verify in mirror and with animations

### 🎵 Audio & Effects

#### Audio Import
- **Formats**: WAV (uncompressed), MP3, OGG
- **Spatial Audio**: 3D positioning
- **Reverb Zones**: Environmental audio
- **Dynamic Audio**: Procedural sound generation

#### Particle Systems
- **Emitter Shapes**: Point, sphere, box, custom mesh
- **Particle Properties**: Size, color, lifetime
- **Forces**: Gravity, wind, turbulence
- **Rendering**: Materials and blending modes

---

## Controlling Artifacts

### 🔗 ProtoFlux Control

#### Basic Object Control
```protoflux
[Button Press] → [Set Position] → [Target Object]
[Slider Value] → [Set Scale] → [Target Object]
[Trigger Enter] → [Play Animation] → [Target Object]
```

#### Advanced Control Systems
```protoflux
[User Input] → [Validation] → [State Machine] → [Object Behavior]
[Sensor Data] → [Processing] → [Feedback] → [Visual Response]
[Network Data] → [Synchronization] → [Multi-user Updates]
```

### 🎛️ OSC Control

#### OSC Address Patterns
```
/avatar/parameters/Custom/[object_name]/[parameter_name]
/world/objects/[object_id]/[property]
/audio/[source_name]/[parameter]
```

#### External Control Examples
- **Lighting Control**: DMX lighting integration
- **Audio Reactive**: Music visualization
- **Motion Capture**: Real-time animation
- **Game Integration**: External game state

### 🤖 MCP Server Control

#### Available Control Tools

**Object Manipulation:**
```bash
# Move objects in world
resonite_object_move(object_id, position, rotation, scale)

# Set object properties
resonite_object_set_property(object_id, property_name, value)

# Animate objects
resonite_object_animate(object_id, animation_data)
```

**Avatar Control:**
```bash
# Load and configure avatars
resonite_avatar_load(avatar_path, slot, parameters)

# Control avatar parameters
resonite_parameter_set(parameter_name, value, avatar_slot)

# Execute avatar animations
resonite_protoflux_execute("avatar_animation", {"intensity": 0.8})
```

**World Management:**
```bash
# Load different worlds
resonite_world_load(world_path)

# Spawn objects dynamically
resonite_object_spawn(object_template, position, properties)
```

### 📊 Parameter Control

#### Avatar Parameters
- **Blend Shapes**: Facial expressions and body morphs
- **IK Targets**: Hand and foot positioning
- **Physics**: Clothing and hair simulation
- **Custom Parameters**: User-defined controls

#### Object Parameters
- **Transform**: Position, rotation, scale
- **Materials**: Colors, textures, properties
- **Physics**: Mass, friction, bounciness
- **Behavior**: Custom ProtoFlux parameters

---

## MCP Integration

### 🎮 MCP Server Features

The Resonite MCP server provides comprehensive control over artifacts:

#### Import/Export Operations
```bash
# Import artifacts
resonite_import_artifact(file_path, import_options)

# Export artifacts
resonite_export_artifact(object_id, export_format, options)

# Batch operations
resonite_batch_import(file_list, common_options)
```

#### Real-time Control
```bash
# Object manipulation
resonite_object_transform(object_id, transform_data)

# Material control
resonite_material_set_property(material_id, property, value)

# Animation control
resonite_animation_play(animation_name, target_object)
```

#### Avatar Management
```bash
# Avatar operations
resonite_avatar_switch(avatar_path)
resonite_avatar_parameter_set(parameter, value)
resonite_avatar_animation_trigger(animation_name)
```

### 🔄 Workflow Integration

#### With External Tools
1. **Create in Blender/Unity** → Export to supported format
2. **Import via MCP** → `resonite_import_artifact()`
3. **Position and configure** → `resonite_object_transform()`
4. **Add ProtoFlux logic** → `resonite_protoflux_execute()`
5. **Test and iterate** → Real-time feedback

#### Automated Pipelines
```python
# Example automated import pipeline
def import_and_setup_model(file_path, target_position):
    # Import the model
    object_id = resonite_import_artifact(file_path, {
        "auto_scale": True,
        "import_materials": True
    })

    # Position it
    resonite_object_transform(object_id, {
        "position": target_position,
        "rotation": [0, 0, 0],
        "scale": [1, 1, 1]
    })

    # Add interaction
    resonite_protoflux_execute("setup_interaction", {
        "object_id": object_id,
        "interaction_type": "grabbable"
    })

    return object_id
```

---

## Best Practices

### 📏 Scale & Units

#### Consistent Units
- **Resonite Units**: 1 unit = 1 meter
- **Import Scale**: Check and adjust as needed
- **Avatar Scale**: Keep between 1.6-2.0 units tall
- **World Scale**: Plan for comfortable navigation

#### Scale Testing
- **Avatar Scale**: Test in mirror with other users
- **Object Scale**: Ensure comfortable interaction
- **World Scale**: Test walking distances
- **UI Scale**: Readable from typical distances

### 🎨 Material Optimization

#### Texture Guidelines
- **Resolution**: 512x512 for most, 1024x1024 for important
- **Format**: PNG for transparency, JPG for opaque
- **Compression**: Use appropriate compression
- **Mipmaps**: Always enable for distance rendering

#### Material Limits
- **Per Object**: 4-8 materials maximum
- **Total Textures**: Budget VRAM carefully
- **Shader Complexity**: Balance visual quality vs performance
- **Transparency**: Use sparingly, expensive to render

### ⚡ Performance Optimization

#### Geometry Budget
- **Mobile/Quest**: < 10K triangles per object
- **PC/Medium**: < 50K triangles per object
- **PC/High-End**: < 200K triangles per object
- **World Total**: < 1M triangles visible at once

#### Draw Call Optimization
- **Batching**: Combine objects with same material
- **LOD System**: Use level of detail
- **Culling**: Hide unseen objects
- **Instancing**: Reuse identical objects

### 🔄 Version Control

#### Asset Organization
- **Naming Convention**: Clear, descriptive names
- **Folder Structure**: Logical organization
- **Version Numbers**: Track iterations
- **Backup Strategy**: Regular backups of important assets

#### Collaboration
- **Shared Libraries**: Reusable asset collections
- **Change Tracking**: Document modifications
- **Review Process**: Test changes before publishing
- **Documentation**: Explain complex assets

---

## Troubleshooting

### 📥 Import Issues

#### Common Import Problems
- **File Not Recognized**: Check file format and extension
- **Import Fails**: Verify file integrity, try different format
- **Materials Missing**: Ensure textures are in correct path
- **Scale Wrong**: Adjust import scale settings

#### VRM-Specific Issues
- **Blend Shapes Not Working**: Check VRM specification compliance
- **IK Not Functioning**: Verify bone naming and hierarchy
- **Materials Broken**: Convert to Resonite-compatible shaders
- **Performance Issues**: Reduce triangle count and textures

#### Mesh Import Problems
- **Geometry Errors**: Clean mesh in source software
- **UV Issues**: Fix UV unwrap problems
- **Material Conflicts**: Resolve material naming conflicts
- **Animation Broken**: Check animation export settings

### 📤 Export Issues

#### Export Problems
- **Format Not Supported**: Choose different export format
- **Data Loss**: Some features may not export (shaders, complex materials)
- **File Size Large**: Optimize geometry and textures
- **Animation Missing**: Ensure animation is baked properly

### 🎮 Runtime Issues

#### Performance Problems
- **Lag/Stuttering**: Reduce polygon count, optimize materials
- **Memory Usage**: Monitor VRAM and system RAM
- **Frame Rate Drops**: Use LOD, reduce draw distance
- **Loading Slow**: Optimize textures and geometry

#### Control Issues
- **OSC Not Working**: Check network settings and addresses
- **ProtoFlux Broken**: Verify wire connections and data types
- **MCP Commands Fail**: Check object IDs and parameter names
- **Avatar Glitches**: Reset avatar or reload VRM

### 🔧 Advanced Troubleshooting

#### Debug Tools
- **ProtoFlux Debugger**: Step through logic visually
- **Performance Profiler**: Identify bottlenecks
- **Network Monitor**: Check OSC communication
- **Log Viewer**: Examine error messages

#### Recovery Procedures
- **Asset Corruption**: Reimport from backup
- **World Broken**: Load backup or reset to default
- **Avatar Issues**: Switch to default avatar, then reload custom
- **ProtoFlux Crash**: Disable suspect components, rebuild logic

---

## Advanced Techniques

### 🎨 Procedural Generation

#### ProtoFlux-Based Creation
```protoflux
[Random Seed] → [Noise Generation] → [Mesh Deformation] → [Material Application]
[Algorithm Input] → [Processing Pipeline] → [Output Object]
```

#### Dynamic Content
- **Runtime Mesh Generation**: Create objects procedurally
- **Material Variation**: Randomize appearances
- **Animation Synthesis**: Generate movement patterns
- **Interactive Modification**: User-driven changes

### 🔗 External Integration

#### Unity Integration
- **Unity Package Export**: Create deployable packages
- **Real-time Sync**: Live updates between Unity and Resonite
- **Asset Pipeline**: Automated import/export workflows

#### API Integration
- **REST API**: Control Resonite via HTTP requests
- **WebSocket**: Real-time bidirectional communication
- **Custom Protocols**: Specialized integration needs

### 🎭 Advanced Avatar Techniques

#### Custom IK Systems
- **Full Body IK**: Advanced pose control
- **Facial Tracking**: Detailed expression capture
- **Gesture Recognition**: Hand and body gesture detection

#### Performance Avatars
- **LOD System**: Detail reduction at distance
- **Culling**: Hide unseen avatar parts
- **Optimization**: Performance-tuned rigging

### 🌐 Multi-User Experiences

#### Synchronization
- **State Sync**: Keep objects consistent across users
- **Ownership**: Control who can modify what
- **Conflict Resolution**: Handle simultaneous changes

#### Collaboration Tools
- **Shared Editing**: Multiple users editing together
- **Version Control**: Track changes and rollbacks
- **Permission System**: Control access levels

---

## 🎯 Quick Reference

### Import Formats
- **Avatars**: VRM, Resonite native
- **Meshes**: OBJ, FBX, GLTF/GLB
- **Splatts**: PLY (Gaussian), OBJ (collision)
- **Audio**: WAV, MP3, OGG
- **Video**: MP4, WebM
- **Textures**: PNG, JPG, TGA, EXR

### Export Formats
- **Meshes**: OBJ, FBX, GLTF/GLB, PLY
- **Animations**: FBX, GLTF
- **Materials**: Embedded or separate
- **Textures**: PNG, JPG, TGA

### Control Methods
- **Direct**: In-world manipulation
- **ProtoFlux**: Visual programming
- **OSC**: External application control
- **MCP**: Programmatic control via API

### Performance Targets
- **Triangles**: < 10K (mobile), < 100K (PC)
- **Textures**: < 4K total resolution
- **Materials**: < 8 per object
- **Draw Calls**: Minimize through batching

---

**Resonite transforms 3D creation from complex pipelines into intuitive, collaborative experiences. Whether importing photorealistic Gaussian splats or crafting interactive ProtoFlux systems, the platform empowers creators to bring their visions to life in VR.** 🚀✨

---

*This guide covers artifact handling as of Resonite 2025.1. Check the official documentation for the latest features and best practices.*
