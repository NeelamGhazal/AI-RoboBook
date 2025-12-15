#!/usr/bin/env python3
"""
voice_control_demo.py

Complete example of a voice-controlled robot system that integrates:
- OpenAI Whisper for speech recognition
- LLM cognitive planning with GPT-4/Claude
- NLP intent classification and entity extraction
- Multi-modal interaction with vision and gestures
- ROS 2 action execution

This example demonstrates the complete pipeline from voice input to robot action.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image, AudioData
from geometry_msgs.msg import Point
import whisper
import openai
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import os
import threading
import queue
import time
import cv2
from cv_bridge import CvBridge
import mediapipe as mp

class VoiceControlDemo(Node):
    """
    Complete voice-controlled robot system demonstration.
    Integrates all components from Module 4: Whisper, LLM planning, NLP, multi-modal interaction.
    """

    def __init__(self):
        super().__init__('voice_control_demo')

        # Initialize all system components
        self.initialize_components()

        # Publishers
        self.voice_command_pub = self.create_publisher(String, 'voice_commands', 10)
        self.navigation_goal_pub = self.create_publisher(Point, 'navigation_goals', 10)
        self.manipulation_cmd_pub = self.create_publisher(String, 'manipulation_commands', 10)
        self.system_status_pub = self.create_publisher(String, 'system_status', 10)

        # Subscribers
        self.audio_sub = self.create_subscription(
            AudioData, 'audio_input', self.audio_callback, 10)
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10)

        # Processing queues
        self.voice_queue = queue.Queue(maxsize=10)
        self.vision_queue = queue.Queue(maxsize=5)

        # Start processing threads
        self.voice_thread = threading.Thread(target=self.voice_processing_loop, daemon=True)
        self.vision_thread = threading.Thread(target=self.vision_processing_loop, daemon=True)
        self.planning_thread = threading.Thread(target=self.planning_loop, daemon=True)

        self.voice_thread.start()
        self.vision_thread.start()
        self.planning_thread.start()

        self.get_logger().info("Voice Control Demo initialized and ready for commands")

    def initialize_components(self):
        """Initialize all system components."""
        # Whisper model for speech recognition
        self.get_logger().info("Loading Whisper model...")
        self.whisper_model = whisper.load_model('base')
        self.get_logger().info("Whisper model loaded successfully")

        # OpenAI client for LLM planning (using environment variable for API key)
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.get_logger().warn("OpenAI API key not found. LLM planning will be simulated.")
            self.openai_client = None
        else:
            openai.api_key = api_key
            self.openai_client = openai

        # NLP components
        self.nlp_model = SentenceTransformer('all-MiniLM-L6-v2')
        try:
            self.spacy_nlp = spacy.load('en_core_web_sm')
        except OSError:
            self.get_logger().warn("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.spacy_nlp = None

        # Intent classification examples
        self.intent_examples = {
            'navigation': [
                'Go to the kitchen', 'Navigate to the living room', 'Move to the bedroom',
                'Walk to the office', 'Go to the garage', 'Move to the hallway'
            ],
            'manipulation': [
                'Pick up the ball', 'Grasp the cup', 'Take the book', 'Grab the toy',
                'Pick up the box', 'Lift the chair'
            ],
            'perception': [
                'Look at the ball', 'Find the cup', 'Locate the book', 'See the toy',
                'Spot the box', 'Identify the chair'
            ]
        }

        # Pre-compute intent embeddings
        self.intent_embeddings = {}
        for intent, examples in self.intent_examples.items():
            example_embeddings = self.nlp_model.encode(examples)
            self.intent_embeddings[intent] = np.mean(example_embeddings, axis=0)

        # MediaPipe for gesture detection
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.cv_bridge = CvBridge()

        # System state
        self.system_state = {
            'is_active': True,
            'last_command': '',
            'command_history': [],
            'robot_location': {'x': 0.0, 'y': 0.0, 'theta': 0.0},
            'held_object': None,
            'vision_data': None
        }

    def audio_callback(self, msg: AudioData):
        """Handle incoming audio data."""
        try:
            self.voice_queue.put_nowait(msg)
        except queue.Full:
            self.get_logger().warn("Voice queue is full, dropping audio")

    def image_callback(self, msg: Image):
        """Handle incoming image data."""
        try:
            self.vision_queue.put_nowait(msg)
        except queue.Full:
            self.get_logger().warn("Vision queue is full, dropping frame")

    def voice_processing_loop(self):
        """Process voice commands in a separate thread."""
        while rclpy.ok() and self.system_state['is_active']:
            try:
                audio_msg = self.voice_queue.get(timeout=1.0)

                # Convert audio to numpy array (simplified - real implementation would handle encoding)
                # For this example, we'll simulate the audio processing
                audio_data = self.process_audio_data(audio_msg)

                if audio_data:
                    # Transcribe using Whisper
                    transcription = self.transcribe_audio(audio_data)

                    if transcription and transcription.strip():
                        self.get_logger().info(f"Transcribed: {transcription}")

                        # Process through NLP pipeline
                        processed_command = self.process_command_nlp(transcription)

                        # Send to planning system
                        self.send_to_planning(processed_command)

            except queue.Empty:
                continue
            except Exception as e:
                self.get_logger().error(f"Error in voice processing: {e}")

    def vision_processing_loop(self):
        """Process vision data in a separate thread."""
        while rclpy.ok() and self.system_state['is_active']:
            try:
                image_msg = self.vision_queue.get(timeout=1.0)

                # Convert ROS image to OpenCV format
                cv_image = self.cv_bridge.imgmsg_to_cv2(image_msg, desired_encoding='bgr8')

                # Process for object detection
                objects = self.detect_objects(cv_image)

                # Process for gesture detection
                gestures = self.detect_gestures(cv_image)

                # Update system state with vision data
                self.system_state['vision_data'] = {
                    'objects': objects,
                    'gestures': gestures,
                    'timestamp': time.time()
                }

                self.get_logger().info(f"Detected {len(objects)} objects, {len(gestures)} gestures")

            except queue.Empty:
                continue
            except Exception as e:
                self.get_logger().error(f"Error in vision processing: {e}")

    def planning_loop(self):
        """Process planning tasks in a separate thread."""
        while rclpy.ok() and self.system_state['is_active']:
            try:
                # In a real system, this would get tasks from a queue
                # For this demo, we'll process them directly
                time.sleep(0.1)  # Prevent busy waiting

            except Exception as e:
                self.get_logger().error(f"Error in planning loop: {e}")

    def process_audio_data(self, audio_msg):
        """Process audio data from ROS message."""
        # Simplified audio processing - in real implementation, handle proper encoding
        # Convert bytes to numpy array and normalize
        audio_array = np.frombuffer(audio_msg.data, dtype=np.int16).astype(np.float32) / 32768.0
        return audio_array

    def transcribe_audio(self, audio_data):
        """Transcribe audio using Whisper model."""
        try:
            # Ensure audio is in the right format for Whisper
            if len(audio_data.shape) > 1:
                audio_data = audio_data.squeeze()

            # Transcribe
            result = self.whisper_model.transcribe(
                audio_data,
                language='en',
                fp16=False,
                temperature=0.0
            )

            return result['text'].strip()

        except Exception as e:
            self.get_logger().error(f"Whisper transcription error: {e}")
            return None

    def process_command_nlp(self, command_text):
        """Process command through NLP pipeline."""
        # Classify intent
        intent, confidence = self.classify_intent(command_text)

        # Extract entities
        entities = self.extract_entities(command_text)

        # Create processed command structure
        processed_command = {
            'raw_text': command_text,
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'timestamp': time.time()
        }

        self.get_logger().info(f"Intent: {intent} (confidence: {confidence:.2f})")
        self.get_logger().info(f"Entities: {entities}")

        return processed_command

    def classify_intent(self, text, threshold=0.3):
        """Classify intent using sentence embeddings."""
        text_embedding = self.nlp_model.encode([text])[0]

        similarities = {}
        for intent, intent_embedding in self.intent_embeddings.items():
            similarity = cosine_similarity([text_embedding], [intent_embedding])[0][0]
            similarities[intent] = similarity

        best_intent = max(similarities, key=similarities.get)
        best_score = similarities[best_intent]

        if best_score >= threshold:
            return best_intent, best_score
        else:
            return 'unknown', best_score

    def extract_entities(self, text):
        """Extract entities from text."""
        entities = {
            'locations': [],
            'objects': [],
            'persons': [],
            'quantities': []
        }

        if self.spacy_nlp:
            doc = self.spacy_nlp(text)

            # Extract spaCy entities
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    entities['persons'].append(ent.text)
                elif ent.label_ == 'QUANTITY':
                    entities['quantities'].append(ent.text)

        # Simple keyword-based extraction for locations and objects
        text_lower = text.lower()

        # Common locations
        locations = ['kitchen', 'living room', 'bedroom', 'office', 'garage', 'hallway', 'dining room', 'bathroom']
        for loc in locations:
            if loc in text_lower:
                entities['locations'].append(loc)

        # Common objects
        objects = ['ball', 'cup', 'book', 'toy', 'box', 'chair', 'table', 'pen', 'bottle', 'bag']
        for obj in objects:
            if obj in text_lower:
                entities['objects'].append(obj)

        return entities

    def detect_objects(self, image):
        """Detect objects in image (simplified for demo)."""
        # In a real implementation, use YOLO, SSD, or similar
        # For this demo, return some placeholder objects
        return [
            {'class': 'person', 'confidence': 0.95, 'bbox': [100, 100, 50, 50]},
            {'class': 'cup', 'confidence': 0.87, 'bbox': [200, 200, 30, 40]}
        ]

    def detect_gestures(self, image):
        """Detect hand gestures in image."""
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        gestures = []

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Check for pointing gesture
                if self.is_pointing_gesture(hand_landmarks):
                    gesture_info = {
                        'type': 'pointing',
                        'confidence': 0.9,
                        'direction': self.get_pointing_direction(hand_landmarks, image.shape)
                    }
                    gestures.append(gesture_info)

        return gestures

    def is_pointing_gesture(self, landmarks):
        """Check if hand is in pointing gesture."""
        # Get landmark positions
        index_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        index_pip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
        middle_tip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        middle_pip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP]

        # Check if index finger is extended and middle finger is bent
        index_extended = index_tip.y < index_pip.y
        middle_bent = middle_tip.y > middle_pip.y

        return index_extended and middle_bent

    def get_pointing_direction(self, landmarks, image_shape):
        """Get direction of pointing gesture."""
        index_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        wrist = landmarks.landmark[self.mp_hands.HandLandmark.WRIST]

        h, w, c = image_shape
        tip_x = int(index_tip.x * w)
        tip_y = int(index_tip.y * h)
        wrist_x = int(wrist.x * w)
        wrist_y = int(wrist.y * h)

        # Calculate direction vector
        dx = tip_x - wrist_x
        dy = tip_y - wrist_y

        # Determine general direction
        if abs(dx) > abs(dy):  # Horizontal dominates
            direction = 'right' if dx > 0 else 'left'
        else:  # Vertical dominates
            direction = 'down' if dy > 0 else 'up'

        return direction

    def send_to_planning(self, processed_command):
        """Send processed command to planning system."""
        # In a real system, this would call the LLM planner
        # For this demo, we'll simulate the planning process

        command_text = processed_command['raw_text']
        intent = processed_command['intent']

        self.get_logger().info(f"Planning for command: {command_text}")

        # Simulate planning based on intent
        if intent == 'navigation':
            self.execute_navigation_command(processed_command)
        elif intent == 'manipulation':
            self.execute_manipulation_command(processed_command)
        elif intent == 'perception':
            self.execute_perception_command(processed_command)
        else:
            self.get_logger().warn(f"Unknown intent for planning: {intent}")

    def execute_navigation_command(self, command_data):
        """Execute navigation command."""
        locations = command_data['entities']['locations']
        if locations:
            location = locations[0].lower()

            # Define location coordinates (in a real system, these would be in a map)
            location_coords = {
                'kitchen': {'x': 2.0, 'y': 1.0, 'theta': 0.0},
                'living room': {'x': -1.0, 'y': 2.0, 'theta': 1.57},
                'bedroom': {'x': 0.0, 'y': -2.0, 'theta': 3.14},
                'office': {'x': -2.0, 'y': -1.0, 'theta': -1.57}
            }

            if location in location_coords:
                coords = location_coords[location]
                goal_point = Point()
                goal_point.x = coords['x']
                goal_point.y = coords['y']
                goal_point.z = coords['theta']  # Using z for theta in this simplified example

                self.navigation_goal_pub.publish(goal_point)
                self.get_logger().info(f"Published navigation goal to {location}: ({coords['x']}, {coords['y']})")

                # Update robot location (simulated)
                self.system_state['robot_location'] = coords
            else:
                self.get_logger().warn(f"Unknown location: {location}")
        else:
            self.get_logger().warn("No location specified in navigation command")

    def execute_manipulation_command(self, command_data):
        """Execute manipulation command."""
        objects = command_data['entities']['objects']
        if objects:
            obj = objects[0]

            # Create manipulation command
            manipulation_cmd = String()
            manipulation_cmd.data = json.dumps({
                'action': 'grasp',
                'object': obj,
                'location': self.system_state['robot_location']
            })

            self.manipulation_cmd_pub.publish(manipulation_cmd)
            self.get_logger().info(f"Published manipulation command: grasp {obj}")

            # Update system state
            self.system_state['held_object'] = obj
        else:
            self.get_logger().warn("No object specified in manipulation command")

    def execute_perception_command(self, command_data):
        """Execute perception command."""
        objects = command_data['entities']['objects']
        if objects:
            obj = objects[0]
            self.get_logger().info(f"Looking for object: {obj}")

            # In a real system, this would trigger object detection
            # For demo, we'll just log the request
            if self.system_state['vision_data']:
                detected_objects = [o['class'] for o in self.system_state['vision_data']['objects']]
                if obj in detected_objects:
                    self.get_logger().info(f"Found {obj} in the scene!")
                else:
                    self.get_logger().info(f"{obj} not found in the current view")
        else:
            self.get_logger().info("Perception command without specific object - analyzing scene...")

    def get_system_status(self):
        """Get current system status."""
        status = {
            'active': self.system_state['is_active'],
            'last_command': self.system_state['last_command'],
            'robot_location': self.system_state['robot_location'],
            'held_object': self.system_state['held_object'],
            'vision_available': self.system_state['vision_data'] is not None,
            'timestamp': time.time()
        }
        return status

def main(args=None):
    """Main function to run the voice control demo."""
    rclpy.init(args=args)

    demo_node = VoiceControlDemo()

    try:
        # Publish initial status
        status_msg = String()
        status_msg.data = json.dumps(demo_node.get_system_status())
        demo_node.system_status_pub.publish(status_msg)

        rclpy.spin(demo_node)
    except KeyboardInterrupt:
        print("\nShutting down voice control demo...")
        demo_node.system_state['is_active'] = False
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()