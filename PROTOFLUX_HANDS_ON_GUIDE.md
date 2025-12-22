# 🛠️ ProtoFlux Hands-On Guide for Beginners

**Step-by-step instructions to use ProtoFlux scripts in Resonite - perfect for exploring the tutorial world!**

---

## 🎯 **Quick Start: Your First ProtoFlux Script**

### **Step 1: Open ProtoFlux Interface**
```
1. Join Resonite
2. Load Tutorial World (or any world)
3. Press F3 (or find "Dev Tools" in Settings)
4. Look for "ProtoFlux" tab or button
```

**Alternative ways to open ProtoFlux:**
- **Chat Command:** Type `/openProtoFlux` in chat
- **Context Menu:** Right-click on objects → "Edit ProtoFlux"
- **Tool Menu:** Some worlds have ProtoFlux tools in the create menu

### **Step 2: Create Your First Node**
```
1. In ProtoFlux editor, right-click on empty space
2. Select "Create" → "Value" → "String Value"
3. A node appears with a text box
4. Type "Hello World!" in the text box
5. Click outside to confirm
```

### **Step 3: Add an Output**
```
1. Right-click on the String node
2. Select "Add" → "Output" → "String"
3. Now right-click empty space again
4. Select "Create" → "Utility" → "Log Message"
5. Connect the String output to the Log Message input
```

**Congratulations!** 🎉 You just created your first ProtoFlux script that outputs "Hello World!" to the log.

---

## 🎮 **Tutorial World Practice Scripts**

### **Script 1: Interactive Button (5 minutes)**

**Goal:** Make a button that changes color when clicked

#### **Step-by-Step:**
```
1. Spawn a cube (B → Create → Primitive → Cube)
2. Right-click the cube → "Edit ProtoFlux"
3. Create nodes:
   ├── [Button Events] → [On Press] → [Set Color]
   └── [Color Value] (choose a bright color)
4. Connect: Button Events → On Press → Set Color
5. Connect: Color Value → Set Color
6. Close ProtoFlux editor
7. Test: Click the cube!
```

**What you learned:** Basic event handling and visual feedback.

### **Script 2: Proximity Door (10 minutes)**

**Goal:** Door that opens when you get close

#### **Step-by-Step:**
```
1. Spawn two cubes side-by-side (make one taller as "door frame")
2. Select the door cube, right-click → "Edit ProtoFlux"
3. Create nodes:
   ├── [Player] → [Position]
   ├── [Door Cube] → [Position]
   ├── [Subtract] (Position - Position = Distance)
   ├── [Magnitude] (get distance length)
   ├── [< 2.0] (close enough threshold)
   └── [Set Position] (move door up/down)
4. Connect the flow:
   Player Position → Subtract ← Door Position → Magnitude → < 2.0 → Set Position
5. Set Position to move door up when close
6. Test by walking near the door!
```

**What you learned:** Player tracking, distance calculations, conditional logic.

### **Script 3: Color-Changing Light (8 minutes)**

**Goal:** Light that cycles through colors over time

#### **Step-by-Step:**
```
1. Spawn a light (B → Create → Lights → Point Light)
2. Select light, right-click → "Edit ProtoFlux"
3. Create nodes:
   ├── [World Time] (current time)
   ├── [Sin] (creates smooth oscillation)
   ├── [Map Range] (convert -1/+1 to 0/360 for hue)
   ├── [HSV to RGB] (convert to color)
   └── [Set Light Color]
4. Connect: World Time → Sin → Map Range → HSV to RGB → Set Light Color
5. Adjust Map Range to get nice color transitions
6. Watch your light cycle through rainbow colors!
```

**What you learned:** Time-based animations, color math, continuous effects.

---

## 🎭 **Avatar Control Scripts You Can Try**

### **Script 4: Simple Expression Changer (12 minutes)**

**Goal:** Change avatar facial expression with a button

#### **Step-by-Step:**
```
1. Spawn a button or use existing object
2. Right-click button → "Edit ProtoFlux"
3. Create nodes:
   ├── [Button Events] → [On Press]
   ├── [Integer Value] (expression index 0-5)
   ├── [Set Avatar Expression] (if available)
   └── [Or use OSC to control avatar parameters]
4. Connect: On Press → Set Avatar Expression
5. Test by pressing button and checking avatar
```

**Note:** Avatar control might require specific permissions in some worlds.

### **Script 5: Gesture Trigger (15 minutes)**

**Goal:** Trigger animation when making a specific hand gesture

#### **Step-by-Step:**
```
1. Create a ProtoFlux script on yourself or an object
2. Create nodes:
   ├── [Hand Tracking] → [Get Hand Pose]
   ├── [Pose Recognizer] (thumb up, peace sign, etc.)
   ├── [If Recognized] → [Trigger Animation]
   └── [Play Sound] (optional feedback)
3. Connect: Hand Pose → Pose Recognizer → If True → Animation
4. Test different hand gestures!
```

**Learning:** Hand tracking, gesture recognition, conditional triggers.

---

## 🌍 **World Enhancement Scripts**

### **Script 6: Welcome Message (7 minutes)**

**Goal:** Show message when players join

#### **Step-by-Step:**
```
1. Create ProtoFlux on a world object (or yourself)
2. Create nodes:
   ├── [User Joined] (world event)
   ├── [String Value] ("Welcome to my world!")
   ├── [Show Notification] or [Log Message]
   └── [Play Sound] (welcome sound)
3. Connect: User Joined → Show Notification
4. Test by having someone else join (or use alt account)
```

**Learning:** World events, user interactions, notifications.

### **Script 7: Teleport Pad (10 minutes)**

**Goal:** Teleport to another location when stepping on pad

#### **Step-by-Step:**
```
1. Spawn a flat platform as teleport pad
2. Right-click pad → "Edit ProtoFlux"
3. Create nodes:
   ├── [Trigger Enter] (when player steps on)
   ├── [Teleport Position] (target location)
   ├── [Fade To Black] (smooth transition)
   └── [Play Sound] (teleport effect)
4. Connect: Trigger Enter → Fade To Black → Teleport → Play Sound
5. Set target position to where you want to teleport
6. Test by stepping on the pad!
```

**Learning:** Player movement, smooth transitions, spatial positioning.

---

## 🔧 **Debugging Your Scripts**

### **Common Issues & Solutions:**

#### **Script Not Running:**
```
1. Check if ProtoFlux is enabled (F3 → ProtoFlux tab)
2. Verify node connections (wires should be solid)
3. Look at Log (F3 → Log) for error messages
4. Try simple test: Add [Log Message] with "Script started"
```

#### **Nodes Not Connecting:**
```
1. Check data types (color wires must match)
2. Ensure you're connecting output → input
3. Some nodes need specific object references
4. Try refreshing the ProtoFlux editor
```

#### **Performance Issues:**
```
1. Too many scripts running? Disable unused ones
2. Complex calculations? Simplify or add delays
3. Check Log for performance warnings
4. Use [Delay] nodes to spread out heavy operations
```

### **Testing Tips:**
```
1. Start simple - one or two nodes at a time
2. Use [Log Message] to debug values
3. Test in isolation before combining scripts
4. Save versions frequently (ProtoFlux can break)
```

---

## 📚 **Using Scripts from the Guide**

### **How to Implement Guide Scripts:**

#### **Step 1: Choose a Simple Script**
Start with "Interactive Button" or "Color-Changing Light" from the guide.

#### **Step 2: Set Up in ProtoFlux**
```
1. Create the nodes mentioned in the guide
2. Connect them in the order shown
3. Adjust values to match your needs
4. Test each connection individually
```

#### **Step 3: Customize for Your World**
```
1. Change colors to match your theme
2. Adjust distances/speeds for your scale
3. Add personal touches (sounds, effects)
4. Combine with other scripts
```

#### **Step 4: Save and Share**
```
1. ProtoFlux saves automatically with the object
2. To share: Save object to inventory
3. Others can copy your ProtoFlux scripts
4. Document what your scripts do!
```

---

## 🎯 **Tutorial World Specific Tips**

### **Practice Areas:**
- **Spawn platforms** for testing scripts
- **Use existing objects** (buttons, doors) to modify
- **Practice in empty areas** to avoid disturbing others
- **Ask for permission** before modifying shared objects

### **Learning Path in Tutorial World:**
```
1. Start with simple buttons and lights
2. Progress to proximity-based interactions
3. Try avatar controls (if allowed)
4. Experiment with world events
5. Combine multiple scripts together
```

### **Getting Help:**
```
1. Use /help command in chat
2. Ask in Resonite Discord #protoflux channel
3. Watch ProtoFlux tutorial videos
4. Study existing scripts in the world
5. Experiment and learn from mistakes!
```

---

## 🚀 **Next Steps After Tutorial World**

### **Build Your Own World:**
```
1. Create private world (Dash → Worlds → Create)
2. Import your tested scripts
3. Build around your ProtoFlux interactions
4. Invite friends to test and give feedback
```

### **Advanced Learning:**
```
1. Study the ProtoFlux Guide for theory
2. Learn about data types and flow
3. Understand component reusability
4. Explore MCP integration possibilities
```

### **Community Resources:**
```
1. Resonite Discord #protoflux
2. ProtoFlux documentation wiki
3. Community script sharing
4. Tutorial videos on YouTube
```

---

**Remember: ProtoFlux is about experimentation!** 🎮

**Break things, try crazy connections, learn from failures. Every "mistake" teaches you something new about how ProtoFlux works.**

**Start with the button script, then try the proximity door. Before you know it, you'll be building complex interactive worlds!** 🚀✨

**For detailed script examples, see the [Useful ProtoFlux Scripts Guide](./USEFUL_PROTOFLUX_SCRIPTS.md).**

**Happy ProtoFluxing!** 🤖🎭
