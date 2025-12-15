---
sidebar_label: 'Chapter 4: Multi-modal Interaction'
sidebar_position: 4
---

# Chapter 4: Multi-modal Interaction for Humanoid Robots

## Learning Objectives

By the end of this chapter, you will be able to:

1. Understand multi-modal interaction combining vision, language, and touch
2. Integrate vision-language models (VLMs) with ROS 2
3. Implement pointing gesture recognition for object selection
4. Combine speech and vision for disambiguated commands
5. Use sensor fusion for robust human-robot interaction
6. Deploy VLMs efficiently on edge hardware
7. Create natural multi-modal control interfaces

---

## 1. Introduction to Multi-modal Interaction

### 1.1 Why Multi-modal?

Humans naturally use multiple modalities:
- **Vision**: Point at objects, show gestures
- **Language**: Describe intentions, provide context
- **Touch**: Direct manipulation, haptic feedback

**Benefits for Robots:**
- ✅ Disambiguation: "Pick up that one" (pointing + speech)
- ✅ Natural interaction: How humans communicate
- ✅ Robustness: Fallback if one modality fails
- ✅ Efficiency: Faster than pure speech

---

## 2. Vision-Language Models

### 2.1 Model Options

| Model | Size | Capabilities | Deployment |
|-------|------|--------------|------------|
| **GPT-4 Vision** | Cloud | Image Q&A, OCR, scene understanding | API |
| **LLaVA** | 7B-13B | Image captioning, VQA | Local/Cloud |
| **CLIP** | 400M | Image-text matching | Edge |
| **OWL-ViT** | 1B | Open-vocabulary detection | Edge |

### 2.2 GPT-4 Vision Integration

```python
"""
GPT-4 Vision for robot scene understanding.
"""

from openai import OpenAI
import base64

client = OpenAI()

def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def query_gpt4_vision(image_path, question):
    """Query GPT-4 Vision about an image."""
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )

    return response.choices[0].message.content

# Usage
result = query_gpt4_vision(
    "robot_view.jpg",
    "What objects do you see on the table? List them from left to right."
)
print(result)
# Output: "I see a red cup, a blue book, and a smartphone from left to right."
```

---

## 3. Pointing Gesture Recognition

### 3.1 Hand Pose Detection

```python
"""
Detect pointing gestures using MediaPipe.
"""

import mediapipe as mp
import cv2
import numpy as np

class PointingDetector:
    """Detect pointing gestures and extract 3D direction."""

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5
        )

    def detect_pointing(self, image):
        """Detect if hand is pointing and extract direction."""
        results = self.hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not results.multi_hand_landmarks:
            return None

        # Get first hand
        hand_landmarks = results.multi_hand_landmarks[0]

        # Check if pointing (index extended, others curled)
        if self.is_pointing_gesture(hand_landmarks):
            # Get pointing direction
            direction = self.get_pointing_direction(hand_landmarks)
            return direction

        return None

    def is_pointing_gesture(self, landmarks):
        """Check if hand pose is pointing."""
        # Index finger extended
        index_tip = landmarks.landmark[8]
        index_pip = landmarks.landmark[6]

        # Middle/ring/pinky curled
        middle_tip = landmarks.landmark[12]
        middle_pip = landmarks.landmark[10]

        # Simple heuristic: index higher than others
        index_extended = index_tip.y < index_pip.y
        middle_curled = middle_tip.y > middle_pip.y

        return index_extended and middle_curled

    def get_pointing_direction(self, landmarks):
        """Get 3D pointing vector."""
        # Vector from wrist to index finger tip
        wrist = landmarks.landmark[0]
        index_tip = landmarks.landmark[8]

        direction = np.array([
            index_tip.x - wrist.x,
            index_tip.y - wrist.y,
            index_tip.z - wrist.z
        ])

        # Normalize
        direction = direction / np.linalg.norm(direction)

        return direction
```

---

## 4. Combined Speech + Vision

### 4.1 Disambiguation Pipeline

```python
"""
Combine speech and pointing for object selection.
"""

class MultimodalSelector:
    """Select objects using speech + pointing."""

    def __init__(self, detector, depth_camera):
        self.pointing_detector = detector
        self.depth_camera = depth_camera
        self.detected_objects = []

    def select_object(self, voice_command, camera_image):
        """Select object using voice + pointing."""

        # 1. Parse voice command
        nlp_result = self.parse_command(voice_command)
        # e.g., "pick up that cup" -> object_type="cup", determiner="that"

        # 2. If "that/this/it" mentioned, use pointing
        if nlp_result['needs_pointing']:
            # Detect pointing gesture
            pointing_dir = self.pointing_detector.detect_pointing(camera_image)

            if pointing_dir is not None:
                # Raycast to find object in pointing direction
                selected_obj = self.raycast_to_object(pointing_dir)

                # Verify object type matches voice command
                if selected_obj['type'] == nlp_result['object_type']:
                    return selected_obj
                else:
                    return f"Pointed object is {selected_obj['type']}, but you said {nlp_result['object_type']}"

        # 3. Fallback: select by description alone
        return self.select_by_description(nlp_result)

    def raycast_to_object(self, pointing_direction):
        """Find object intersecting pointing ray."""
        # Get depth image
        depth_img = self.depth_camera.get_depth()

        # Project pointing ray into 3D
        # Find objects along ray
        # Return closest object

        # Simplified implementation
        for obj in self.detected_objects:
            # Check if object is in pointing direction
            obj_direction = obj['position'] / np.linalg.norm(obj['position'])
            angle = np.arccos(np.dot(pointing_direction, obj_direction))

            if angle < np.radians(15):  # Within 15 degree cone
                return obj

        return None
```

---

## 5. Complete Multi-modal System

### 5.1 ROS 2 Integration

```python
"""
Multi-modal interaction ROS 2 node.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, PointCloud2
from std_msgs.msg import String
from cv_bridge import CvBridge
import json

class MultimodalInteractionNode(Node):
    """Multi-modal human-robot interaction node."""

    def __init__(self):
        super().__init__('multimodal_interaction')

        # Subscribe to inputs
        self.image_sub = self.create_subscription(
            Image, '/camera/rgb/image_raw', self.image_callback, 10
        )
        self.voice_sub = self.create_subscription(
            String, '/voice_commands', self.voice_callback, 10
        )

        # Publishers
        self.action_pub = self.create_publisher(String, '/robot_actions', 10)

        # State
        self.latest_image = None
        self.bridge = CvBridge()
        self.pointing_detector = PointingDetector()
        self.vlm_client = VisionLanguageModel()

        self.get_logger().info('Multi-modal interaction ready')

    def image_callback(self, msg):
        """Store latest camera image."""
        self.latest_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

    def voice_callback(self, msg):
        """Process voice command with visual context."""
        voice_command = msg.data
        self.get_logger().info(f'Voice: "{voice_command}"')

        if self.latest_image is None:
            self.get_logger().warning('No camera image available')
            return

        # Analyze command for visual grounding needs
        if self.needs_visual_grounding(voice_command):
            # Use VLM to understand scene
            scene_description = self.vlm_client.describe_scene(self.latest_image)
            self.get_logger().info(f'Scene: {scene_description}')

            # Check for pointing gesture
            pointing_dir = self.pointing_detector.detect_pointing(self.latest_image)

            # Combine modalities
            action = self.resolve_action(
                voice_command,
                scene_description,
                pointing_dir
            )

            # Execute
            if action:
                action_msg = String()
                action_msg.data = json.dumps(action)
                self.action_pub.publish(action_msg)

    def needs_visual_grounding(self, command):
        """Check if command needs vision."""
        visual_keywords = ['that', 'this', 'it', 'there', 'here', 'one', 'left', 'right']
        return any(word in command.lower() for word in visual_keywords)
```

---

## Assessment Questions

### Traditional Questions

1. **What are the benefits of multi-modal interaction over voice-only control?**
   - Answer: Multi-modal enables disambiguation ("that cup" with pointing), natural human communication patterns, robustness (fallback modalities), and efficiency (pointing faster than describing location). Combines strengths of each modality.

2. **Explain how vision-language models enable robot scene understanding.**
   - Answer: VLMs (GPT-4 Vision, LLaVA) process images and answer questions about them. Robots can ask "What objects are on the table?" or "Which cup is red?" and get text responses for action planning. Bridges vision (pixels) and language (reasoning).

3. **Describe how to detect pointing gestures for object selection.**
   - Answer: (1) Use MediaPipe to detect hand landmarks, (2) Check if index finger extended and others curled, (3) Compute vector from wrist to index fingertip, (4) Raycast this direction in 3D scene, (5) Find objects intersecting ray, (6) Select closest object within cone.

4. **How would you combine speech and pointing to disambiguate "pick up that one"?**
   - Answer: (1) Parse speech: intent=grasp, determiner="that", (2) Detect pointing gesture to get 3D direction, (3) Raycast to find pointed object, (4) Verify object type if specified in speech, (5) If match, execute grasp on pointed object. Pointing provides "which one", speech provides "what action".

5. **What challenges arise when deploying VLMs on robot edge hardware?**
   - Answer: Large model size (7B-13B params need 14-26GB), slow inference (1-5s latency), high power consumption, limited VRAM on edge GPUs. Solutions: use smaller models (CLIP, OWL-ViT), quantization (int8), cloud offloading for complex queries, caching common scenes.

### Knowledge Check Questions

6. **Multiple Choice: Which model is best for real-time edge deployment?**
   - A) GPT-4 Vision
   - B) LLaVA 13B
   - C) CLIP ✓
   - D) Flamingo
   - Answer: C. CLIP (400M params) is lightweight enough for edge GPUs with fast inference. Others require cloud or powerful workstations.

7. **True/False: Pointing gestures provide 3D object coordinates directly.**
   - Answer: False. Pointing gives a 2D direction from the hand. Requires depth sensing or raycasting in 3D scene to find the actual pointed object's 3D position.

8. **Fill in the blank: MediaPipe detects __________ hand landmarks for gesture recognition.**
   - Answer: 21 (21 keypoints including wrist, fingers, palm)

9. **Short Answer: Why combine vision and language instead of using vision alone?**
   - Answer: Vision detects "what's there" but not "what to do". Language provides intent and context. "Pick up the RED cup" (vision finds all cups, language filters by color and specifies grasp action). Complementary strengths.

10. **Scenario: User says "bring me that" while pointing, but camera is occluded. How to handle?**
    - Answer: (1) Detect no visual input available, (2) Request clarification: "I can't see right now. Can you describe which object?", (3) Switch to pure language mode: "the cup on the left", (4) Log issue for operator, (5) Move robot to unoccluded position if autonomous.

---

## Summary

In this chapter, you learned about:

- **Multi-modal Interaction**: Combining vision, language, gestures for natural control
- **Vision-Language Models**: GPT-4 Vision, LLaVA, CLIP for scene understanding
- **Gesture Recognition**: Detecting pointing with MediaPipe for object selection
- **Speech + Vision**: Disambiguating commands by combining modalities
- **ROS 2 Integration**: Complete multi-modal interaction node

Multi-modal interaction enables robots to understand humans the way humans naturally communicate—through combined speech, gestures, and visual context.

---

**Next Chapter**: [Chapter 5: Capstone Project Guide](./chapter5.md) - Build a complete voice-controlled humanoid robot system integrating all Module 4 concepts.
