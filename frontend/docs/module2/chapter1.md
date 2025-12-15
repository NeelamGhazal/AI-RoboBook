---
sidebar_label: 'Chapter 1: Physics Simulation Fundamentals'
sidebar_position: 1
---

# Chapter 1: Physics Simulation Fundamentals

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand the principles of rigid body dynamics in simulation
- Explain collision detection algorithms and their applications
- Describe sensor simulation techniques
- Apply physics simulation concepts to robotics applications
- Evaluate trade-offs between simulation accuracy and performance

## Introduction to Physics Simulation

Physics simulation is the foundation of modern robotics development. It allows engineers to test algorithms, validate designs, and train AI systems in a safe, cost-effective virtual environment before deploying to real hardware.

### Why Physics Simulation Matters

**Benefits**:
- **Safety**: Test dangerous scenarios without risk to hardware or people
- **Cost**: Reduce hardware damage and development costs
- **Speed**: Iterate faster than real-time testing
- **Reproducibility**: Create consistent test environments
- **Scale**: Simulate multiple robots and scenarios simultaneously

**Applications**:
- Algorithm development and validation
- Hardware design verification
- AI training and reinforcement learning
- System integration testing
- Edge case exploration

## Rigid Body Dynamics

Rigid body dynamics describe how solid objects move and interact in a simulated environment.

### Core Concepts

**Rigid Body**: An object that doesn't deform under forces. Key properties include:
- **Mass**: Resistance to linear acceleration
- **Inertia Tensor**: Resistance to rotational acceleration
- **Center of Mass**: Balance point of the object
- **Velocity**: Linear and angular motion

### Newton's Laws in Simulation

```python
# Pseudo-code for rigid body dynamics
class RigidBody:
    def __init__(self, mass, inertia, position, velocity):
        self.mass = mass
        self.inertia = inertia  # Inertia tensor (3x3 matrix)
        self.position = position
        self.velocity = velocity
        self.angular_velocity = [0, 0, 0]

    def apply_force(self, force, point):
        """Apply force at a point on the body"""
        # F = ma (Newton's second law)
        acceleration = force / self.mass
        self.velocity += acceleration * dt

        # Calculate torque: τ = r × F
        r = point - self.center_of_mass
        torque = cross_product(r, force)

        # Angular acceleration: α = I⁻¹τ
        angular_acceleration = inverse(self.inertia) @ torque
        self.angular_velocity += angular_acceleration * dt

    def update(self, dt):
        """Update position and rotation"""
        self.position += self.velocity * dt
        self.rotation += self.angular_velocity * dt
```

### Integration Methods

Simulators use numerical integration to update object states:

1. **Euler Integration** (simplest, least accurate):
   ```
   v(t+Δt) = v(t) + a(t)·Δt
   x(t+Δt) = x(t) + v(t)·Δt
   ```

2. **Runge-Kutta (RK4)** (more accurate, slower):
   - Uses multiple intermediate steps
   - Better energy conservation
   - Commonly used in high-fidelity simulators

3. **Semi-implicit Euler** (good balance):
   ```
   v(t+Δt) = v(t) + a(t)·Δt
   x(t+Δt) = x(t) + v(t+Δt)·Δt
   ```

## Collision Detection

Collision detection determines when and where objects intersect in the simulation.

### Collision Detection Pipeline

```mermaid
graph LR
    A[Broad Phase] --> B[Narrow Phase]
    B --> C[Contact Generation]
    C --> D[Collision Response]

    style A fill:#0f1729,stroke:#00d4ff,stroke-width:2px
    style B fill:#0f1729,stroke:#00d4ff,stroke-width:2px
    style C fill:#0f1729,stroke:#00d4ff,stroke-width:2px
    style D fill:#0f1729,stroke:#00d4ff,stroke-width:2px
```

### Broad Phase Collision Detection

Quickly eliminates pairs of objects that cannot possibly collide:

- **Bounding Volumes**: Simple shapes that enclose complex objects
  - **AABB** (Axis-Aligned Bounding Box): Fastest, less tight fit
  - **OBB** (Oriented Bounding Box): Better fit, more expensive
  - **Bounding Sphere**: Fast distance checks, loose fit

- **Spatial Partitioning**:
  - **Grid**: Divide space into cells
  - **Octree**: Hierarchical 3D grid
  - **Sweep and Prune**: Sort objects along axes

### Narrow Phase Collision Detection

Precise collision detection for pairs identified in broad phase:

- **Primitive Shapes**:
  - Sphere-sphere: Distance check
  - Box-box: Separating axis theorem (SAT)
  - Capsule-capsule: Segment distance

- **Complex Meshes**:
  - Triangle-triangle intersection
  - GJK algorithm (Gilbert-Johnson-Keerthi)
  - EPA algorithm (Expanding Polytope Algorithm)

### Contact Generation

Generate contact points with detailed information:

```python
class Contact:
    def __init__(self, point, normal, penetration_depth, bodies):
        self.point = point  # Contact point in world space
        self.normal = normal  # Contact normal (from body1 to body2)
        self.penetration_depth = penetration_depth  # How deep objects overlap
        self.body1 = bodies[0]
        self.body2 = bodies[1]

    def resolve(self, dt):
        """Resolve collision using impulse-based method"""
        # Calculate relative velocity at contact point
        v1 = self.body1.get_velocity_at_point(self.point)
        v2 = self.body2.get_velocity_at_point(self.point)
        relative_velocity = v1 - v2

        # Velocity along normal
        velocity_along_normal = dot(relative_velocity, self.normal)

        # Don't resolve if objects are separating
        if velocity_along_normal > 0:
            return

        # Calculate impulse scalar
        restitution = min(self.body1.restitution, self.body2.restitution)
        impulse_scalar = -(1 + restitution) * velocity_along_normal
        impulse_scalar /= (1/self.body1.mass + 1/self.body2.mass)

        # Apply impulse
        impulse = impulse_scalar * self.normal
        self.body1.apply_impulse(impulse, self.point)
        self.body2.apply_impulse(-impulse, self.point)
```

### Collision Response

**Impulse-Based**: Apply instantaneous velocity changes
- Fast and stable
- Used in real-time simulators
- May not conserve energy perfectly

**Constraint-Based**: Solve for forces that prevent penetration
- More accurate
- Can handle complex contact scenarios
- Computationally expensive

## Friction and Damping

### Friction Models

**Coulomb Friction**:
```
F_friction ≤ μ × F_normal
```
Where:
- μ is the coefficient of friction
- F_normal is the normal force

**Static vs Kinetic Friction**:
- **Static friction** (μ_s): Prevents motion from starting
- **Kinetic friction** (μ_k): Opposes motion once started
- Usually μ_s > μ_k

### Damping

Damping removes energy from the system to prevent unrealistic bouncing:

```python
# Linear damping (air resistance)
force_damping = -damping_coefficient * velocity

# Angular damping (rotational resistance)
torque_damping = -angular_damping_coefficient * angular_velocity
```

## Sensor Simulation

Simulating sensors is crucial for testing perception algorithms.

### Camera Simulation

**Ray Tracing**: Physically accurate rendering
- Traces light rays from camera through pixels
- Accounts for reflections, refractions
- Computationally expensive

**Rasterization**: Real-time rendering
- Projects triangles onto image plane
- Fast but less physically accurate
- Used in most real-time simulators

**Camera Models**:
```python
class PinholeCamera:
    def __init__(self, width, height, fov, position, orientation):
        self.width = width
        self.height = height
        self.fov = fov  # Field of view in degrees
        self.position = position
        self.orientation = orientation

        # Calculate focal length
        self.focal_length = (width / 2) / tan(fov / 2)

    def project_point(self, world_point):
        """Project 3D world point to 2D image coordinates"""
        # Transform to camera coordinates
        camera_point = self.world_to_camera(world_point)

        # Perspective projection
        if camera_point.z <= 0:
            return None  # Point behind camera

        u = self.focal_length * camera_point.x / camera_point.z + self.width / 2
        v = self.focal_length * camera_point.y / camera_point.z + self.height / 2

        return (u, v)
```

### LiDAR Simulation

**Ray Casting**: Simulate laser beams
- Cast rays in defined pattern (e.g., 360° horizontal, 32 vertical channels)
- Find first intersection with geometry
- Return distance and intensity

**Noise Models**:
- **Gaussian noise**: Random measurement error
- **Dropout**: Missing measurements
- **Reflectivity**: Material-dependent returns

```python
class LiDARSensor:
    def __init__(self, range_max, angular_resolution, num_channels):
        self.range_max = range_max
        self.angular_resolution = angular_resolution  # degrees
        self.num_channels = num_channels

    def scan(self, world):
        """Perform LiDAR scan"""
        points = []

        for channel in range(self.num_channels):
            vertical_angle = self.get_vertical_angle(channel)

            for horizontal_angle in range(0, 360, self.angular_resolution):
                # Create ray direction
                direction = self.angle_to_direction(horizontal_angle, vertical_angle)

                # Cast ray
                hit = world.raycast(self.position, direction, self.range_max)

                if hit:
                    distance = hit.distance
                    intensity = self.calculate_intensity(hit.material, hit.angle)

                    # Add noise
                    distance += random.gauss(0, 0.01)  # 1cm standard deviation

                    points.append((direction, distance, intensity))

        return points
```

### IMU Simulation

Inertial Measurement Units measure acceleration and angular velocity:

```python
class IMUSensor:
    def __init__(self, accel_noise, gyro_noise, accel_bias, gyro_bias):
        self.accel_noise_std = accel_noise
        self.gyro_noise_std = gyro_noise
        self.accel_bias = accel_bias
        self.gyro_bias = gyro_bias

    def measure(self, body):
        """Measure linear acceleration and angular velocity"""
        # Get true values from rigid body
        true_accel = body.get_linear_acceleration()
        true_gyro = body.get_angular_velocity()

        # Add bias and noise
        measured_accel = true_accel + self.accel_bias + random.gauss(0, self.accel_noise_std)
        measured_gyro = true_gyro + self.gyro_bias + random.gauss(0, self.gyro_noise_std)

        return {
            'linear_acceleration': measured_accel,
            'angular_velocity': measured_gyro
        }
```

### Depth Camera Simulation

Depth cameras (e.g., RealSense, Kinect) provide RGB and depth:

- **Structured Light**: Project pattern, measure distortion
- **Time of Flight**: Measure light travel time
- **Stereo Vision**: Triangulate from two cameras

**Simulation Approaches**:
1. Render depth buffer from graphics pipeline
2. Add characteristic noise patterns
3. Simulate missing data (e.g., reflective surfaces, sunlight interference)

## Simulation Performance Optimization

### Level of Detail (LOD)

Use simpler collision geometry than visual geometry:
- Visual: High-poly mesh for rendering
- Collision: Convex decomposition or primitive shapes

### Timestep Selection

**Fixed Timestep**: Consistent, deterministic
```python
dt = 1.0 / 240.0  # 240 Hz physics update
while simulation_running:
    physics_update(dt)
    render()
```

**Variable Timestep**: Adaptive to computation load
- Risk of instability
- Harder to reproduce results

### Parallelization

- **Broad phase**: Parallelize across object pairs
- **Islands**: Simulate disconnected groups separately
- **Solver**: Parallel constraint solving (advanced)

## Common Pitfalls

1. **Tunneling**: Fast objects pass through thin obstacles
   - Solution: Continuous collision detection (CCD)

2. **Jitter**: Objects vibrate unrealistically
   - Solution: Increase solver iterations, add damping

3. **Energy Drift**: System gains/loses energy over time
   - Solution: Use symplectic integrators, add damping

4. **Scale Issues**: Numerical precision problems with very large/small objects
   - Solution: Keep object sizes reasonable (0.01m to 100m)

## Assessment Questions

1. What are the three main phases of collision detection?
2. Explain the difference between static and kinetic friction.
3. How does an IMU sensor differ from a LiDAR sensor?
4. What is the purpose of using a fixed timestep in physics simulation?
5. Describe one method to prevent fast-moving objects from tunneling through obstacles.

## Knowledge Check

1. **Multiple Choice**: Which integration method provides the best balance between accuracy and performance?
   - A) Euler Integration
   - B) Semi-implicit Euler
   - C) Runge-Kutta 4
   - D) Verlet Integration

   *Answer: B) Semi-implicit Euler - provides good stability and energy conservation with reasonable computational cost*

2. **True/False**: In collision detection, the broad phase generates precise contact points.
   - A) True
   - B) False

   *Answer: B) False - The broad phase only identifies potential collisions; the narrow phase generates precise contact points*

3. **Multiple Choice**: What type of sensor uses ray casting to measure distance?
   - A) Camera
   - B) IMU
   - C) LiDAR
   - D) GPS

   *Answer: C) LiDAR*

4. **Short Answer**: Why is it important to add noise to simulated sensor data?

   *Answer: Adding noise makes simulated sensor data more realistic and helps algorithms generalize to real-world conditions where sensors always have measurement uncertainty*

5. **Scenario**: Your humanoid robot in simulation is vibrating when standing still. What are two possible causes and solutions?

   *Answer: (1) Solver iterations too low - increase iterations in physics engine settings; (2) Contact forces fighting gravity - add damping or adjust contact parameters like stiffness and damping coefficients*

## References

- [Bullet Physics Manual](https://github.com/bulletphysics/bullet3/blob/master/docs/Bullet_User_Manual.pdf)
- [Real-Time Collision Detection](https://realtimecollisiondetection.net/) by Christer Ericson
- [Game Physics Engine Development](https://www.crcpress.com/Game-Physics-Engine-Development/Millington/p/book/9780123819765) by Ian Millington

## Next Steps

In the next chapter, we'll apply these physics simulation concepts using Gazebo, setting up simulation environments for humanoid robots.