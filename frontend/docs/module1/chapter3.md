---
sidebar_label: 'Chapter 3: URDF for Humanoid Robots'
sidebar_position: 3
---

# Chapter 3: URDF for Humanoid Robots

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand the Unified Robot Description Format (URDF) structure
- Create basic robot models with links and joints
- Define joint types and their properties
- Include visual and collision properties in URDF
- Use Xacro macros to simplify complex robot descriptions

## Introduction to URDF

Unified Robot Description Format (URDF) is an XML-based format used in ROS to describe robot models. It defines the physical structure of a robot including links, joints, inertial properties, visual elements, and collision properties.

URDF is essential for:
- Robot simulation in Gazebo
- Robot visualization in RViz
- Kinematic analysis
- Motion planning

## URDF Structure

A basic URDF file consists of:

```xml
<?xml version="1.0"?>
<robot name="my_robot">
  <!-- Links definition -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <box size="1 1 1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1"/>
      <inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/>
    </inertial>
  </link>

  <!-- Joints definition -->
  <joint name="joint_name" type="revolute">
    <parent link="base_link"/>
    <child link="child_link"/>
    <origin xyz="1 0 0" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14" upper="3.14" effort="100" velocity="1"/>
  </joint>

  <link name="child_link">
    <!-- Child link definition -->
  </link>
</robot>
```

## Links

A **link** represents a rigid body part of the robot. Each link has:

- **Visual**: How the link appears in visualization
- **Collision**: How the link interacts in physics simulation
- **Inertial**: Mass and inertial properties for dynamics

### Visual Properties

The visual element defines how a link appears:

```xml
<visual>
  <origin xyz="0 0 0" rpy="0 0 0"/>
  <geometry>
    <!-- Choose one geometry type -->
    <box size="1 2 3"/>
    <!-- OR -->
    <cylinder radius="0.5" length="1.0"/>
    <!-- OR -->
    <sphere radius="0.5"/>
    <!-- OR -->
    <mesh filename="package://my_robot/meshes/link.stl"/>
  </geometry>
  <material name="blue">
    <color rgba="0 0 1 1"/>
  </material>
</visual>
```

### Collision Properties

The collision element defines how the link interacts in physics simulation:

```xml
<collision>
  <origin xyz="0 0 0" rpy="0 0 0"/>
  <geometry>
    <!-- Same geometry types as visual -->
    <box size="1 2 3"/>
  </geometry>
</collision>
```

### Inertial Properties

The inertial element defines mass and inertia properties:

```xml
<inertial>
  <origin xyz="0 0 0" rpy="0 0 0"/>
  <mass value="1.0"/>
  <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
</inertial>
```

## Joints

A **joint** connects two links. Common joint types include:

- **Revolute**: Rotational joint with limits
- **Continuous**: Rotational joint without limits
- **Prismatic**: Linear sliding joint with limits
- **Fixed**: Rigid connection (no movement)
- **Floating**: 6 DOF joint
- **Planar**: Movement in a plane

### Joint Definition

```xml
<joint name="joint_name" type="revolute">
  <parent link="parent_link"/>
  <child link="child_link"/>
  <origin xyz="1 0 0" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit lower="-3.14" upper="3.14" effort="100" velocity="1"/>
  <dynamics damping="0.1" friction="0.0"/>
</joint>
```

## Humanoid Robot Example

Here's a simplified humanoid robot with torso, head, arms, and legs:

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">
  <!-- Torso -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.5 0.3 0.8"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.3 0.8"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10"/>
      <inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/>
    </inertial>
  </link>

  <!-- Head -->
  <link name="head">
    <visual>
      <geometry>
        <sphere radius="0.15"/>
      </geometry>
      <material name="skin">
        <color rgba="1 0.8 0.6 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.15"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2"/>
      <inertia ixx="0.05" ixy="0" ixz="0" iyy="0.05" iyz="0" izz="0.05"/>
    </inertial>
  </link>

  <!-- Neck joint -->
  <joint name="neck_joint" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 0.5" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="1"/>
  </joint>

  <!-- Right upper arm -->
  <link name="right_upper_arm">
    <visual>
      <geometry>
        <cylinder length="0.4" radius="0.05"/>
      </geometry>
      <material name="gray"/>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.4" radius="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Right shoulder joint -->
  <joint name="right_shoulder_joint" type="revolute">
    <parent link="torso"/>
    <child link="right_upper_arm"/>
    <origin xyz="-0.3 0 0.2" rpy="0 0 -1.57"/>
    <axis xyz="0 1 0"/>
    <limit lower="-3.14" upper="3.14" effort="10" velocity="1"/>
  </joint>
</robot>
```

## Xacro for Complex Models

Xacro (XML Macros) allows you to create reusable URDF components:

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="xacro_humanoid">

  <!-- Define constants -->
  <xacro:property name="M_PI" value="3.14159"/>
  <xacro:property name="torso_width" value="0.5"/>
  <xacro:property name="torso_depth" value="0.3"/>
  <xacro:property name="torso_height" value="0.8"/>

  <!-- Macro for a simple box link -->
  <xacro:macro name="box_link" params="name x y z mass color">
    <link name="${name}">
      <visual>
        <geometry>
          <box size="${x} ${y} ${z}"/>
        </geometry>
        <material name="${color}_material">
          <color rgba="${color} 1"/>
        </material>
      </visual>
      <collision>
        <geometry>
          <box size="${x} ${y} ${z}"/>
        </geometry>
      </collision>
      <inertial>
        <mass value="${mass}"/>
        <inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/>
      </inertial>
    </link>
  </xacro:macro>

  <!-- Use the macro -->
  <xacro:box_link name="torso" x="0.5" y="0.3" z="0.8" mass="10" color="0.5 0.5 0.5"/>

</robot>
```

## URDF Tools

ROS provides several tools for working with URDF:

- `check_urdf <urdf_file>`: Validate URDF syntax
- `urdf_to_graphiz <urdf_file>`: Generate robot structure diagram
- `rviz`: Visualize URDF models
- `gazebo`: Simulate URDF robots

## Best Practices

1. **Start Simple**: Begin with basic shapes and add complexity gradually
2. **Use Consistent Units**: Stick to meters for length, kilograms for mass
3. **Validate Regularly**: Use `check_urdf` to catch errors early
4. **Use Xacro**: For complex robots, use Xacro to avoid repetition
5. **Realistic Inertias**: Calculate or estimate realistic inertial properties

## Assessment Questions

1. What are the three main components that define a link in URDF?
2. Name the six different joint types available in URDF.
3. What is the difference between visual and collision elements in a link?
4. When would you use Xacro instead of plain URDF?
5. What is the purpose of the inertial element in a URDF link?

## Knowledge Check

Complete these knowledge check questions to verify your understanding:

1. **Multiple Choice**: What does URDF stand for?
   - A) Universal Robot Design Format
   - B) Unified Robot Description Format
   - C) Universal Robot Definition Framework
   - D) Unified Robotics Data Format

   *Answer: B) Unified Robot Description Format*

2. **True/False**: A URDF file can contain multiple robots.
   - A) True
   - B) False

   *Answer: B) False - A URDF file describes a single robot*

3. **Multiple Choice**: Which joint type allows continuous rotation without limits?
   - A) Revolute
   - B) Prismatic
   - C) Continuous
   - D) Fixed

   *Answer: C) Continuous*

4. **Short Answer**: Explain the difference between visual and collision properties in a URDF link.

   *Answer: Visual properties define how the link appears in visualization tools like RViz, while collision properties define how the link interacts in physics simulation. They can use different geometries for performance reasons.*

5. **Scenario**: You're designing a humanoid robot with 20 identical joints. How would you simplify the URDF using Xacro?

   *Answer: Create a Xacro macro for a joint with parameters for name, type, limits, etc., then instantiate it 20 times with different parameter values.*

## References

- [URDF/XML Format](http://wiki.ros.org/urdf/XML)
- [Xacro Documentation](http://wiki.ros.org/xacro)
- [Robot Modeling Tutorials](https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Introduction.html)