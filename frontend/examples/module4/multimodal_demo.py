#!/usr/bin/env python3
"""
multimodal_demo.py

Example demonstrating multi-modal interaction combining voice, vision, and gesture inputs.
Shows how to integrate different input modalities for enhanced robot interaction.
"""

import cv2
import mediapipe as mp
import numpy as np
import json
from typing import Dict, List, Tuple, Optional
import time
import threading
import queue

class VisionProcessor:
    """
    Vision processing for object detection and scene analysis.
    """

    def __init__(self):
        # Initialize MediaPipe components
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_objectron = mp.solutions.objectron

        # For this demo, we'll use a simple color-based object detection
        # In a real system, you'd use more sophisticated methods like YOLO
        self.object_colors = {
            'red_ball': ([0, 0, 150], [10, 10, 255]),  # Lower and upper HSV bounds
            'blue_cup': ([100, 100, 50], [130, 255, 255]),
            'green_book': ([40, 50, 50], [80, 255, 255])
        }

    def detect_objects(self, image: np.ndarray) -> List[Dict]:
        """
        Detect objects in the image using color-based detection.

        Args:
            image: Input image as numpy array

        Returns:
            List of detected objects with bounding boxes and confidence
        """
        # Convert BGR to HSV for better color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        detected_objects = []

        for obj_name, (lower, upper) in self.object_colors.items():
            # Create mask for the color range
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                # Filter by area to avoid small noise
                area = cv2.contourArea(contour)
                if area > 500:  # Minimum area threshold
                    # Get bounding box
                    x, y, w, h = cv2.boundingRect(contour)

                    # Calculate center and confidence based on size
                    center_x, center_y = x + w//2, y + h//2
                    confidence = min(1.0, area / 10000)  # Normalize confidence

                    detected_objects.append({
                        'class': obj_name,
                        'confidence': confidence,
                        'bbox': [x, y, w, h],
                        'center': [center_x, center_y],
                        'area': area
                    })

        return detected_objects

    def analyze_scene(self, image: np.ndarray) -> Dict:
        """
        Analyze the scene composition and spatial relationships.

        Args:
            image: Input image

        Returns:
            Scene analysis results
        """
        height, width = image.shape[:2]
        objects = self.detect_objects(image)

        # Analyze spatial relationships
        scene_analysis = {
            'objects': objects,
            'scene_composition': {
                'object_density': len(objects) / (width * height) if width * height > 0 else 0,
                'dominant_region': self._find_dominant_region(objects, width, height),
                'image_dimensions': [width, height]
            },
            'spatial_relationships': self._analyze_spatial_relationships(objects),
            'timestamp': time.time()
        }

        return scene_analysis

    def _find_dominant_region(self, objects: List[Dict], width: int, height: int) -> str:
        """Find the dominant region of the image based on object placement."""
        if not objects:
            return 'empty'

        # Divide image into quadrants
        center_x, center_y = width // 2, height // 2

        top_left_count = sum(1 for obj in objects
                           if obj['center'][0] < center_x and obj['center'][1] < center_y)
        top_right_count = sum(1 for obj in objects
                            if obj['center'][0] >= center_x and obj['center'][1] < center_y)
        bottom_left_count = sum(1 for obj in objects
                              if obj['center'][0] < center_x and obj['center'][1] >= center_y)
        bottom_right_count = sum(1 for obj in objects
                               if obj['center'][0] >= center_x and obj['center'][1] >= center_y)

        # Determine dominant region
        counts = {
            'top-left': top_left_count,
            'top-right': top_right_count,
            'bottom-left': bottom_left_count,
            'bottom-right': bottom_right_count
        }

        return max(counts, key=counts.get)

    def _analyze_spatial_relationships(self, objects: List[Dict]) -> List[Dict]:
        """Analyze spatial relationships between objects."""
        relationships = []

        for i, obj1 in enumerate(objects):
            for j, obj2 in enumerate(objects[i+1:], i+1):
                dx = obj2['center'][0] - obj1['center'][0]
                dy = obj2['center'][1] - obj1['center'][1]
                distance = np.sqrt(dx**2 + dy**2)

                # Determine relationship based on distance
                if distance < 50:  # Very close
                    relationship = 'very_close'
                elif distance < 150:  # Close
                    relationship = 'close'
                elif distance < 300:  # Medium distance
                    relationship = 'medium_distance'
                else:  # Far apart
                    relationship = 'far_apart'

                # Determine direction
                if abs(dx) > abs(dy):  # Horizontal dominates
                    direction = 'left' if dx < 0 else 'right'
                else:  # Vertical dominates
                    direction = 'above' if dy < 0 else 'below'

                relationships.append({
                    'object1': obj1['class'],
                    'object2': obj2['class'],
                    'relationship': relationship,
                    'direction': direction,
                    'distance_pixels': distance
                })

        return relationships

class GestureDetector:
    """
    Hand gesture detection using MediaPipe.
    Detects hand landmarks and recognizes pointing gestures.
    """

    def __init__(self):
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def detect_gestures(self, image: np.ndarray) -> Dict:
        """
        Detect hand gestures in the image.

        Args:
            image: Input image as numpy array

        Returns:
            Dictionary with gesture information
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image
        results = self.hands.process(image_rgb)

        gesture_data = {
            'hands_detected': 0,
            'gestures': [],
            'is_pointing': False,
            'pointing_direction': None,
            'confidence': 0.0
        }

        if results.multi_hand_landmarks:
            gesture_data['hands_detected'] = len(results.multi_hand_landmarks)

            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Draw landmarks for visualization
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )

                # Check for pointing gesture
                if self._is_pointing_gesture(hand_landmarks):
                    gesture_data['is_pointing'] = True
                    gesture_data['pointing_direction'] = self._get_pointing_direction(
                        hand_landmarks, image.shape
                    )
                    # Use the confidence from the hand detection
                    gesture_data['confidence'] = results.multi_handedness[idx].classification[0].score

        return gesture_data

    def _is_pointing_gesture(self, landmarks) -> bool:
        """Check if the hand is in a pointing gesture."""
        # Get landmark positions
        index_finger_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        index_finger_pip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
        middle_finger_tip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        middle_finger_pip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP]

        # Check if index finger is extended and middle finger is bent
        index_extended = index_finger_tip.y < index_finger_pip.y  # Index finger higher than PIP
        middle_bent = middle_finger_tip.y > middle_finger_pip.y   # Middle finger lower than PIP

        # Additional checks for other fingers being bent
        ring_tip = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
        ring_pip = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP]
        ring_bent = ring_tip.y > ring_pip.y

        pinky_tip = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]
        pinky_pip = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_PIP]
        pinky_bent = pinky_tip.y > pinky_pip.y

        return index_extended and middle_bent and ring_bent and pinky_bent

    def _get_pointing_direction(self, landmarks, image_shape) -> Dict:
        """Get the direction of the pointing gesture."""
        index_finger_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        wrist = landmarks.landmark[self.mp_hands.HandLandmark.WRIST]

        h, w, c = image_shape
        tip_x = int(index_finger_tip.x * w)
        tip_y = int(index_finger_tip.y * h)
        wrist_x = int(wrist.x * w)
        wrist_y = int(wrist.y * h)

        # Calculate direction vector
        dx = tip_x - wrist_x
        dy = tip_y - wrist_y

        # Normalize and get angle
        magnitude = max(1, np.sqrt(dx*dx + dy*dy))
        normalized_dx = dx / magnitude
        normalized_dy = dy / magnitude

        # Calculate angle in degrees
        angle_degrees = np.degrees(np.arctan2(dy, dx))
        if angle_degrees < 0:
            angle_degrees += 360

        # Determine general direction
        if -45 <= angle_degrees < 45:
            direction = 'right'
        elif 45 <= angle_degrees < 135:
            direction = 'down'
        elif 135 <= angle_degrees < 225:
            direction = 'left'
        else:
            direction = 'up'

        return {
            'direction': direction,
            'angle_degrees': angle_degrees,
            'normalized_vector': [normalized_dx, normalized_dy],
            'pixel_coordinates': [tip_x, tip_y]
        }

class MultimodalProcessor:
    """
    Complete multi-modal processor that combines voice, vision, and gesture inputs.
    """

    def __init__(self):
        self.vision_processor = VisionProcessor()
        self.gesture_detector = GestureDetector()

        # Simulated voice commands queue
        self.voice_commands = queue.Queue()
        self.fusion_results = queue.Queue()

    def process_multimodal_input(self, image: np.ndarray, voice_command: str = None) -> Dict:
        """
        Process multi-modal input combining vision, gestures, and voice.

        Args:
            image: Input image from camera
            voice_command: Optional voice command

        Returns:
            Dictionary with fused multi-modal analysis
        """
        # Process vision
        scene_analysis = self.vision_processor.analyze_scene(image)

        # Process gestures
        gesture_data = self.gesture_detector.detect_gestures(image)

        # Combine with voice command if provided
        fusion_result = {
            'vision_data': scene_analysis,
            'gesture_data': gesture_data,
            'voice_command': voice_command,
            'fusion_analysis': self._fuse_modalities(scene_analysis, gesture_data, voice_command),
            'timestamp': time.time()
        }

        return fusion_result

    def _fuse_modalities(self, vision_data: Dict, gesture_data: Dict, voice_command: str) -> Dict:
        """
        Fuse information from different modalities to create a coherent understanding.

        Args:
            vision_data: Vision analysis results
            gesture_data: Gesture detection results
            voice_command: Voice command text

        Returns:
            Fused analysis combining all modalities
        """
        fusion_analysis = {
            'intent_ambiguity': 0.0,
            'disambiguation_needed': False,
            'resolved_intent': None,
            'target_object': None,
            'target_location': None,
            'action_recommendation': None,
            'confidence': 0.0
        }

        # If we have both voice command and pointing gesture, try to resolve ambiguity
        if voice_command and gesture_data['is_pointing']:
            pointing_direction = gesture_data['pointing_direction']

            # Look for objects in the pointed direction
            pointed_objects = []
            for obj in vision_data['objects']:
                obj_center = obj['center']
                # Simplified: assume pointing direction indicates region of interest
                if self._is_in_pointed_direction(obj_center, pointing_direction, vision_data['scene_composition']['image_dimensions']):
                    pointed_objects.append(obj)

            if pointed_objects:
                fusion_analysis['target_object'] = pointed_objects[0]['class']
                fusion_analysis['disambiguation_needed'] = False
                fusion_analysis['confidence'] = max(obj['confidence'] for obj in pointed_objects)

        # If we have voice command, extract intent
        if voice_command:
            # Simple keyword-based intent extraction for demo
            if any(word in voice_command.lower() for word in ['go', 'move', 'navigate']):
                fusion_analysis['resolved_intent'] = 'navigation'
            elif any(word in voice_command.lower() for word in ['pick', 'grasp', 'take', 'grab']):
                fusion_analysis['resolved_intent'] = 'manipulation'
            elif any(word in voice_command.lower() for word in ['look', 'find', 'locate', 'see']):
                fusion_analysis['resolved_intent'] = 'perception'

        # Generate action recommendation
        self._generate_action_recommendation(fusion_analysis, vision_data, gesture_data, voice_command)

        return fusion_analysis

    def _is_in_pointed_direction(self, obj_center: List[int], pointing_direction: Dict, image_dims: List[int]) -> bool:
        """Check if object is in the pointed direction."""
        # Simplified: just check if object is in the general region indicated by pointing
        obj_x, obj_y = obj_center
        img_w, img_h = image_dims

        # Determine which region the pointing direction indicates
        if pointing_direction['direction'] == 'right':
            return obj_x > img_w * 0.5
        elif pointing_direction['direction'] == 'left':
            return obj_x < img_w * 0.5
        elif pointing_direction['direction'] == 'down':
            return obj_y > img_h * 0.5
        elif pointing_direction['direction'] == 'up':
            return obj_y < img_h * 0.5

        return True  # Default to true if direction is ambiguous

    def _generate_action_recommendation(self, fusion_analysis: Dict, vision_data: Dict, gesture_data: Dict, voice_command: str):
        """Generate action recommendation based on fused modalities."""
        intent = fusion_analysis['resolved_intent']
        target_obj = fusion_analysis['target_object']

        if intent == 'navigation' and voice_command:
            # Extract location from voice command
            locations = ['kitchen', 'living room', 'bedroom', 'office', 'garage', 'hallway']
            for loc in locations:
                if loc in voice_command.lower():
                    fusion_analysis['target_location'] = loc
                    fusion_analysis['action_recommendation'] = f"Navigate to {loc}"
                    break

        elif intent == 'manipulation' and (target_obj or voice_command):
            if target_obj:
                fusion_analysis['action_recommendation'] = f"Manipulate {target_obj} (pointed)"
            else:
                # Extract object from voice command
                objects = ['ball', 'cup', 'book', 'toy', 'box']
                for obj in objects:
                    if obj in voice_command.lower():
                        fusion_analysis['action_recommendation'] = f"Manipulate {obj}"
                        break

        elif intent == 'perception' and voice_command:
            fusion_analysis['action_recommendation'] = f"Perceive scene based on: {voice_command}"

        # Set default confidence based on available modalities
        if fusion_analysis['action_recommendation']:
            fusion_analysis['confidence'] = 0.8 if gesture_data['is_pointing'] else 0.6

def main():
    """Main function to demonstrate multi-modal processing."""
    print("Multi-modal Interaction Demo")
    print("=" * 50)

    # Initialize multi-modal processor
    multimodal_processor = MultimodalProcessor()

    # Simulate different scenarios
    scenarios = [
        {
            'name': 'Pointing to Object',
            'voice_command': 'Pick up that object',
            'image_description': 'Image with a red ball in the scene, hand pointing at it'
        },
        {
            'name': 'Navigation Command',
            'voice_command': 'Go to the kitchen',
            'image_description': 'Image of a hallway/room scene'
        },
        {
            'name': 'Object Search',
            'voice_command': 'Find my keys',
            'image_description': 'Image with various objects scattered around'
        }
    ]

    print(f"Processing {len(scenarios)} multi-modal scenarios...\n")

    for i, scenario in enumerate(scenarios, 1):
        print(f"Scenario {i}: {scenario['name']}")
        print(f"Voice Command: {scenario['voice_command']}")
        print(f"Image: {scenario['image_description']}")
        print("-" * 40)

        # Create a simulated image for demonstration
        # In a real system, this would come from a camera
        simulated_image = np.zeros((480, 640, 3), dtype=np.uint8)

        # Add some simulated objects to the image
        if 'Pointing' in scenario['name']:
            # Add a red ball
            cv2.circle(simulated_image, (320, 240), 30, (0, 0, 255), -1)
            # Add a hand pointing gesture (simplified)
            cv2.line(simulated_image, (200, 300), (320, 240), (0, 255, 0), 3)
        elif 'Navigation' in scenario['name']:
            # Add room boundaries
            cv2.rectangle(simulated_image, (50, 50), (590, 430), (255, 255, 255), 2)
        elif 'Object Search' in scenario['name']:
            # Add multiple objects
            cv2.circle(simulated_image, (150, 150), 20, (0, 0, 255), -1)  # Red
            cv2.circle(simulated_image, (300, 200), 20, (255, 0, 0), -1)  # Blue
            cv2.circle(simulated_image, (450, 300), 20, (0, 255, 0), -1)  # Green

        # Process the multi-modal input
        result = multimodal_processor.process_multimodal_input(
            simulated_image, scenario['voice_command']
        )

        # Display results
        print(f"Vision Objects: {len(result['vision_data']['objects'])}")
        print(f"Gestures Detected: {result['gesture_data']['hands_detected']}")
        print(f"Pointing Detected: {result['gesture_data']['is_pointing']}")

        if result['gesture_data']['is_pointing']:
            pointing_dir = result['gesture_data']['pointing_direction']
            print(f"Pointing Direction: {pointing_dir['direction']} "
                  f"({pointing_dir['angle_degrees']:.1f}°)")

        fusion = result['fusion_analysis']
        print(f"Resolved Intent: {fusion['resolved_intent']}")
        print(f"Target Object: {fusion['target_object']}")
        print(f"Action Recommendation: {fusion['action_recommendation']}")
        print(f"Confidence: {fusion['confidence']:.2f}")

        print()

    # Interactive simulation
    print("Interactive Multi-modal Simulation:")
    print("In a real system, this would process live camera feed and voice input.")
    print("For this demo, we'll simulate the process with predefined inputs.")

    # Simulate a complex multi-modal command
    print(f"\nSimulating: 'Look at the red ball and pick it up'")

    # Create image with red ball
    complex_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.circle(complex_image, (320, 240), 40, (0, 0, 255), -1)  # Red ball in center

    complex_result = multimodal_processor.process_multimodal_input(
        complex_image, "Look at the red ball and pick it up"
    )

    print(f"\nComplex Scenario Results:")
    print(f"Detected Objects: {[obj['class'] for obj in complex_result['vision_data']['objects']]}")
    print(f"Pointing Gesture: {complex_result['gesture_data']['is_pointing']}")
    print(f"Fusion Result: {complex_result['fusion_analysis']['action_recommendation']}")
    print(f"Confidence: {complex_result['fusion_analysis']['confidence']:.2f}")

    print(f"\nMulti-modal Interaction Demo completed!")

if __name__ == '__main__':
    main()