---
id: chapter5
title: "Chapter 5: Capstone Project Guide - Voice-Controlled Humanoid Robot System"
sidebar_position: 5
---

# Chapter 5: Capstone Project Guide - Voice-Controlled Humanoid Robot System

## Overview

Welcome to the capstone project for Module 4! In this comprehensive project, you'll build a complete voice-controlled humanoid robot system that integrates all the technologies covered in this module. This project combines OpenAI Whisper for speech recognition, LLM cognitive planning, NLP intent classification, and multi-modal interaction to create an intelligent robotic assistant capable of understanding and executing complex voice commands.

### Learning Objectives

By the end of this chapter, you will be able to:

1. Design and implement a complete voice-controlled humanoid robot system
2. Integrate speech recognition, LLM planning, and NLP processing in a unified architecture
3. Create robust multi-modal interaction capabilities combining voice, vision, and gestures
4. Build a scalable system architecture for real-time voice command processing
5. Implement safety mechanisms and error handling for voice-controlled robots
6. Evaluate and optimize the performance of the integrated system
7. Deploy and test the complete voice-controlled robot system

### Prerequisites

Before starting this capstone project, ensure you have completed:

- Module 1: Introduction to Robotics and ROS 2
- Module 2: Advanced ROS 2 Programming with Isaac Sim, VSLAM, and Nav2
- Module 3: Advanced ROS 2 Programming with Isaac Sim, VSLAM, and Nav2
- Module 4, Chapters 1-4: Voice-to-Action, LLM Cognitive Planning, NLP to ROS 2 Actions, and Multi-modal Interaction

### Estimated Completion Time

This capstone project requires approximately **2-3 weeks** of focused work, depending on your prior experience with the technologies involved. The project is divided into several phases with clear milestones and deliverables.

## 1. Project Requirements and Architecture

### 1.1 System Requirements

Our voice-controlled humanoid robot system must meet the following functional requirements:

- **Speech Recognition**: Real-time conversion of spoken commands to text using OpenAI Whisper
- **Intent Classification**: Accurate identification of user intentions from spoken commands
- **Entity Extraction**: Recognition of objects, locations, and parameters from voice commands
- **LLM Cognitive Planning**: High-level task decomposition and planning using GPT-4/Claude
- **Multi-modal Processing**: Integration of visual information and pointing gestures
- **ROS 2 Action Execution**: Translation of high-level plans into ROS 2 actions and services
- **Navigation**: Autonomous movement to specified locations
- **Object Manipulation**: Grasping and manipulation of objects based on voice commands
- **Safety Monitoring**: Continuous safety checks and emergency stop capabilities
- **Feedback Mechanisms**: Audio and visual feedback to confirm command execution

### 1.2 System Architecture

The architecture follows a modular design with clear separation of concerns:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Voice Input   │───▶│ Speech Recognizer│───▶│ Intent Classifier│
│   Microphone    │    │   (Whisper)      │    │   (NLP Model)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                    ┌──────────────────┐    ┌─────────────────┐
                    │ Entity Extractor │───▶│ LLM Planner     │
                    │ (spaCy/BERT)     │    │ (GPT-4/Claude)  │
                    └──────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                    ┌──────────────────┐    ┌─────────────────┐
                    │ Visual Processor │    │ Action Executor │
                    │ (Camera/Vision)  │    │ (ROS 2 Nodes)   │
                    └──────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                    ┌──────────────────┐    ┌─────────────────┐
                    │ Gesture Detector │    │ Navigation/     │
                    │ (MediaPipe)      │    │ Manipulation    │
                    └──────────────────┘    └─────────────────┘
```

### 1.3 Technical Stack

- **ROS 2 Humble Hawksbill** for robot middleware
- **OpenAI Whisper** for speech recognition
- **GPT-4/Claude** for cognitive planning
- **spaCy/Sentence Transformers** for NLP
- **MediaPipe** for gesture detection
- **OpenCV** for computer vision
- **Isaac Sim** for simulation and testing
- **Python 3.8+** for implementation

## 2. Phase 1: System Setup and Foundation (Days 1-3)

### 2.1 Project Structure

Create the following directory structure for the capstone project:

```
capstone_project/
├── src/
│   ├── voice_control/
│   │   ├── whisper_node.py
│   │   ├── nlp_processor.py
│   │   └── intent_classifier.py
│   ├── llm_planning/
│   │   ├── cognitive_planner.py
│   │   └── task_decomposer.py
│   ├── multimodal/
│   │   ├── vision_processor.py
│   │   └── gesture_detector.py
│   ├── ros_integration/
│   │   ├── action_executor.py
│   │   └── service_clients.py
│   └── main.py
├── config/
│   ├── whisper_config.yaml
│   ├── llm_config.yaml
│   └── system_config.yaml
├── tests/
│   ├── test_voice_control.py
│   └── test_integration.py
├── requirements.txt
└── README.md
```

### 2.2 Core System Components

Let's start by implementing the main system orchestrator that will coordinate all components:

```python
#!/usr/bin/env python3
"""
capstone_project/src/main.py
Voice-Controlled Humanoid Robot System Main Orchestrator
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Point
from sensor_msgs.msg import Image
import threading
import queue
import time
from typing import Dict, Any, Optional

class VoiceControlOrchestrator(Node):
    """
    Main orchestrator for the voice-controlled humanoid robot system.
    Coordinates all subsystems: voice recognition, NLP, LLM planning, and ROS 2 execution.
    """

    def __init__(self):
        super().__init__('voice_control_orchestrator')

        # Initialize component queues
        self.voice_queue = queue.Queue(maxsize=10)
        self.vision_queue = queue.Queue(maxsize=10)
        self.planning_queue = queue.Queue(maxsize=10)

        # Publishers for different subsystems
        self.voice_command_pub = self.create_publisher(String, 'voice_commands', 10)
        self.navigation_goal_pub = self.create_publisher(Point, 'navigation_goals', 10)
        self.manipulation_cmd_pub = self.create_publisher(String, 'manipulation_commands', 10)

        # Subscribers
        self.voice_sub = self.create_subscription(
            String, 'transcribed_text', self.voice_callback, 10)
        self.vision_sub = self.create_subscription(
            Image, 'camera_image', self.vision_callback, 10)

        # Timer for system health checks
        self.health_timer = self.create_timer(1.0, self.system_health_check)

        # System state
        self.system_state = {
            'is_active': True,
            'last_command_time': time.time(),
            'command_history': [],
            'error_count': 0
        }

        # Start component threads
        self.start_component_threads()

        self.get_logger().info("Voice Control Orchestrator initialized")

    def start_component_threads(self):
        """Start background threads for each subsystem."""
        # Voice processing thread
        voice_thread = threading.Thread(target=self.voice_processing_loop, daemon=True)
        voice_thread.start()

        # Vision processing thread
        vision_thread = threading.Thread(target=self.vision_processing_loop, daemon=True)
        vision_thread.start()

        # Planning thread
        planning_thread = threading.Thread(target=self.planning_loop, daemon=True)
        planning_thread.start()

    def voice_callback(self, msg: String):
        """Handle incoming voice commands."""
        try:
            self.voice_queue.put_nowait(msg.data)
            self.get_logger().info(f"Received voice command: {msg.data}")
        except queue.Full:
            self.get_logger().warn("Voice queue is full, dropping command")

    def vision_callback(self, msg: Image):
        """Handle incoming vision data."""
        try:
            # Convert Image message to format suitable for processing
            self.vision_queue.put_nowait(msg)
        except queue.Full:
            self.get_logger().warn("Vision queue is full, dropping frame")

    def voice_processing_loop(self):
        """Process voice commands in a separate thread."""
        while rclpy.ok() and self.system_state['is_active']:
            try:
                command = self.voice_queue.get(timeout=1.0)

                # Process the command through NLP pipeline
                processed_command = self.process_voice_command(command)

                if processed_command:
                    # Send to planning system
                    self.planning_queue.put_nowait(processed_command)

                    # Log command for history
                    self.system_state['command_history'].append({
                        'timestamp': time.time(),
                        'command': command,
                        'processed': processed_command
                    })

                    self.system_state['last_command_time'] = time.time()

            except queue.Empty:
                continue
            except Exception as e:
                self.get_logger().error(f"Error in voice processing: {e}")
                self.system_state['error_count'] += 1

    def vision_processing_loop(self):
        """Process vision data in a separate thread."""
        while rclpy.ok() and self.system_state['is_active']:
            try:
                image_msg = self.vision_queue.get(timeout=1.0)

                # Process image for object detection and gesture recognition
                vision_results = self.process_vision_data(image_msg)

                if vision_results:
                    # Update system state with vision information
                    self.update_vision_state(vision_results)

            except queue.Empty:
                continue
            except Exception as e:
                self.get_logger().error(f"Error in vision processing: {e}")

    def planning_loop(self):
        """Process planning tasks in a separate thread."""
        while rclpy.ok() and self.system_state['is_active']:
            try:
                processed_command = self.planning_queue.get(timeout=1.0)

                # Generate plan using LLM
                plan = self.generate_plan(processed_command)

                if plan:
                    # Execute the plan
                    self.execute_plan(plan)

            except queue.Empty:
                continue
            except Exception as e:
                self.get_logger().error(f"Error in planning loop: {e}")

    def process_voice_command(self, command: str) -> Optional[Dict[str, Any]]:
        """Process voice command through NLP pipeline."""
        # This will be implemented by the NLP processor
        # For now, return a basic structure
        return {
            'raw_command': command,
            'intents': self.classify_intent(command),
            'entities': self.extract_entities(command),
            'confidence': 0.9
        }

    def process_vision_data(self, image_msg: Image):
        """Process vision data for object detection and gesture recognition."""
        # Placeholder - will be implemented by vision processor
        return None

    def generate_plan(self, processed_command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate execution plan using LLM."""
        # Placeholder - will be implemented by cognitive planner
        return None

    def execute_plan(self, plan: Dict[str, Any]):
        """Execute the generated plan."""
        # Placeholder - will be implemented by action executor
        pass

    def classify_intent(self, text: str) -> list:
        """Classify intent from text."""
        # This will be replaced by the actual NLP classifier
        # Simple keyword-based classification for now
        intents = []
        text_lower = text.lower()

        if any(word in text_lower for word in ['go', 'move', 'navigate', 'walk']):
            intents.append('navigation')
        if any(word in text_lower for word in ['pick', 'grasp', 'take', 'grab']):
            intents.append('manipulation')
        if any(word in text_lower for word in ['look', 'see', 'find', 'locate']):
            intents.append('perception')

        return intents

    def extract_entities(self, text: str) -> Dict[str, str]:
        """Extract entities from text."""
        # This will be replaced by the actual NLP extractor
        # Simple entity extraction for now
        entities = {}

        # Location entities
        locations = ['kitchen', 'living room', 'bedroom', 'office', 'garage', 'hallway']
        for loc in locations:
            if loc in text.lower():
                entities['location'] = loc

        # Object entities
        objects = ['ball', 'cup', 'book', 'toy', 'box', 'chair', 'table']
        for obj in objects:
            if obj in text.lower():
                entities['object'] = obj

        return entities

    def update_vision_state(self, vision_results):
        """Update system state with vision information."""
        pass

    def system_health_check(self):
        """Perform periodic system health checks."""
        current_time = time.time()

        # Check if system is responsive
        if current_time - self.system_state['last_command_time'] > 300:  # 5 minutes
            self.get_logger().warn("No commands received in 5 minutes")

        # Check error rate
        if self.system_state['error_count'] > 10:
            self.get_logger().error("High error rate detected, system may need restart")
            self.system_state['error_count'] = 0  # Reset counter

    def shutdown(self):
        """Clean shutdown of the system."""
        self.system_state['is_active'] = False
        self.get_logger().info("Shutting down voice control orchestrator")

def main(args=None):
    rclpy.init(args=args)

    orchestrator = VoiceControlOrchestrator()

    try:
        rclpy.spin(orchestrator)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        orchestrator.shutdown()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 2.3 Voice Recognition Component

Now let's implement the Whisper-based voice recognition component:

```python
#!/usr/bin/env python3
"""
capstone_project/src/voice_control/whisper_node.py
Whisper-based Speech Recognition Node
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from sensor_msgs.msg import AudioData
import whisper
import numpy as np
import torch
import threading
import queue
import time
from typing import Optional

class WhisperNode(Node):
    """
    ROS 2 node for speech recognition using OpenAI Whisper.
    Converts audio input to text and publishes transcribed text.
    """

    def __init__(self):
        super().__init__('whisper_node')

        # Load Whisper model (using 'base' model for faster inference)
        self.get_logger().info("Loading Whisper model...")
        self.model = whisper.load_model('base')
        self.get_logger().info("Whisper model loaded successfully")

        # Publishers
        self.transcription_pub = self.create_publisher(String, 'transcribed_text', 10)
        self.status_pub = self.create_publisher(String, 'voice_status', 10)

        # Subscribers
        self.audio_sub = self.create_subscription(
            AudioData, 'audio_input', self.audio_callback, 10)
        self.listen_toggle_sub = self.create_subscription(
            Bool, 'toggle_listening', self.toggle_listening_callback, 10)

        # Configuration
        self.listening_enabled = True
        self.audio_buffer = []
        self.buffer_size = 16000 * 5  # 5 seconds of audio at 16kHz
        self.min_audio_length = 16000  # Minimum 1 second of audio

        # Processing queue
        self.process_queue = queue.Queue(maxsize=5)

        # Start processing thread
        self.processing_thread = threading.Thread(target=self.process_audio_loop, daemon=True)
        self.processing_thread.start()

        self.get_logger().info("Whisper node initialized")

    def audio_callback(self, msg: AudioData):
        """Handle incoming audio data."""
        if not self.listening_enabled:
            return

        try:
            # Convert audio data to numpy array
            audio_array = np.frombuffer(msg.data, dtype=np.int16).astype(np.float32) / 32768.0

            # Add to buffer
            self.audio_buffer.extend(audio_array.tolist())

            # Limit buffer size
            if len(self.audio_buffer) > self.buffer_size:
                self.audio_buffer = self.audio_buffer[-self.buffer_size:]

        except Exception as e:
            self.get_logger().error(f"Error processing audio: {e}")

    def toggle_listening_callback(self, msg: Bool):
        """Toggle listening state."""
        self.listening_enabled = msg.data
        status_msg = String()
        status_msg.data = f"Listening {'enabled' if self.listening_enabled else 'disabled'}"
        self.status_pub.publish(status_msg)
        self.get_logger().info(status_msg.data)

    def process_audio_loop(self):
        """Process audio in a separate thread."""
        while rclpy.ok():
            if len(self.audio_buffer) >= self.min_audio_length:
                # Extract audio chunk for processing
                audio_chunk = self.audio_buffer[:self.min_audio_length]
                self.audio_buffer = self.audio_buffer[self.min_audio_length // 2:]  # Overlap

                try:
                    # Transcribe the audio
                    result = self.transcribe_audio(np.array(audio_chunk))

                    if result and result.strip():
                        # Publish transcription
                        transcription_msg = String()
                        transcription_msg.data = result
                        self.transcription_pub.publish(transcription_msg)

                        self.get_logger().info(f"Transcribed: {result}")

                except Exception as e:
                    self.get_logger().error(f"Error in audio processing: {e}")

            time.sleep(0.1)  # Small delay to prevent busy waiting

    def transcribe_audio(self, audio: np.ndarray) -> Optional[str]:
        """Transcribe audio using Whisper model."""
        try:
            # Ensure audio is in the right format
            if len(audio.shape) > 1:
                audio = audio.squeeze()

            # Transcribe using Whisper
            result = self.model.transcribe(
                audio,
                language='en',
                fp16=False,  # Set to True if using GPU with FP16 support
                temperature=0.0  # Deterministic output
            )

            return result['text'].strip()

        except Exception as e:
            self.get_logger().error(f"Error in Whisper transcription: {e}")
            return None

    def get_model_info(self):
        """Get information about the loaded model."""
        return {
            'model_type': self.model.model_name,
            'language': 'English',
            'sample_rate': 16000
        }

def main(args=None):
    rclpy.init(args=args)

    whisper_node = WhisperNode()

    try:
        rclpy.spin(whisper_node)
    except KeyboardInterrupt:
        print("Shutting down Whisper node...")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 3. Phase 2: NLP Processing Pipeline (Days 4-7)

### 3.1 Intent Classification and Entity Extraction

Now let's implement the NLP processing component that will handle intent classification and entity extraction:

```python
#!/usr/bin/env python3
"""
capstone_project/src/voice_control/nlp_processor.py
NLP Processing Pipeline for Intent Classification and Entity Extraction
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from typing import Dict, List, Tuple, Optional
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import re

class MLIntentClassifier:
    """
    Machine Learning-based intent classifier using sentence embeddings.
    Compares input text against predefined intent examples to determine intent.
    """

    def __init__(self):
        # Load sentence transformer model for semantic similarity
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Define intent examples with multiple variations
        self.intent_examples = {
            'navigation': [
                'Go to the kitchen',
                'Navigate to the living room',
                'Move to the bedroom',
                'Walk to the office',
                'Go to the garage',
                'Move to the hallway',
                'Go to the dining room',
                'Navigate to the bathroom',
                'Walk to the garden',
                'Go to the entrance'
            ],
            'manipulation': [
                'Pick up the ball',
                'Grasp the cup',
                'Take the book',
                'Grab the toy',
                'Pick up the box',
                'Lift the chair',
                'Move the table',
                'Hold the pen',
                'Get the bottle',
                'Carry the bag'
            ],
            'perception': [
                'Look at the ball',
                'Find the cup',
                'Locate the book',
                'See the toy',
                'Spot the box',
                'Identify the chair',
                'Detect the table',
                'Recognize the pen',
                'Observe the bottle',
                'Examine the bag'
            ],
            'interaction': [
                'Say hello',
                'Introduce yourself',
                'Tell me about yourself',
                'Play music',
                'Turn on the lights',
                'Turn off the lights',
                'Open the door',
                'Close the door',
                'Sing a song',
                'Dance'
            ]
        }

        # Pre-compute embeddings for all intent examples
        self.intent_embeddings = {}
        for intent, examples in self.intent_examples.items():
            example_embeddings = self.model.encode(examples)
            # Store mean embedding for the intent
            self.intent_embeddings[intent] = np.mean(example_embeddings, axis=0)

    def classify(self, text: str, threshold: float = 0.3) -> Tuple[str, float]:
        """
        Classify the intent of the given text.

        Args:
            text: Input text to classify
            threshold: Minimum similarity score to accept an intent

        Returns:
            Tuple of (intent, confidence_score)
        """
        text_embedding = self.model.encode([text])[0]

        similarities = {}
        for intent, intent_embedding in self.intent_embeddings.items():
            similarity = cosine_similarity([text_embedding], [intent_embedding])[0][0]
            similarities[intent] = similarity

        # Find the best matching intent
        best_intent = max(similarities, key=similarities.get)
        best_score = similarities[best_intent]

        if best_score >= threshold:
            return best_intent, best_score
        else:
            return 'unknown', best_score

class NLPEntityExtractor:
    """
    Named Entity Recognition and Extraction using spaCy.
    Identifies locations, objects, and other entities in text.
    """

    def __init__(self):
        # Load English model for spaCy
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            raise Exception("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")

        # Define custom entity patterns
        self.location_patterns = [
            'kitchen', 'living room', 'bedroom', 'office', 'garage', 'hallway',
            'dining room', 'bathroom', 'garden', 'entrance', 'corridor',
            'study', 'patio', 'balcony', 'basement', 'attic', 'closet'
        ]

        self.object_patterns = [
            'ball', 'cup', 'book', 'toy', 'box', 'chair', 'table', 'pen',
            'bottle', 'bag', 'laptop', 'phone', 'keys', 'wallet', 'hat',
            'glasses', 'watch', 'ring', 'jacket', 'shoes', 'umbrella'
        ]

        self.action_patterns = [
            'pick', 'grasp', 'take', 'grab', 'lift', 'move', 'hold', 'carry',
            'place', 'put', 'drop', 'throw', 'catch', 'touch', 'press'
        ]

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from the given text.

        Args:
            text: Input text to extract entities from

        Returns:
            Dictionary containing extracted entities
        """
        doc = self.nlp(text)

        entities = {
            'locations': [],
            'objects': [],
            'actions': [],
            'persons': [],
            'quantities': [],
            'custom_entities': []
        }

        # Extract spaCy recognized entities
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                entities['persons'].append(ent.text)
            elif ent.label_ == 'QUANTITY':
                entities['quantities'].append(ent.text)

        # Extract custom entities using pattern matching
        text_lower = text.lower()

        # Find locations
        for loc in self.location_patterns:
            if loc in text_lower:
                entities['locations'].append(loc)

        # Find objects
        for obj in self.object_patterns:
            if obj in text_lower:
                entities['objects'].append(obj)

        # Find actions
        for act in self.action_patterns:
            if act in text_lower:
                entities['actions'].append(act)

        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities

class NLPProcessorNode(Node):
    """
    ROS 2 node that processes voice commands using NLP techniques.
    Performs intent classification and entity extraction.
    """

    def __init__(self):
        super().__init__('nlp_processor')

        # Initialize NLP components
        self.intent_classifier = MLIntentClassifier()
        self.entity_extractor = NLPEntityExtractor()

        # Publishers
        self.processed_command_pub = self.create_publisher(String, 'processed_commands', 10)

        # Subscribers
        self.command_sub = self.create_subscription(
            String, 'transcribed_text', self.command_callback, 10)

        self.get_logger().info("NLP Processor initialized")

    def command_callback(self, msg: String):
        """Process incoming voice command."""
        try:
            text = msg.data.strip()
            if not text:
                return

            # Classify intent
            intent, confidence = self.intent_classifier.classify(text)

            # Extract entities
            entities = self.entity_extractor.extract_entities(text)

            # Create processed command structure
            processed_command = {
                'raw_text': text,
                'intent': intent,
                'confidence': confidence,
                'entities': entities,
                'timestamp': self.get_clock().now().to_msg().sec
            }

            # Publish processed command
            result_msg = String()
            result_msg.data = json.dumps(processed_command)
            self.processed_command_pub.publish(result_msg)

            self.get_logger().info(f"Processed command: {intent} (confidence: {confidence:.2f})")
            self.get_logger().info(f"Entities: {entities}")

        except Exception as e:
            self.get_logger().error(f"Error processing command: {e}")

def main(args=None):
    rclpy.init(args=args)

    nlp_processor = NLPProcessorNode()

    try:
        rclpy.spin(nlp_processor)
    except KeyboardInterrupt:
        print("Shutting down NLP processor...")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 3.2 Enhanced Intent Classification

Let's also create a more sophisticated intent classifier that can handle more complex scenarios:

```python
#!/usr/bin/env python3
"""
capstone_project/src/voice_control/intent_classifier.py
Advanced Intent Classification with Context Awareness
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Point
import json
from typing import Dict, List, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class ContextAwareIntentClassifier:
    """
    Advanced intent classifier that considers context and handles complex commands.
    """

    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Define intent examples with context
        self.intent_definitions = {
            'navigation': {
                'examples': [
                    'Go to the kitchen',
                    'Navigate to the living room',
                    'Move to the bedroom',
                    'Walk to the office',
                    'Go to the garage',
                    'Move to the hallway',
                    'Go to the dining room',
                    'Navigate to the bathroom',
                    'Walk to the garden',
                    'Go to the entrance'
                ],
                'keywords': ['go', 'move', 'navigate', 'walk', 'drive', 'head', 'travel', 'reach'],
                'patterns': [r'go to (\w+)', r'navigate to (\w+)', r'move to (\w+)']
            },
            'manipulation': {
                'examples': [
                    'Pick up the ball',
                    'Grasp the cup',
                    'Take the book',
                    'Grab the toy',
                    'Pick up the box',
                    'Lift the chair',
                    'Move the table',
                    'Hold the pen',
                    'Get the bottle',
                    'Carry the bag'
                ],
                'keywords': ['pick', 'grasp', 'take', 'grab', 'lift', 'move', 'hold', 'carry', 'get', 'collect'],
                'patterns': [r'(pick|grasp|take|grab) (the|a) (\w+)', r'lift (the|a) (\w+)']
            },
            'perception': {
                'examples': [
                    'Look at the ball',
                    'Find the cup',
                    'Locate the book',
                    'See the toy',
                    'Spot the box',
                    'Identify the chair',
                    'Detect the table',
                    'Recognize the pen',
                    'Observe the bottle',
                    'Examine the bag'
                ],
                'keywords': ['look', 'find', 'locate', 'see', 'spot', 'identify', 'detect', 'recognize', 'observe', 'examine'],
                'patterns': [r'look at (the|a) (\w+)', r'find (the|a) (\w+)', r'locate (the|a) (\w+)']
            },
            'navigation_manipulation': {
                'examples': [
                    'Go to the kitchen and pick up the cup',
                    'Navigate to the bedroom and find the book',
                    'Move to the office and grab the pen',
                    'Go to the living room and take the remote'
                ],
                'keywords': ['and', 'then', 'after', 'next'],
                'patterns': [r'go to (\w+) and (pick|grasp|take|grab) (the|a) (\w+)']
            }
        }

        # Pre-compute embeddings
        self.intent_embeddings = {}
        for intent, data in self.intent_definitions.items():
            embeddings = self.model.encode(data['examples'])
            self.intent_embeddings[intent] = np.mean(embeddings, axis=0)

    def classify_with_context(self, text: str, context: Dict = None) -> Dict:
        """
        Classify intent with context awareness.

        Args:
            text: Input text to classify
            context: Additional context information

        Returns:
            Dictionary with classification results
        """
        if context is None:
            context = {}

        text_embedding = self.model.encode([text])[0]

        # Calculate similarity scores
        similarities = {}
        for intent, intent_embedding in self.intent_embeddings.items():
            similarity = cosine_similarity([text_embedding], [intent_embedding])[0][0]
            similarities[intent] = similarity

        # Apply context-based adjustments
        adjusted_scores = self.apply_context_adjustments(similarities, text, context)

        # Find best match
        best_intent = max(adjusted_scores, key=adjusted_scores.get)
        best_score = adjusted_scores[best_intent]

        return {
            'intent': best_intent,
            'confidence': best_score,
            'all_scores': adjusted_scores,
            'original_scores': similarities
        }

    def apply_context_adjustments(self, scores: Dict, text: str, context: Dict) -> Dict:
        """Apply context-based adjustments to similarity scores."""
        adjusted_scores = scores.copy()

        # Adjust based on keywords
        text_lower = text.lower()
        for intent, data in self.intent_definitions.items():
            keyword_bonus = 0
            for keyword in data['keywords']:
                if keyword in text_lower:
                    keyword_bonus += 0.1
            adjusted_scores[intent] += keyword_bonus

        # Ensure scores don't exceed 1.0
        for intent in adjusted_scores:
            adjusted_scores[intent] = min(1.0, adjusted_scores[intent])

        return adjusted_scores

class AdvancedIntentClassifierNode(Node):
    """
    ROS 2 node for advanced intent classification with context awareness.
    """

    def __init__(self):
        super().__init__('advanced_intent_classifier')

        # Initialize classifier
        self.classifier = ContextAwareIntentClassifier()

        # Publishers
        self.classified_intent_pub = self.create_publisher(String, 'classified_intents', 10)

        # Subscribers
        self.processed_command_sub = self.create_subscription(
            String, 'processed_commands', self.processed_command_callback, 10)

        # Context storage
        self.context = {
            'last_location': None,
            'last_object': None,
            'robot_state': 'idle'
        }

        self.get_logger().info("Advanced Intent Classifier initialized")

    def processed_command_callback(self, msg: String):
        """Process incoming processed commands."""
        try:
            command_data = json.loads(msg.data)
            text = command_data['raw_text']

            # Classify with context
            result = self.classifier.classify_with_context(text, self.context)

            # Update context based on command
            self.update_context(result, command_data)

            # Publish classification result
            classification_msg = String()
            classification_msg.data = json.dumps(result)
            self.classified_intent_pub.publish(classification_msg)

            self.get_logger().info(f"Classified: {result['intent']} (confidence: {result['confidence']:.2f})")

        except Exception as e:
            self.get_logger().error(f"Error in advanced classification: {e}")

    def update_context(self, classification_result: Dict, command_data: Dict):
        """Update context based on the classified command."""
        intent = classification_result['intent']

        if intent == 'navigation':
            entities = command_data.get('entities', {})
            locations = entities.get('locations', [])
            if locations:
                self.context['last_location'] = locations[0]

        elif intent == 'manipulation':
            entities = command_data.get('entities', {})
            objects = entities.get('objects', [])
            if objects:
                self.context['last_object'] = objects[0]

        self.context['robot_state'] = 'processing'

def main(args=None):
    rclpy.init(args=args)

    classifier_node = AdvancedIntentClassifierNode()

    try:
        rclpy.spin(classifier_node)
    except KeyboardInterrupt:
        print("Shutting down advanced intent classifier...")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 4. Phase 3: LLM Cognitive Planning (Days 8-12)

### 4.1 Cognitive Planning System

Now let's implement the LLM-based cognitive planning system that will generate high-level plans based on voice commands:

```python
#!/usr/bin/env python3
"""
capstone_project/src/llm_planning/cognitive_planner.py
LLM-based Cognitive Planning System
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import openai
import json
import os
from typing import Dict, List, Optional
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

class LLMCognitivePlanner:
    """
    LLM-based cognitive planner that generates high-level plans from voice commands.
    Uses GPT-4 or Claude for sophisticated planning and task decomposition.
    """

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key
        self.model = model

        # Set up OpenAI client
        openai.api_key = api_key

        # Define system prompt for planning
        self.system_prompt = """
You are an intelligent robot cognitive planner. Your job is to decompose high-level voice commands into executable robot tasks.
Each plan should be a sequence of atomic actions that can be executed by a ROS 2 robot system.
Focus on navigation, manipulation, perception, and interaction tasks.
Return your response as valid JSON with the following structure:
{
    "plan_id": "unique identifier",
    "tasks": [
        {
            "id": "task identifier",
            "type": "navigation|manipulation|perception|interaction",
            "action": "specific action to perform",
            "parameters": {"param1": "value1", ...},
            "dependencies": ["task_id1", ...],
            "estimated_duration": seconds
        }
    ],
    "context": {
        "environment": "description of environment",
        "constraints": ["constraint1", ...]
    }
}
Be precise, efficient, and consider safety constraints.
"""

    def generate_plan(self, command: str, context: Dict = None) -> Optional[Dict]:
        """
        Generate a plan for the given command using LLM.

        Args:
            command: Voice command to plan for
            context: Additional context information

        Returns:
            Generated plan as dictionary, or None if failed
        """
        try:
            # Prepare the user message
            user_message = f"Generate a plan for this command: '{command}'"

            if context:
                user_message += f"\nAdditional context: {json.dumps(context)}"

            # Call the LLM
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=2000
            )

            # Parse the response
            plan_json = response.choices[0].message.content
            plan = json.loads(plan_json)

            return plan

        except Exception as e:
            print(f"Error generating plan: {e}")
            return None

    def validate_plan(self, plan: Dict) -> bool:
        """Validate the generated plan."""
        required_fields = ['plan_id', 'tasks']
        if not all(field in plan for field in required_fields):
            return False

        for task in plan.get('tasks', []):
            required_task_fields = ['id', 'type', 'action', 'parameters']
            if not all(field in task for field in required_task_fields):
                return False

            valid_types = ['navigation', 'manipulation', 'perception', 'interaction']
            if task['type'] not in valid_types:
                return False

        return True

class CognitivePlannerNode(Node):
    """
    ROS 2 node for LLM-based cognitive planning.
    """

    def __init__(self):
        super().__init__('cognitive_planner')

        # Get API key from environment or parameter
        api_key = os.getenv('OPENAI_API_KEY') or self.declare_parameter('openai_api_key', '').get_parameter_value().string_value
        model = self.declare_parameter('model', 'gpt-4-turbo-preview').get_parameter_value().string_value

        if not api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")

        # Initialize planner
        self.planner = LLMCognitivePlanner(api_key, model)

        # Publishers
        self.plan_pub = self.create_publisher(String, 'generated_plans', 10)

        # Subscribers
        self.intent_sub = self.create_subscription(
            String, 'classified_intents', self.intent_callback, 10)

        # Thread pool for async LLM calls
        self.executor = ThreadPoolExecutor(max_workers=2)

        self.get_logger().info("Cognitive Planner initialized")

    def intent_callback(self, msg: String):
        """Handle incoming classified intents."""
        try:
            intent_data = json.loads(msg.data)

            # Extract command from context (this would come from previous nodes)
            # For now, we'll simulate getting the command from a global context
            # In practice, this would be linked to the original voice command
            command = getattr(self, '_last_command', "Navigate to kitchen and pick up cup")

            # Generate plan
            future = self.executor.submit(self._generate_and_publish_plan, command, intent_data)

        except Exception as e:
            self.get_logger().error(f"Error in intent callback: {e}")

    def _generate_and_publish_plan(self, command: str, intent_data: Dict):
        """Generate plan in a separate thread and publish it."""
        try:
            plan = self.planner.generate_plan(command, intent_data)

            if plan and self.planner.validate_plan(plan):
                # Publish the plan
                plan_msg = String()
                plan_msg.data = json.dumps(plan)
                self.plan_pub.publish(plan_msg)

                self.get_logger().info(f"Generated plan with {len(plan['tasks'])} tasks")

                # Log plan details
                for task in plan['tasks']:
                    self.get_logger().info(f"  - {task['id']}: {task['action']}")
            else:
                self.get_logger().error("Invalid plan generated")

        except Exception as e:
            self.get_logger().error(f"Error generating plan: {e}")

    def set_last_command(self, command: str):
        """Set the last command for plan generation."""
        self._last_command = command

def main(args=None):
    rclpy.init(args=args)

    planner_node = CognitivePlannerNode()

    try:
        rclpy.spin(planner_node)
    except KeyboardInterrupt:
        print("Shutting down cognitive planner...")
    finally:
        planner_node.executor.shutdown(wait=True)
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 4.2 Task Decomposition System

Let's also create a task decomposition system that can break down complex plans into simpler steps:

```python
#!/usr/bin/env python3
"""
capstone_project/src/llm_planning/task_decomposer.py
Task Decomposition and Optimization System
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Point
import json
from typing import Dict, List
import heapq

class TaskDecomposer:
    """
    Decomposes high-level plans into executable low-level tasks.
    Optimizes task sequences and resolves dependencies.
    """

    def __init__(self):
        # Define task decomposition rules
        self.decomposition_rules = {
            'navigation_to_location': [
                'check_current_position',
                'plan_path_to_location',
                'execute_navigation',
                'verify_arrival'
            ],
            'manipulate_object': [
                'approach_object',
                'identify_grasp_points',
                'execute_grasp',
                'verify_grasp_success'
            ],
            'perceive_environment': [
                'activate_sensors',
                'capture_environment_data',
                'analyze_objects',
                'update_world_model'
            ]
        }

    def decompose_plan(self, high_level_plan: Dict) -> Dict:
        """
        Decompose high-level plan into executable low-level tasks.

        Args:
            high_level_plan: Plan from LLM cognitive planner

        Returns:
            Dictionary with decomposed and optimized tasks
        """
        low_level_tasks = []
        task_id_counter = 0

        for high_level_task in high_level_plan['tasks']:
            task_type = high_level_task['type']
            action = high_level_task['action']

            # Determine decomposition pattern
            if 'navigate' in action.lower() or 'go to' in action.lower():
                pattern = 'navigation_to_location'
            elif 'pick' in action.lower() or 'grasp' in action.lower() or 'take' in action.lower():
                pattern = 'manipulate_object'
            elif 'look' in action.lower() or 'find' in action.lower() or 'locate' in action.lower():
                pattern = 'perceive_environment'
            else:
                # Default to a simple task
                low_level_tasks.append({
                    'id': f'low_{high_level_task["id"]}_simple',
                    'type': task_type,
                    'action': action,
                    'parameters': high_level_task['parameters'],
                    'parent_id': high_level_task['id'],
                    'estimated_duration': high_level_task.get('estimated_duration', 10),
                    'dependencies': high_level_task.get('dependencies', [])
                })
                continue

            # Decompose using pattern
            subtasks = self.decomposition_rules.get(pattern, [action])
            for subtask_desc in subtasks:
                task_id_counter += 1
                low_level_tasks.append({
                    'id': f'low_{high_level_task["id"]}_{task_id_counter}',
                    'type': task_type,
                    'action': subtask_desc,
                    'parameters': self._derive_parameters(subtask_desc, high_level_task['parameters']),
                    'parent_id': high_level_task['id'],
                    'estimated_duration': self._estimate_duration(subtask_desc),
                    'dependencies': self._derive_dependencies(subtask_desc, low_level_tasks)
                })

        # Optimize task execution order considering dependencies
        optimized_tasks = self._optimize_execution_order(low_level_tasks)

        return {
            'plan_id': high_level_plan['plan_id'],
            'decomposed_tasks': optimized_tasks,
            'original_tasks': high_level_plan['tasks'],
            'optimization_summary': self._generate_optimization_summary(optimized_tasks)
        }

    def _derive_parameters(self, subtask_desc: str, original_params: Dict) -> Dict:
        """Derive parameters for subtasks based on original parameters."""
        params = original_params.copy()

        # Add specific parameters based on subtask
        if 'navigate' in subtask_desc or 'path' in subtask_desc:
            params['navigation_mode'] = 'global'
        elif 'grasp' in subtask_desc or 'identify' in subtask_desc:
            params['manipulation_mode'] = 'precision'

        return params

    def _estimate_duration(self, subtask_desc: str) -> int:
        """Estimate duration for subtask."""
        duration_map = {
            'check_current_position': 2,
            'plan_path_to_location': 5,
            'execute_navigation': 10,
            'verify_arrival': 3,
            'approach_object': 8,
            'identify_grasp_points': 15,
            'execute_grasp': 10,
            'verify_grasp_success': 5,
            'activate_sensors': 2,
            'capture_environment_data': 8,
            'analyze_objects': 12,
            'update_world_model': 5
        }

        return duration_map.get(subtask_desc, 10)

    def _derive_dependencies(self, subtask_desc: str, existing_tasks: List) -> List[str]:
        """Derive dependencies for subtask."""
        # For now, simple linear dependencies
        if existing_tasks:
            return [existing_tasks[-1]['id']]
        return []

    def _optimize_execution_order(self, tasks: List[Dict]) -> List[Dict]:
        """Optimize task execution order considering dependencies."""
        # Build dependency graph
        task_graph = {task['id']: [] for task in tasks}
        for task in tasks:
            for dep in task['dependencies']:
                if dep in task_graph:
                    task_graph[dep].append(task['id'])

        # Topological sort to determine execution order
        in_degree = {task['id']: 0 for task in tasks}
        for task_id, deps in task_graph.items():
            for dep in deps:
                in_degree[dep] += 1

        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        ordered_tasks = []

        while queue:
            current_task_id = queue.pop(0)
            ordered_tasks.append(next(task for task in tasks if task['id'] == current_task_id))

            for dependent_task_id in task_graph[current_task_id]:
                in_degree[dependent_task_id] -= 1
                if in_degree[dependent_task_id] == 0:
                    queue.append(dependent_task_id)

        return ordered_tasks

    def _generate_optimization_summary(self, tasks: List[Dict]) -> Dict:
        """Generate optimization summary."""
        total_duration = sum(task['estimated_duration'] for task in tasks)
        task_counts = {}

        for task in tasks:
            task_type = task['type']
            task_counts[task_type] = task_counts.get(task_type, 0) + 1

        return {
            'total_tasks': len(tasks),
            'total_estimated_duration': total_duration,
            'task_distribution': task_counts,
            'dependency_depth': self._calculate_dependency_depth(tasks)
        }

    def _calculate_dependency_depth(self, tasks: List[Dict]) -> int:
        """Calculate maximum dependency depth."""
        if not tasks:
            return 0

        task_deps = {task['id']: task['dependencies'] for task in tasks}
        max_depth = 0

        for task_id in task_deps:
            depth = self._calculate_single_task_depth(task_id, task_deps, {})
            max_depth = max(max_depth, depth)

        return max_depth

    def _calculate_single_task_depth(self, task_id: str, task_deps: Dict, memo: Dict) -> int:
        """Calculate dependency depth for a single task."""
        if task_id in memo:
            return memo[task_id]

        if not task_deps[task_id]:
            memo[task_id] = 1
            return 1

        depth = 1 + max(
            self._calculate_single_task_depth(dep_id, task_deps, memo)
            for dep_id in task_deps[task_id]
        )

        memo[task_id] = depth
        return depth

class TaskDecomposerNode(Node):
    """
    ROS 2 node for task decomposition and optimization.
    """

    def __init__(self):
        super().__init__('task_decomposer')

        # Initialize decomposer
        self.decomposer = TaskDecomposer()

        # Publishers
        self.decomposed_plan_pub = self.create_publisher(String, 'decomposed_plans', 10)

        # Subscribers
        self.plan_sub = self.create_subscription(
            String, 'generated_plans', self.plan_callback, 10)

        self.get_logger().info("Task Decomposer initialized")

    def plan_callback(self, msg: String):
        """Handle incoming high-level plans."""
        try:
            high_level_plan = json.loads(msg.data)

            # Decompose the plan
            decomposed_plan = self.decomposer.decompose_plan(high_level_plan)

            # Publish decomposed plan
            plan_msg = String()
            plan_msg.data = json.dumps(decomposed_plan)
            self.decomposed_plan_pub.publish(plan_msg)

            self.get_logger().info(f"Decomposed plan: {len(decomposed_plan['decomposed_tasks'])} tasks")
            self.get_logger().info(f"Estimated duration: {decomposed_plan['optimization_summary']['total_estimated_duration']} seconds")

        except Exception as e:
            self.get_logger().error(f"Error decomposing plan: {e}")

def main(args=None):
    rclpy.init(args=args)

    decomposer_node = TaskDecomposerNode()

    try:
        rclpy.spin(decomposer_node)
    except KeyboardInterrupt:
        print("Shutting down task decomposer...")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 5. Phase 4: Multi-modal Interaction (Days 13-16)

### 5.1 Vision Processing System

Now let's implement the vision processing system that will handle object detection and scene understanding:

```python
#!/usr/bin/env python3
"""
capstone_project/src/multimodal/vision_processor.py
Multi-modal Vision Processing System
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from std_msgs.msg import String
from geometry_msgs.msg import Point
import cv2
import numpy as np
from cv_bridge import CvBridge
import json
from typing import Dict, List, Tuple, Optional
import threading
import queue

class ObjectDetector:
    """
    Object detection system using YOLO or similar models.
    Detects objects in camera frames and provides spatial information.
    """

    def __init__(self):
        # For this example, we'll use OpenCV's built-in HOG descriptor for people detection
        # In practice, you'd use YOLO, SSD, or similar models
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        # Define object classes we care about
        self.target_classes = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
            'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
            'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
            'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
            'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat',
            'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
            'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
            'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
            'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
            'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]

    def detect_objects(self, image: np.ndarray) -> List[Dict]:
        """
        Detect objects in the image.

        Args:
            image: Input image as numpy array

        Returns:
            List of detected objects with bounding boxes and confidence
        """
        # Resize image for faster processing
        resized_img = cv2.resize(image, (640, 480))

        # Convert BGR to RGB for HOG detector
        rgb_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

        # Detect people (basic example)
        boxes, weights = self.hog.detectMultiScale(rgb_img, winStride=(8,8), padding=(32,32), scale=1.05)

        detections = []
        for (x, y, w, h), weight in zip(boxes, weights):
            # Convert back to original scale
            scale_x = image.shape[1] / 640.0
            scale_y = image.shape[0] / 480.0

            orig_x = int(x * scale_x)
            orig_y = int(y * scale_y)
            orig_w = int(w * scale_x)
            orig_h = int(h * scale_y)

            detections.append({
                'class': 'person',  # For this basic example
                'confidence': float(weight),
                'bbox': [orig_x, orig_y, orig_w, orig_h],
                'center': [orig_x + orig_w//2, orig_y + orig_h//2],
                'area': orig_w * orig_h
            })

        return detections

class SceneAnalyzer:
    """
    Analyzes scenes to provide context and spatial relationships.
    """

    def __init__(self):
        self.object_detector = ObjectDetector()

    def analyze_scene(self, image: np.ndarray, camera_info: Dict = None) -> Dict:
        """
        Analyze the scene in the image.

        Args:
            image: Input image
            camera_info: Camera intrinsic parameters

        Returns:
            Scene analysis results
        """
        # Detect objects
        objects = self.object_detector.detect_objects(image)

        # Analyze spatial relationships
        scene_analysis = {
            'objects': objects,
            'scene_composition': self._analyze_composition(objects, image.shape),
            'spatial_relationships': self._analyze_spatial_relationships(objects),
            'potential_interactions': self._identify_potential_interactions(objects),
            'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
        }

        return scene_analysis

    def _analyze_composition(self, objects: List[Dict], img_shape: Tuple) -> Dict:
        """Analyze the composition of the scene."""
        height, width = img_shape[:2]

        composition = {
            'object_density': len(objects) / (width * height),
            'dominant_region': self._find_dominant_region(objects, width, height),
            'foreground_objects': [obj for obj in objects if obj['area'] > (width * height * 0.01)],
            'background_objects': [obj for obj in objects if obj['area'] <= (width * height * 0.01)]
        }

        return composition

    def _find_dominant_region(self, objects: List[Dict], width: int, height: int) -> str:
        """Find the dominant region of the image based on object placement."""
        if not objects:
            return 'empty'

        # Divide image into regions
        center_x, center_y = width // 2, height // 2

        left_objects = [obj for obj in objects if obj['center'][0] < center_x]
        right_objects = [obj for obj in objects if obj['center'][0] >= center_x]
        top_objects = [obj for obj in objects if obj['center'][1] < center_y]
        bottom_objects = [obj for obj in objects if obj['center'][1] >= center_y]

        # Determine dominant region
        if len(left_objects) > len(right_objects):
            if len(top_objects) > len(bottom_objects):
                return 'top-left'
            else:
                return 'bottom-left'
        else:
            if len(top_objects) > len(bottom_objects):
                return 'top-right'
            else:
                return 'bottom-right'

    def _analyze_spatial_relationships(self, objects: List[Dict]) -> List[Dict]:
        """Analyze spatial relationships between objects."""
        relationships = []

        for i, obj1 in enumerate(objects):
            for j, obj2 in enumerate(objects[i+1:], i+1):
                dx = obj2['center'][0] - obj1['center'][0]
                dy = obj2['center'][1] - obj1['center'][1]
                distance = np.sqrt(dx**2 + dy**2)

                # Determine relationship based on distance and position
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

    def _identify_potential_interactions(self, objects: List[Dict]) -> List[Dict]:
        """Identify potential object interactions."""
        interactions = []

        for obj in objects:
            if obj['class'] in ['person', 'human']:
                # Look for nearby objects that might be interactable
                nearby_objects = [other for other in objects
                                if other != obj and
                                np.linalg.norm(np.array(obj['center']) - np.array(other['center'])) < 200]

                for nearby_obj in nearby_objects:
                    interactions.append({
                        'actor': obj['class'],
                        'action': 'near',
                        'target': nearby_obj['class'],
                        'confidence': min(obj['confidence'], nearby_obj['confidence'])
                    })

        return interactions

class VisionProcessorNode(Node):
    """
    ROS 2 node for vision processing and scene analysis.
    """

    def __init__(self):
        super().__init__('vision_processor')

        # Initialize vision components
        self.scene_analyzer = SceneAnalyzer()
        self.cv_bridge = CvBridge()

        # Publishers
        self.scene_analysis_pub = self.create_publisher(String, 'scene_analysis', 10)
        self.object_detection_pub = self.create_publisher(String, 'detected_objects', 10)

        # Subscribers
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10)
        self.camera_info_sub = self.create_subscription(
            CameraInfo, 'camera/camera_info', self.camera_info_callback, 10)

        # Processing queue
        self.process_queue = queue.Queue(maxsize=5)
        self.camera_info = None

        # Start processing thread
        self.processing_thread = threading.Thread(target=self.process_images_loop, daemon=True)
        self.processing_thread.start()

        self.get_logger().info("Vision Processor initialized")

    def camera_info_callback(self, msg: CameraInfo):
        """Handle camera info updates."""
        self.camera_info = {
            'width': msg.width,
            'height': msg.height,
            'intrinsics': msg.k
        }

    def image_callback(self, msg: Image):
        """Handle incoming camera images."""
        try:
            # Convert ROS image to OpenCV format
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Add to processing queue
            self.process_queue.put_nowait((cv_image, msg.header.stamp.sec))

        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")

    def process_images_loop(self):
        """Process images in a separate thread."""
        while rclpy.ok():
            try:
                cv_image, timestamp = self.process_queue.get(timeout=1.0)

                # Analyze the scene
                scene_analysis = self.scene_analyzer.analyze_scene(cv_image, self.camera_info)

                # Publish scene analysis
                analysis_msg = String()
                analysis_msg.data = json.dumps(scene_analysis)
                self.scene_analysis_pub.publish(analysis_msg)

                # Also publish object detections separately
                objects_msg = String()
                objects_msg.data = json.dumps(scene_analysis['objects'])
                self.object_detection_pub.publish(objects_msg)

                self.get_logger().info(f"Analyzed scene with {len(scene_analysis['objects'])} objects")

            except queue.Empty:
                continue
            except Exception as e:
                self.get_logger().error(f"Error in vision processing: {e}")

def main(args=None):
    rclpy.init(args=args)

    vision_node = VisionProcessorNode()

    try:
        rclpy.spin(vision_node)
    except KeyboardInterrupt:
        print("Shutting down vision processor...")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 5.2 Gesture Detection System

Let's also implement a gesture detection system using MediaPipe:

```python
#!/usr/bin/env python3
"""
capstone_project/src/multimodal/gesture_detector.py
Gesture Detection and Recognition System
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from geometry_msgs.msg import Point
import cv2
import mediapipe as mp
from cv_bridge import CvBridge
import json
from typing import Dict, List, Tuple, Optional
import math

class HandGestureDetector:
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
            'landmarks': [],
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

                # Analyze gestures
                hand_gesture = self._analyze_hand_gesture(hand_landmarks, image.shape)
                gesture_data['gestures'].append(hand_gesture)

                # Check for pointing gesture
                if self._is_pointing_gesture(hand_landmarks):
                    gesture_data['is_pointing'] = True
                    gesture_data['pointing_direction'] = self._get_pointing_direction(
                        hand_landmarks, image.shape
                    )
                    gesture_data['confidence'] = hand_gesture['confidence']

        return gesture_data

    def _analyze_hand_gesture(self, landmarks, image_shape) -> Dict:
        """Analyze the hand gesture based on landmarks."""
        # Get specific landmark coordinates
        thumb_tip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        index_finger_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_finger_tip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_finger_tip = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]

        wrist = landmarks.landmark[self.mp_hands.HandLandmark.WRIST]

        # Convert normalized coordinates to pixel coordinates
        h, w, c = image_shape
        thumb_px = (int(thumb_tip.x * w), int(thumb_tip.y * h))
        index_px = (int(index_finger_tip.x * w), int(index_finger_tip.y * h))
        middle_px = (int(middle_finger_tip.x * w), int(middle_finger_tip.y * h))
        ring_px = (int(ring_finger_tip.x * w), int(ring_finger_tip.y * h))
        pinky_px = (int(pinky_tip.x * w), int(pinky_tip.y * h))
        wrist_px = (int(wrist.x * w), int(wrist.y * h))

        # Calculate finger positions relative to wrist
        index_rel = (index_px[0] - wrist_px[0], index_px[1] - wrist_px[1])
        middle_rel = (middle_px[0] - wrist_px[0], middle_px[1] - wrist_px[1])
        ring_rel = (ring_px[0] - wrist_px[0], ring_px[1] - wrist_px[1])
        pinky_rel = (pinky_px[0] - wrist_px[0], pinky_px[1] - wrist_px[1])

        # Determine gesture type based on finger positions
        gesture_type = self._classify_gesture(
            index_rel, middle_rel, ring_rel, pinky_rel, index_px, wrist_px
        )

        # Calculate confidence based on landmark positions
        confidence = min(
            thumb_tip.z, index_finger_tip.z, middle_finger_tip.z,
            ring_finger_tip.z, pinky_tip.z
        )
        confidence = max(0.0, abs(confidence))  # Normalize confidence

        return {
            'gesture_type': gesture_type,
            'confidence': 1.0 - confidence,  # Invert since negative z values indicate confidence
            'landmarks': {
                'thumb_tip': thumb_px,
                'index_finger_tip': index_px,
                'middle_finger_tip': middle_px,
                'ring_finger_tip': ring_px,
                'pinky_tip': pinky_px,
                'wrist': wrist_px
            },
            'relative_positions': {
                'index': index_rel,
                'middle': middle_rel,
                'ring': ring_rel,
                'pinky': pinky_rel
            }
        }

    def _classify_gesture(self, index_rel, middle_rel, ring_rel, pinky_rel, index_pos, wrist_pos) -> str:
        """Classify the gesture based on finger positions."""
        # Simple gesture classification
        if self._is_pointing_gesture_simple(index_rel, middle_rel, ring_rel, pinky_rel):
            return 'pointing'
        elif self._is_thumb_up(index_rel, middle_rel, ring_rel, pinky_rel):
            return 'thumb_up'
        elif self._is_fist(index_rel, middle_rel, ring_rel, pinky_rel):
            return 'fist'
        elif self._is_open_palm(index_rel, middle_rel, ring_rel, pinky_rel):
            return 'open_palm'
        else:
            return 'unknown'

    def _is_pointing_gesture_simple(self, index_rel, middle_rel, ring_rel, pinky_rel) -> bool:
        """Check if the gesture is a pointing gesture (index finger extended, others bent)."""
        # Index finger should be extended (away from palm)
        index_extended = index_rel[1] < -20  # Index finger higher than wrist (on screen)

        # Other fingers should be bent (closer to palm/wrist)
        middle_bent = middle_rel[1] > -10
        ring_bent = ring_rel[1] > -10
        pinky_bent = pinky_rel[1] > -10

        return index_extended and middle_bent and ring_bent and pinky_bent

    def _is_pointing_gesture(self, landmarks) -> bool:
        """Check if the hand is in a pointing gesture."""
        # Get landmark positions
        index_finger_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        index_finger_pip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
        middle_finger_tip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        middle_finger_pip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP]

        # Check if index finger is extended and middle finger is bent
        index_extended = index_finger_tip.y < index_finger_pip.y
        middle_bent = middle_finger_tip.y > middle_finger_pip.y

        # Additional checks for other fingers being bent
        thumb_tip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        thumb_ip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP]
        thumb_extended = thumb_tip.x > thumb_ip.x  # Thumb might be extended for pointing

        ring_tip = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
        ring_pip = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP]
        ring_bent = ring_tip.y > ring_pip.y

        pinky_tip = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]
        pinky_pip = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_PIP]
        pinky_bent = pinky_tip.y > pinky_pip.y

        return (index_extended and middle_bent and ring_bent and pinky_bent) or \
               (index_extended and ring_bent and pinky_bent and not middle_bent)

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
        magnitude = max(1, math.sqrt(dx*dx + dy*dy))
        normalized_dx = dx / magnitude
        normalized_dy = dy / magnitude

        # Calculate angle in degrees
        angle_degrees = math.degrees(math.atan2(dy, dx))
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

    def _is_thumb_up(self, index_rel, middle_rel, ring_rel, pinky_rel) -> bool:
        """Check if the gesture is a thumb up."""
        # For simplicity, checking if thumb is extended upward
        # This would need more sophisticated analysis in practice
        return False  # Placeholder

    def _is_fist(self, index_rel, middle_rel, ring_rel, pinky_rel) -> bool:
        """Check if the gesture is a fist."""
        # All fingers should be bent toward the palm
        fingers_bent = all(rel[1] > 0 for rel in [index_rel, middle_rel, ring_rel, pinky_rel])
        return fingers_bent

    def _is_open_palm(self, index_rel, middle_rel, ring_rel, pinky_rel) -> bool:
        """Check if the gesture is an open palm."""
        # All fingers should be extended away from the palm
        fingers_extended = all(rel[1] < 0 for rel in [index_rel, middle_rel, ring_rel, pinky_rel])
        return fingers_extended

class GestureDetectorNode(Node):
    """
    ROS 2 node for gesture detection and recognition.
    """

    def __init__(self):
        super().__init__('gesture_detector')

        # Initialize gesture detector
        self.gesture_detector = HandGestureDetector()
        self.cv_bridge = CvBridge()

        # Publishers
        self.gesture_pub = self.create_publisher(String, 'hand_gestures', 10)
        self.pointing_pub = self.create_publisher(Point, 'pointing_direction', 10)

        # Subscribers
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10)

        self.get_logger().info("Gesture Detector initialized")

    def image_callback(self, msg: Image):
        """Handle incoming camera images for gesture detection."""
        try:
            # Convert ROS image to OpenCV format
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Detect gestures
            gesture_data = self.gesture_detector.detect_gestures(cv_image)

            # Publish gesture data
            gesture_msg = String()
            gesture_msg.data = json.dumps(gesture_data)
            self.gesture_pub.publish(gesture_msg)

            # If pointing detected, publish direction
            if gesture_data['is_pointing'] and gesture_data['pointing_direction']:
                pointing_direction = gesture_data['pointing_direction']
                point_msg = Point()
                point_msg.x = pointing_direction['normalized_vector'][0]
                point_msg.y = pointing_direction['normalized_vector'][1]
                point_msg.z = gesture_data['confidence']
                self.pointing_pub.publish(point_msg)

                self.get_logger().info(f"Pointing detected: {pointing_direction['direction']} "
                                     f"(angle: {pointing_direction['angle_degrees']:.1f}°)")

        except Exception as e:
            self.get_logger().error(f"Error in gesture detection: {e}")

def main(args=None):
    rclpy.init(args=args)

    gesture_node = GestureDetectorNode()

    try:
        rclpy.spin(gesture_node)
    except KeyboardInterrupt:
        print("Shutting down gesture detector...")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 6. Phase 5: ROS 2 Integration and Action Execution (Days 17-21)

### 6.1 Action Executor System

Now let's implement the ROS 2 action execution system that will translate high-level plans into actual robot actions:

```python
#!/usr/bin/env python3
"""
capstone_project/src/ros_integration/action_executor.py
ROS 2 Action Executor for Executing Decomposed Plans
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Point, PoseStamped
from sensor_msgs.msg import JointState
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import json
from typing import Dict, List, Optional
import time
import threading
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NavigationExecutor:
    """
    Handles navigation tasks using Nav2.
    """

    def __init__(self, node: Node):
        self.node = node
        self.nav_client = ActionClient(node, NavigateToPose, 'navigate_to_pose')

        # Wait for navigation server
        self.nav_client.wait_for_server()
        self.node.get_logger().info("Navigation client connected")

    def execute_navigation(self, location: str, coordinates: Dict = None) -> bool:
        """
        Execute navigation to specified location.

        Args:
            location: Named location or coordinates
            coordinates: Dictionary with x, y, theta values

        Returns:
            True if successful, False otherwise
        """
        try:
            # For named locations, we'd have a map of location names to coordinates
            # For now, we'll use coordinates if provided, otherwise default
            if coordinates:
                goal_x = coordinates.get('x', 0.0)
                goal_y = coordinates.get('y', 0.0)
                goal_theta = coordinates.get('theta', 0.0)
            else:
                # Default coordinates for demonstration
                location_coords = {
                    'kitchen': {'x': 2.0, 'y': 1.0, 'theta': 0.0},
                    'living_room': {'x': -1.0, 'y': 2.0, 'theta': 1.57},
                    'bedroom': {'x': 0.0, 'y': -2.0, 'theta': 3.14},
                    'office': {'x': -2.0, 'y': -1.0, 'theta': -1.57}
                }

                coords = location_coords.get(location.lower(), {'x': 0.0, 'y': 0.0, 'theta': 0.0})
                goal_x, goal_y, goal_theta = coords['x'], coords['y'], coords['theta']

            # Create navigation goal
            goal_msg = NavigateToPose.Goal()
            goal_msg.pose.header.frame_id = 'map'
            goal_msg.pose.header.stamp = self.node.get_clock().now().to_msg()

            # Set position
            goal_msg.pose.pose.position.x = goal_x
            goal_msg.pose.pose.position.y = goal_y
            goal_msg.pose.pose.position.z = 0.0

            # Set orientation (convert theta to quaternion)
            import math
            from tf_transformations import quaternion_from_euler
            quat = quaternion_from_euler(0, 0, goal_theta)
            goal_msg.pose.pose.orientation.x = quat[0]
            goal_msg.pose.pose.orientation.y = quat[1]
            goal_msg.pose.pose.orientation.z = quat[2]
            goal_msg.pose.pose.orientation.w = quat[3]

            # Send goal
            self.node.get_logger().info(f"Sending navigation goal to ({goal_x}, {goal_y})")

            future = self.nav_client.send_goal_async(goal_msg)

            # Wait for result (with timeout)
            rclpy.spin_until_future_complete(self.node, future, timeout_sec=30.0)

            if future.result() is not None:
                goal_handle = future.result()
                if goal_handle.accepted:
                    result_future = goal_handle.get_result_async()
                    rclpy.spin_until_future_complete(self.node, result_future, timeout_sec=60.0)

                    if result_future.result() is not None:
                        result = result_future.result().result
                        status = result_future.result().status

                        if status == GoalStatus.STATUS_SUCCEEDED:
                            self.node.get_logger().info("Navigation succeeded")
                            return True
                        else:
                            self.node.get_logger().error(f"Navigation failed with status: {status}")
                            return False
                    else:
                        self.node.get_logger().error("Navigation result future timed out")
                        return False
                else:
                    self.node.get_logger().error("Navigation goal was rejected")
                    return False
            else:
                self.node.get_logger().error("Navigation goal future timed out")
                return False

        except Exception as e:
            self.node.get_logger().error(f"Error in navigation execution: {e}")
            return False

class ManipulationExecutor:
    """
    Handles manipulation tasks using joint trajectory control.
    """

    def __init__(self, node: Node):
        self.node = node

        # Joint trajectory action client for arm control
        self.arm_client = ActionClient(node, FollowJointTrajectory, 'arm_controller/follow_joint_trajectory')
        self.gripper_client = ActionClient(node, FollowJointTrajectory, 'gripper_controller/follow_joint_trajectory')

        # Publishers for direct joint control
        self.joint_pub = self.node.create_publisher(JointState, 'joint_states', 10)

        # Wait for servers
        self.arm_client.wait_for_server()
        self.gripper_client.wait_for_server()
        self.node.get_logger().info("Manipulation clients connected")

    def execute_manipulation(self, action: str, parameters: Dict) -> bool:
        """
        Execute manipulation action.

        Args:
            action: Type of manipulation (grasp, release, move_arm, etc.)
            parameters: Action parameters

        Returns:
            True if successful, False otherwise
        """
        try:
            if 'grasp' in action.lower() or 'pick' in action.lower():
                return self._execute_grasp(parameters)
            elif 'release' in action.lower() or 'drop' in action.lower():
                return self._execute_release(parameters)
            elif 'move_arm' in action.lower():
                return self._execute_arm_movement(parameters)
            else:
                self.node.get_logger().warn(f"Unknown manipulation action: {action}")
                return False

        except Exception as e:
            self.node.get_logger().error(f"Error in manipulation execution: {e}")
            return False

    def _execute_grasp(self, parameters: Dict) -> bool:
        """Execute grasp action."""
        try:
            # Move arm to object position
            object_pos = parameters.get('object_position', {'x': 0.5, 'y': 0.0, 'z': 0.2})

            # Create trajectory for grasping
            trajectory = self._create_grasp_trajectory(object_pos)

            # Send to arm controller
            goal_msg = FollowJointTrajectory.Goal()
            goal_msg.trajectory = trajectory

            future = self.arm_client.send_goal_async(goal_msg)
            rclpy.spin_until_future_complete(self.node, future, timeout_sec=30.0)

            if future.result() is not None:
                goal_handle = future.result()
                if goal_handle.accepted:
                    result_future = goal_handle.get_result_async()
                    rclpy.spin_until_future_complete(self.node, result_future, timeout_sec=30.0)

                    if result_future.result() is not None:
                        status = result_future.result().status
                        return status == GoalStatus.STATUS_SUCCEEDED

            # Close gripper after positioning
            gripper_trajectory = self._create_gripper_close_trajectory()
            gripper_goal = FollowJointTrajectory.Goal()
            gripper_goal.trajectory = gripper_trajectory

            gripper_future = self.gripper_client.send_goal_async(gripper_goal)
            rclpy.spin_until_future_complete(self.node, gripper_future, timeout_sec=10.0)

            if gripper_future.result() is not None:
                gripper_goal_handle = gripper_future.result()
                if gripper_goal_handle.accepted:
                    gripper_result_future = gripper_goal_handle.get_result_async()
                    rclpy.spin_until_future_complete(self.node, gripper_result_future, timeout_sec=10.0)

                    if gripper_result_future.result() is not None:
                        status = gripper_result_future.result().status
                        return status == GoalStatus.STATUS_SUCCEEDED

            return True

        except Exception as e:
            self.node.get_logger().error(f"Error in grasp execution: {e}")
            return False

    def _execute_release(self, parameters: Dict) -> bool:
        """Execute release action."""
        try:
            # Open gripper
            gripper_trajectory = self._create_gripper_open_trajectory()
            gripper_goal = FollowJointTrajectory.Goal()
            gripper_goal.trajectory = gripper_trajectory

            gripper_future = self.gripper_client.send_goal_async(gripper_goal)
            rclpy.spin_until_future_complete(self.node, gripper_future, timeout_sec=10.0)

            if gripper_future.result() is not None:
                gripper_goal_handle = gripper_future.result()
                if gripper_goal_handle.accepted:
                    gripper_result_future = gripper_goal_handle.get_result_async()
                    rclpy.spin_until_future_complete(self.node, gripper_result_future, timeout_sec=10.0)

                    if gripper_result_future.result() is not None:
                        status = gripper_result_future.result().status
                        if status == GoalStatus.STATUS_SUCCEEDED:
                            # Move arm away after releasing
                            retract_pos = parameters.get('retract_position', {'x': 0.6, 'y': 0.0, 'z': 0.3})
                            retract_traj = self._create_retract_trajectory(retract_pos)

                            retract_goal = FollowJointTrajectory.Goal()
                            retract_goal.trajectory = retract_traj

                            retract_future = self.arm_client.send_goal_async(retract_goal)
                            rclpy.spin_until_future_complete(self.node, retract_future, timeout_sec=20.0)

                            if retract_future.result() is not None:
                                retract_goal_handle = retract_future.result()
                                if retract_goal_handle.accepted:
                                    retract_result_future = retract_goal_handle.get_result_async()
                                    rclpy.spin_until_future_complete(self.node, retract_result_future, timeout_sec=20.0)

                                    if retract_result_future.result() is not None:
                                        status = retract_result_future.result().status
                                        return status == GoalStatus.STATUS_SUCCEEDED

            return True

        except Exception as e:
            self.node.get_logger().error(f"Error in release execution: {e}")
            return False

    def _create_grasp_trajectory(self, position: Dict) -> JointTrajectory:
        """Create trajectory for grasping motion."""
        # This is a simplified example - real implementation would need inverse kinematics
        trajectory = JointTrajectory()
        trajectory.joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
                                 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']

        point = JointTrajectoryPoint()
        point.positions = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]  # Example positions
        point.velocities = [0.0] * 6
        point.accelerations = [0.0] * 6
        point.time_from_start.sec = 5
        point.time_from_start.nanosec = 0

        trajectory.points.append(point)
        return trajectory

    def _create_gripper_close_trajectory(self) -> JointTrajectory:
        """Create trajectory for closing gripper."""
        trajectory = JointTrajectory()
        trajectory.joint_names = ['gripper_joint']

        point = JointTrajectoryPoint()
        point.positions = [0.01]  # Closed position
        point.velocities = [0.0]
        point.accelerations = [0.0]
        point.time_from_start.sec = 2
        point.time_from_start.nanosec = 0

        trajectory.points.append(point)
        return trajectory

    def _create_gripper_open_trajectory(self) -> JointTrajectory:
        """Create trajectory for opening gripper."""
        trajectory = JointTrajectory()
        trajectory.joint_names = ['gripper_joint']

        point = JointTrajectoryPoint()
        point.positions = [0.05]  # Open position
        point.velocities = [0.0]
        point.accelerations = [0.0]
        point.time_from_start.sec = 2
        point.time_from_start.nanosec = 0

        trajectory.points.append(point)
        return trajectory

    def _create_retract_trajectory(self, position: Dict) -> JointTrajectory:
        """Create trajectory for retracting after manipulation."""
        trajectory = JointTrajectory()
        trajectory.joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
                                 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']

        point = JointTrajectoryPoint()
        point.positions = [0.0, -1.0, 0.0, -2.0, 0.0, 0.0]  # Example retracted positions
        point.velocities = [0.0] * 6
        point.accelerations = [0.0] * 6
        point.time_from_start.sec = 3
        point.time_from_start.nanosec = 0

        trajectory.points.append(point)
        return trajectory

class ActionExecutorNode(Node):
    """
    ROS 2 node for executing decomposed plans as ROS 2 actions.
    """

    def __init__(self):
        super().__init__('action_executor')

        # Initialize executors
        self.nav_executor = NavigationExecutor(self)
        self.manip_executor = ManipulationExecutor(self)

        # Publishers
        self.task_status_pub = self.create_publisher(String, 'task_status', 10)
        self.execution_feedback_pub = self.create_publisher(String, 'execution_feedback', 10)

        # Subscribers
        self.plan_sub = self.create_subscription(
            String, 'decomposed_plans', self.plan_callback, 10)

        # Task execution tracking
        self.active_tasks = {}
        self.task_lock = threading.Lock()

        self.get_logger().info("Action Executor initialized")

    def plan_callback(self, msg: String):
        """Handle incoming decomposed plans."""
        try:
            plan_data = json.loads(msg.data)
            decomposed_tasks = plan_data['decomposed_tasks']

            self.get_logger().info(f"Executing plan with {len(decomposed_tasks)} tasks")

            # Execute tasks in order
            for task in decomposed_tasks:
                self.execute_task(task)

        except Exception as e:
            self.get_logger().error(f"Error in plan callback: {e}")

    def execute_task(self, task: Dict):
        """Execute a single task."""
        task_id = task['id']
        task_type = task['type']
        action = task['action']
        parameters = task['parameters']

        self.get_logger().info(f"Executing task {task_id}: {action} ({task_type})")

        # Update task status
        self._publish_task_status(task_id, TaskStatus.EXECUTING.value)

        success = False
        try:
            if task_type == 'navigation':
                success = self.nav_executor.execute_navigation(action, parameters)
            elif task_type == 'manipulation':
                success = self.manip_executor.execute_manipulation(action, parameters)
            elif task_type == 'perception':
                success = self._execute_perception_task(action, parameters)
            elif task_type == 'interaction':
                success = self._execute_interaction_task(action, parameters)
            else:
                self.get_logger().warn(f"Unknown task type: {task_type}")
                success = False

        except Exception as e:
            self.get_logger().error(f"Error executing task {task_id}: {e}")
            success = False

        # Update final status
        final_status = TaskStatus.COMPLETED.value if success else TaskStatus.FAILED.value
        self._publish_task_status(task_id, final_status)

        # Publish execution feedback
        feedback = {
            'task_id': task_id,
            'success': success,
            'execution_time': task.get('estimated_duration', 10),
            'actual_outcome': 'completed' if success else 'failed'
        }

        feedback_msg = String()
        feedback_msg.data = json.dumps(feedback)
        self.execution_feedback_pub.publish(feedback_msg)

        if success:
            self.get_logger().info(f"Task {task_id} completed successfully")
        else:
            self.get_logger().error(f"Task {task_id} failed")

    def _execute_perception_task(self, action: str, parameters: Dict) -> bool:
        """Execute perception-related tasks."""
        # For perception tasks, we might trigger object detection or scene analysis
        # This is a placeholder - real implementation would involve vision processing
        self.get_logger().info(f"Perception task: {action}")

        # Simulate perception task completion
        time.sleep(2)  # Simulate processing time
        return True

    def _execute_interaction_task(self, action: str, parameters: Dict) -> bool:
        """Execute interaction tasks."""
        # For interaction tasks like speaking, playing sounds, etc.
        self.get_logger().info(f"Interaction task: {action}")

        # Simulate interaction task completion
        time.sleep(1)  # Simulate processing time
        return True

    def _publish_task_status(self, task_id: str, status: str):
        """Publish task status update."""
        status_data = {
            'task_id': task_id,
            'status': status,
            'timestamp': self.get_clock().now().to_msg().sec
        }

        status_msg = String()
        status_msg.data = json.dumps(status_data)
        self.task_status_pub.publish(status_msg)

def main(args=None):
    rclpy.init(args=args)

    executor_node = ActionExecutorNode()

    try:
        rclpy.spin(executor_node)
    except KeyboardInterrupt:
        print("Shutting down action executor...")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 7. Phase 6: System Integration and Testing (Days 22-25)

### 7.1 System Integration Launch File

Let's create a launch file to bring up the entire system:

```xml
<!-- capstone_project/launch/voice_control_system.launch.xml -->
<launch>
  <!-- Parameters -->
  <arg name="openai_api_key" default="$(env OPENAI_API_KEY '')"/>
  <arg name="model" default="gpt-4-turbo-preview"/>

  <!-- Main orchestrator -->
  <node pkg="capstone_project" exec="main.py" name="voice_control_orchestrator" output="screen">
    <param name="use_sim_time" value="false"/>
  </node>

  <!-- Voice recognition -->
  <node pkg="capstone_project" exec="whisper_node.py" name="whisper_node" output="screen">
    <param name="use_sim_time" value="false"/>
  </node>

  <!-- NLP processing -->
  <node pkg="capstone_project" exec="nlp_processor.py" name="nlp_processor" output="screen">
    <param name="use_sim_time" value="false"/>
  </node>

  <!-- Advanced intent classification -->
  <node pkg="capstone_project" exec="intent_classifier.py" name="advanced_intent_classifier" output="screen">
    <param name="use_sim_time" value="false"/>
    <param name="openai_api_key" value="$(var openai_api_key)"/>
    <param name="model" value="$(var model)"/>
  </node>

  <!-- Cognitive planning -->
  <node pkg="capstone_project" exec="cognitive_planner.py" name="cognitive_planner" output="screen">
    <param name="use_sim_time" value="false"/>
    <param name="openai_api_key" value="$(var openai_api_key)"/>
    <param name="model" value="$(var model)"/>
  </node>

  <!-- Task decomposition -->
  <node pkg="capstone_project" exec="task_decomposer.py" name="task_decomposer" output="screen">
    <param name="use_sim_time" value="false"/>
  </node>

  <!-- Vision processing -->
  <node pkg="capstone_project" exec="vision_processor.py" name="vision_processor" output="screen">
    <param name="use_sim_time" value="false"/>
  </node>

  <!-- Gesture detection -->
  <node pkg="capstone_project" exec="gesture_detector.py" name="gesture_detector" output="screen">
    <param name="use_sim_time" value="false"/>
  </node>

  <!-- Action execution -->
  <node pkg="capstone_project" exec="action_executor.py" name="action_executor" output="screen">
    <param name="use_sim_time" value="false"/>
  </node>

</launch>
```

### 7.2 Requirements File

Let's create a comprehensive requirements file:

```txt
# capstone_project/requirements.txt
# Core ROS 2 dependencies
rclpy>=3.0.0
std_msgs>=3.0.0
sensor_msgs>=3.0.0
geometry_msgs>=3.0.0
nav2_msgs>=1.0.0
control_msgs>=4.0.0
trajectory_msgs>=3.0.0
action_msgs>=1.0.0

# AI/ML Libraries
openai>=1.0.0
whisper==20231117
torch>=2.0.0
sentence-transformers>=2.2.0
scikit-learn>=1.3.0
numpy>=1.21.0
spacy>=3.6.0
en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.6.0/en_core_web_sm-3.6.0.tar.gz

# Computer Vision
opencv-python>=4.8.0
mediapipe>=0.10.0
cv-bridge>=3.0.0

# Utilities
requests>=2.31.0
tqdm>=4.65.0
matplotlib>=3.7.0
pandas>=2.0.0

# Development
pytest>=7.4.0
black>=23.7.0
flake8>=6.0.0
```

### 7.3 README Documentation

```markdown
# Voice-Controlled Humanoid Robot System

This project implements a complete voice-controlled humanoid robot system that integrates speech recognition, LLM cognitive planning, NLP processing, and multi-modal interaction.

## Features

- **Speech Recognition**: Real-time voice command processing using OpenAI Whisper
- **Intent Classification**: Advanced NLP-based intent recognition
- **Entity Extraction**: Named entity recognition for objects and locations
- **LLM Cognitive Planning**: High-level task planning using GPT-4/Claude
- **Multi-modal Interaction**: Vision and gesture-based input processing
- **ROS 2 Integration**: Seamless integration with ROS 2 navigation and manipulation
- **Safety Monitoring**: Built-in safety checks and emergency procedures

## Prerequisites

- ROS 2 Humble Hawksbill
- Python 3.8+
- OpenAI API key (for LLM planning)
- CUDA-compatible GPU (recommended for Whisper model)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd capstone_project
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

3. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

4. Build the ROS 2 package:
   ```bash
   colcon build
   source install/setup.bash
   ```

## Usage

### Launch the System

```bash
ros2 launch capstone_project voice_control_system.launch.xml
```

### Voice Commands

The system understands various voice commands:

- **Navigation**: "Go to the kitchen", "Navigate to the living room"
- **Manipulation**: "Pick up the red ball", "Grasp the cup"
- **Perception**: "Look at the table", "Find the keys"
- **Complex Tasks**: "Go to the kitchen and pick up the cup"

### System Architecture

The system follows a modular architecture with clear separation of concerns:

1. **Voice Input**: Microphone captures audio, Whisper converts to text
2. **NLP Processing**: Intent classification and entity extraction
3. **Cognitive Planning**: LLM generates high-level plans
4. **Task Decomposition**: Plans broken into executable tasks
5. **Multi-modal Integration**: Vision and gesture input combined
6. **Action Execution**: ROS 2 actions executed on robot

## Configuration

Configuration files are located in the `config/` directory:
- `whisper_config.yaml`: Whisper model settings
- `llm_config.yaml`: LLM parameters and API settings
- `system_config.yaml`: Overall system parameters

## Testing

Run unit tests:
```bash
pytest tests/
```

Run integration tests:
```bash
# Launch system in simulation
ros2 launch capstone_project voice_control_system.launch.xml use_sim_time:=true

# Run integration tests
python -m pytest tests/test_integration.py
```

## Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure OPENAI_API_KEY is properly set
2. **GPU Memory**: Reduce model size if experiencing memory issues
3. **Audio Quality**: Use high-quality microphone for better recognition
4. **Network Latency**: LLM calls may be slow over poor connections

### Performance Tuning

- Use GPU acceleration for Whisper model
- Adjust confidence thresholds in NLP components
- Optimize camera resolution for vision processing
- Tune task execution timeouts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for Whisper and GPT models
- NVIDIA for Isaac Sim and CUDA
- ROS 2 community for robot operating system
- spaCy for NLP processing
- MediaPipe for gesture detection
```

## 8. Phase 7: Evaluation and Optimization (Days 26-28)

### 8.1 Performance Metrics and Evaluation

Let's create an evaluation script to test the system:

```python
#!/usr/bin/env python3
"""
capstone_project/evaluation/system_evaluator.py
System Evaluation and Performance Metrics
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import time
from collections import defaultdict
from typing import Dict, List, Tuple
import statistics

class SystemEvaluator:
    """
    Evaluates system performance and generates metrics.
    """

    def __init__(self):
        self.metrics = {
            'response_times': [],
            'accuracy_rates': [],
            'success_rates': [],
            'error_rates': [],
            'throughput': [],
            'resource_usage': []
        }

        self.test_scenarios = [
            {
                'name': 'Simple Navigation',
                'command': 'Go to the kitchen',
                'expected_actions': ['navigation'],
                'timeout': 30
            },
            {
                'name': 'Simple Manipulation',
                'command': 'Pick up the red ball',
                'expected_actions': ['navigation', 'manipulation'],
                'timeout': 60
            },
            {
                'name': 'Complex Task',
                'command': 'Go to the kitchen and pick up the cup',
                'expected_actions': ['navigation', 'manipulation'],
                'timeout': 90
            },
            {
                'name': 'Perception Task',
                'command': 'Look at the table and find the keys',
                'expected_actions': ['perception'],
                'timeout': 45
            }
        ]

    def evaluate_response_time(self, start_time: float, end_time: float) -> float:
        """Calculate response time."""
        return end_time - start_time

    def evaluate_accuracy(self, expected: str, actual: str) -> float:
        """Evaluate accuracy of command interpretation."""
        # Simple string similarity for demonstration
        if expected.lower() == actual.lower():
            return 1.0

        # More sophisticated comparison would go here
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())

        intersection = expected_words.intersection(actual_words)
        union = expected_words.union(actual_words)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def evaluate_success_rate(self, tasks_completed: int, tasks_total: int) -> float:
        """Calculate success rate."""
        if tasks_total == 0:
            return 0.0
        return tasks_completed / tasks_total

    def generate_report(self) -> Dict:
        """Generate comprehensive evaluation report."""
        report = {
            'timestamp': time.time(),
            'summary': {
                'avg_response_time': statistics.mean(self.metrics['response_times']) if self.metrics['response_times'] else 0,
                'median_response_time': statistics.median(self.metrics['response_times']) if self.metrics['response_times'] else 0,
                'avg_accuracy': statistics.mean(self.metrics['accuracy_rates']) if self.metrics['accuracy_rates'] else 0,
                'avg_success_rate': statistics.mean(self.metrics['success_rates']) if self.metrics['success_rates'] else 0,
                'avg_error_rate': statistics.mean(self.metrics['error_rates']) if self.metrics['error_rates'] else 0,
            },
            'detailed_metrics': self.metrics,
            'recommendations': self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []

        avg_response = statistics.mean(self.metrics['response_times']) if self.metrics['response_times'] else 0
        avg_accuracy = statistics.mean(self.metrics['accuracy_rates']) if self.metrics['accuracy_rates'] else 0
        avg_success = statistics.mean(self.metrics['success_rates']) if self.metrics['success_rates'] else 0

        if avg_response > 5.0:
            recommendations.append("Response time is high (>5s). Consider optimizing LLM calls or using caching.")

        if avg_accuracy < 0.8:
            recommendations.append("Accuracy is low (<80%). Improve NLP training data or adjust confidence thresholds.")

        if avg_success < 0.9:
            recommendations.append("Success rate is low (<90%). Investigate task execution failures and improve error handling.")

        if not recommendations:
            recommendations.append("System performance is satisfactory. Consider adding more test scenarios.")

        return recommendations

class SystemEvaluationNode(Node):
    """
    ROS 2 node for system evaluation and metrics collection.
    """

    def __init__(self):
        super().__init__('system_evaluation')

        # Initialize evaluator
        self.evaluator = SystemEvaluator()

        # Publishers
        self.metrics_pub = self.create_publisher(String, 'system_metrics', 10)
        self.evaluation_report_pub = self.create_publisher(String, 'evaluation_report', 10)

        # Subscribers
        self.command_sub = self.create_subscription(
            String, 'transcribed_text', self.command_callback, 10)
        self.response_sub = self.create_subscription(
            String, 'execution_feedback', self.response_callback, 10)

        # Timer for periodic evaluation reports
        self.report_timer = self.create_timer(60.0, self.publish_evaluation_report)

        # Track timing
        self.command_timestamps = {}

        self.get_logger().info("System Evaluation initialized")

    def command_callback(self, msg: String):
        """Track command timestamps."""
        command_hash = hash(msg.data)
        self.command_timestamps[command_hash] = time.time()

    def response_callback(self, msg: String):
        """Process response and calculate metrics."""
        try:
            feedback = json.loads(msg.data)

            # Calculate response time
            command_hash = hash(feedback.get('original_command', ''))
            if command_hash in self.command_timestamps:
                response_time = time.time() - self.command_timestamps[command_hash]
                self.evaluator.metrics['response_times'].append(response_time)

                # Clean up timestamp
                del self.command_timestamps[command_hash]

            # Calculate success rate
            success = feedback.get('success', False)
            self.evaluator.metrics['success_rates'].append(1.0 if success else 0.0)

            # Calculate error rate
            self.evaluator.metrics['error_rates'].append(0.0 if success else 1.0)

            # Publish current metrics
            metrics_msg = String()
            metrics_msg.data = json.dumps({
                'response_time': response_time if 'response_time' in locals() else 0,
                'success': success,
                'timestamp': time.time()
            })
            self.metrics_pub.publish(metrics_msg)

        except Exception as e:
            self.get_logger().error(f"Error processing response feedback: {e}")

    def publish_evaluation_report(self):
        """Publish periodic evaluation report."""
        try:
            report = self.evaluator.generate_report()

            report_msg = String()
            report_msg.data = json.dumps(report, indent=2)
            self.evaluation_report_pub.publish(report_msg)

            self.get_logger().info(f"Evaluation report published: {report['summary']}")

        except Exception as e:
            self.get_logger().error(f"Error publishing evaluation report: {e}")

def main(args=None):
    rclpy.init(args=args)

    eval_node = SystemEvaluationNode()

    try:
        rclpy.spin(eval_node)
    except KeyboardInterrupt:
        print("Shutting down system evaluation...")
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 9. Assessment Questions

### 9.1 Traditional Assessment Questions

1. What are the main components of the voice-controlled humanoid robot system?
2. Explain the role of LLM cognitive planning in the system architecture.
3. How does the multi-modal interaction system integrate voice, vision, and gesture inputs?
4. Describe the process of decomposing high-level plans into executable tasks.
5. What safety mechanisms are implemented in the system?
6. How does the system handle context-aware intent classification?
7. What are the key performance metrics for evaluating the system?
8. Explain the difference between navigation and manipulation tasks in the system.
9. How does the NLP processing pipeline extract entities from voice commands?
10. What are the main challenges in real-time voice command processing?

### 9.2 Knowledge Check Assessment Questions

1. True/False: The system uses OpenAI Whisper for speech recognition.
2. Multiple Choice: Which of the following is NOT a main component of the system?
   a) Voice Recognition
   b) LLM Cognitive Planning
   c) Blockchain Integration
   d) Multi-modal Interaction
3. Short Answer: What is the purpose of the task decomposer component?
4. True/False: The system can handle complex commands that combine navigation and manipulation.
5. Multiple Choice: Which Python library is used for sentence embeddings in intent classification?
   a) scikit-learn
   b) sentence-transformers
   c) transformers
   d) all of the above
6. Short Answer: How does the gesture detection system identify pointing gestures?
7. True/False: The system requires an internet connection for all operations.
8. Multiple Choice: What is the primary purpose of the system orchestrator?
   a) Voice recognition only
   b) Coordinate all subsystems
   c) Execute navigation tasks
   d) Process vision data
9. Short Answer: Name three types of tasks that the action executor can handle.
10. True/False: The system includes performance evaluation and metrics collection capabilities.

## Conclusion

The Voice-Controlled Humanoid Robot System represents a comprehensive integration of modern AI technologies with robotic systems. This capstone project demonstrates the practical application of speech recognition, natural language processing, large language models, computer vision, and gesture recognition in creating an intelligent robotic assistant.

The system architecture provides a modular, extensible foundation that can be adapted for various applications, from home assistance to industrial automation. Through careful integration of these technologies, we've created a robot system capable of understanding and executing complex voice commands in real-world environments.

The project emphasizes safety, reliability, and performance, incorporating multiple layers of error handling and system monitoring. The evaluation framework ensures continuous improvement and optimization of system capabilities.

Future enhancements could include multi-language support, improved contextual understanding, enhanced safety protocols, and expanded task capabilities for more complex robotic operations.

This capstone project serves as a complete example of how to build sophisticated AI-powered robotic systems that can interact naturally with humans through voice commands while maintaining the precision and reliability required for autonomous operation.