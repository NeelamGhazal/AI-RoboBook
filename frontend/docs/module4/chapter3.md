---
sidebar_label: 'Chapter 3: NLP to ROS 2 Actions'
sidebar_position: 3
---

# Chapter 3: NLP to ROS 2 Actions

## Learning Objectives

By the end of this chapter, you will be able to:

1. Understand intent classification and entity extraction
2. Build NLP pipelines for robot command parsing
3. Map natural language to ROS 2 action parameters
4. Handle ambiguous and incomplete commands
5. Implement slot filling for missing parameters
6. Create robust error handling for misunder

stood commands
7. Optimize NLP for real-time robot interaction

---

## 1. Natural Language Understanding for Robots

### 1.1 NLP Pipeline Overview

```mermaid
graph LR
    A[Voice Input<br/>"Go to kitchen"] --> B[Speech Recognition<br/>Whisper]
    B --> C[Text Normalization<br/>Lowercase, Clean]
    C --> D[Intent Classification<br/>Navigate]
    D --> E[Entity Extraction<br/>location=kitchen]
    E --> F[Slot Filling<br/>Complete Parameters]
    F --> G[Action Mapping<br/>ROS 2 Goal]
    G --> H[Execution<br/>Robot Moves]

    style A fill:#0f1729,stroke:#00d4ff,stroke-width:2px,color:#fff
    style D fill:#1a1f3a,stroke:#00d4ff,stroke-width:2px,color:#fff
    style H fill:#0f1729,stroke:#0ea5e9,stroke-width:2px,color:#fff
```

### 1.2 Key NLP Tasks

| Task | Purpose | Example |
|------|---------|---------|
| **Intent Classification** | What action to perform | "navigate", "grasp", "follow" |
| **Entity Extraction** | Extract parameters | location="kitchen", object="cup" |
| **Slot Filling** | Request missing info | "Navigate where?" if location missing |
| **Coreference Resolution** | Resolve pronouns | "it" → "the cup" |
| **Disambiguation** | Clarify ambiguity | "left" → "turn left" or "left object"? |

---

## 2. Intent Classification

### 2.1 Rule-Based Approach

```python
"""
Simple rule-based intent classifier.
"""

import re

class IntentClassifier:
    """Classify user intent from natural language."""

    def __init__(self):
        # Define intent patterns
        self.patterns = {
            'navigate': [
                r'(go|move|navigate|drive|head) to',
                r'take me to',
                r'bring me to',
            ],
            'grasp': [
                r'(pick|grab|grasp|get) (?:up |the )?(\w+)',
                r'take (?:the )?(\w+)',
            ],
            'place': [
                r'(put|place|set) (?:the )?(\w+) (?:on|in|at)',
                r'leave (?:the )?(\w+)',
            ],
            'follow': [
                r'follow (me|the \w+)',
                r'come with me',
            ],
            'stop': [
                r'stop',
                r'halt',
                r'freeze',
            ],
        }

    def classify(self, text):
        """Classify intent from text."""
        text = text.lower().strip()

        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent

        return 'unknown'

# Usage
classifier = IntentClassifier()
print(classifier.classify("Go to the kitchen"))  # navigate
print(classifier.classify("Pick up the cup"))     # grasp
```

### 2.2 ML-Based Classification

```python
"""
Machine learning intent classifier using sentence transformers.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class MLIntentClassifier:
    """ML-based intent classifier using embeddings."""

    def __init__(self):
        # Load pre-trained sentence transformer
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Define intent examples (few-shot)
        self.intent_examples = {
            'navigate': [
                "go to the kitchen",
                "move to the living room",
                "navigate to the bedroom",
                "take me to the garage",
            ],
            'grasp': [
                "pick up the cup",
                "grab the bottle",
                "get the remote",
                "take the book",
            ],
            'place': [
                "put the cup on the table",
                "place the bottle in the fridge",
                "set the book on the shelf",
            ],
            'follow': [
                "follow me",
                "come with me",
                "follow the person",
            ],
        }

        # Compute embeddings for examples
        self.intent_embeddings = {}
        for intent, examples in self.intent_examples.items():
            embeddings = self.model.encode(examples)
            # Store mean embedding for intent
            self.intent_embeddings[intent] = np.mean(embeddings, axis=0)

    def classify(self, text, threshold=0.5):
        """Classify intent using semantic similarity."""
        # Encode input text
        text_embedding = self.model.encode([text])[0]

        # Compute similarity to each intent
        similarities = {}
        for intent, intent_emb in self.intent_embeddings.items():
            sim = cosine_similarity(
                [text_embedding],
                [intent_emb]
            )[0][0]
            similarities[intent] = sim

        # Get best match
        best_intent = max(similarities, key=similarities.get)
        best_score = similarities[best_intent]

        if best_score < threshold:
            return 'unknown', best_score

        return best_intent, best_score

# Usage
classifier = MLIntentClassifier()
intent, confidence = classifier.classify("move to the dining room")
print(f"Intent: {intent}, Confidence: {confidence:.2f}")
```

---

## 3. Entity Extraction

### 3.1 Named Entity Recognition (NER)

```python
"""
Extract entities (locations, objects) from commands.
"""

import spacy
import re

class EntityExtractor:
    """Extract entities from natural language commands."""

    def __init__(self):
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")

        # Define custom entity patterns
        self.location_keywords = ['kitchen', 'bedroom', 'living room', 'garage', 'office']
        self.object_keywords = ['cup', 'bottle', 'book', 'remote', 'phone', 'keys']

    def extract(self, text, intent):
        """Extract entities based on intent."""
        doc = self.nlp(text.lower())

        entities = {}

        if intent == 'navigate':
            # Extract location
            location = self.extract_location(text, doc)
            if location:
                entities['location'] = location

        elif intent == 'grasp':
            # Extract object
            obj = self.extract_object(text, doc)
            if obj:
                entities['object'] = obj

        elif intent == 'place':
            # Extract both object and location
            obj = self.extract_object(text, doc)
            location = self.extract_location(text, doc)
            if obj:
                entities['object'] = obj
            if location:
                entities['location'] = location

        return entities

    def extract_location(self, text, doc):
        """Extract location entity."""
        # Check for predefined locations
        for loc in self.location_keywords:
            if loc in text:
                return loc

        # Use NER to find locations
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC', 'FAC']:  # Geopolitical, location, facility
                return ent.text

        # Fallback: extract after "to"
        match = re.search(r'to (?:the )?(\w+[\s\w]*)', text)
        if match:
            return match.group(1).strip()

        return None

    def extract_object(self, text, doc):
        """Extract object entity."""
        # Check for predefined objects
        for obj in self.object_keywords:
            if obj in text:
                return obj

        # Extract after action verbs
        match = re.search(r'(?:pick|grab|get|grasp|take) (?:up |the )?(\w+)', text)
        if match:
            return match.group(1)

        # Use NER for objects
        for ent in doc.ents:
            if ent.label_ == 'PRODUCT':
                return ent.text

        return None

# Usage
extractor = EntityExtractor()
entities = extractor.extract("go to the kitchen", intent='navigate')
print(entities)  # {'location': 'kitchen'}
```

---

## 4. Complete NLP to ROS 2 Pipeline

### 4.1 Integrated System

```python
"""
Complete NLP pipeline for ROS 2 robot control.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from moveit_msgs.action import MoveGroup
import json

class NLPActionMapper(Node):
    """Map natural language commands to ROS 2 actions."""

    def __init__(self):
        super().__init__('nlp_action_mapper')

        # Initialize NLP components
        self.intent_classifier = MLIntentClassifier()
        self.entity_extractor = EntityExtractor()

        # Subscribe to voice commands
        self.subscription = self.create_subscription(
            String,
            'voice_commands',
            self.command_callback,
            10
        )

        # Publisher for action requests
        self.action_pub = self.create_publisher(String, 'robot_actions', 10)

        # Location database
        self.locations = {
            'kitchen': {'x': 5.0, 'y': 2.0, 'yaw': 0.0},
            'living room': {'x': 8.0, 'y': 5.0, 'yaw': 1.57},
            'bedroom': {'x': 2.0, 'y': 8.0, 'yaw': 3.14},
        }

        # Object database
        self.objects = {
            'cup': {'type': 'graspable', 'size': 'small'},
            'bottle': {'type': 'graspable', 'size': 'medium'},
            'book': {'type': 'graspable', 'size': 'large'},
        }

        # Conversation state (for slot filling)
        self.pending_action = None
        self.pending_slots = {}

        self.get_logger().info('NLP Action Mapper ready')

    def command_callback(self, msg):
        """Process voice command and map to action."""
        text = msg.data
        self.get_logger().info(f'Processing command: "{text}"')

        # 1. Classify intent
        intent, confidence = self.intent_classifier.classify(text)

        if intent == 'unknown':
            self.get_logger().warning(f'Unknown intent for: "{text}"')
            self.request_clarification(text)
            return

        self.get_logger().info(f'Intent: {intent} (confidence: {confidence:.2f})')

        # 2. Extract entities
        entities = self.entity_extractor.extract(text, intent)
        self.get_logger().info(f'Entities: {entities}')

        # 3. Check for missing required parameters
        required_params = self.get_required_params(intent)
        missing_params = [p for p in required_params if p not in entities]

        if missing_params:
            # Slot filling: request missing information
            self.request_missing_params(intent, entities, missing_params)
            return

        # 4. Map to robot action
        action = self.map_to_action(intent, entities)

        if action:
            # Publish action
            action_msg = String()
            action_msg.data = json.dumps(action)
            self.action_pub.publish(action_msg)

            self.get_logger().info(f'Executing action: {action["type"]}')
        else:
            self.get_logger().error('Failed to map command to action')

    def get_required_params(self, intent):
        """Get required parameters for intent."""
        requirements = {
            'navigate': ['location'],
            'grasp': ['object'],
            'place': ['object', 'location'],
            'follow': [],
            'stop': [],
        }
        return requirements.get(intent, [])

    def request_missing_params(self, intent, entities, missing_params):
        """Request missing parameters from user."""
        # Save state
        self.pending_action = intent
        self.pending_slots = entities.copy()

        # Generate clarification question
        param = missing_params[0]  # Ask for first missing param

        questions = {
            'location': "Where should I go?",
            'object': "Which object?",
        }

        question = questions.get(param, f"Please specify the {param}")
        self.get_logger().info(f'Requesting: {question}')

        # In a real system, publish question to TTS or display
        # User's next command should provide the missing param

    def map_to_action(self, intent, entities):
        """Map intent and entities to executable action."""
        action = {'type': intent}

        if intent == 'navigate':
            location_name = entities['location']
            if location_name in self.locations:
                coords = self.locations[location_name]
                action['parameters'] = {
                    'goal_pose': {
                        'x': coords['x'],
                        'y': coords['y'],
                        'yaw': coords['yaw']
                    }
                }
            else:
                self.get_logger().error(f'Unknown location: {location_name}')
                return None

        elif intent == 'grasp':
            object_name = entities['object']
            if object_name in self.objects:
                action['parameters'] = {
                    'object': object_name,
                    'object_type': self.objects[object_name]['type']
                }
            else:
                self.get_logger().error(f'Unknown object: {object_name}')
                return None

        elif intent == 'place':
            object_name = entities['object']
            location_name = entities['location']

            if object_name in self.objects and location_name in self.locations:
                action['parameters'] = {
                    'object': object_name,
                    'location': location_name
                }
            else:
                return None

        return action

def main(args=None):
    rclpy.init(args=args)
    node = NLPActionMapper()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

---

## 5. Handling Edge Cases

### 5.1 Ambiguity Resolution

```python
def resolve_ambiguity(self, text, entities):
    """Resolve ambiguous commands."""

    # Example: "left" could mean "turn left" or "left object"
    if "left" in text and "right" in text:
        # Clarify: direction or object selection?
        return self.ask_clarification("Did you mean turn left/right or select left/right object?")

    # Multiple objects detected
    if 'object' in entities and isinstance(entities['object'], list):
        objects = entities['object']
        return self.ask_selection(f"Which object? {', '.join(objects)}")

    return None
```

### 5.2 Error Recovery

```python
def handle_nlp_failure(self, text, error_type):
    """Recover from NLP failures."""

    recovery_strategies = {
        'no_intent': "I didn't understand that command. Try: 'go to kitchen' or 'pick up cup'",
        'missing_entity': "Please be more specific. Where should I go?",
        'invalid_entity': "I don't know that location. Available: kitchen, bedroom, living room",
        'ambiguous': "That command is ambiguous. Please rephrase.",
    }

    message = recovery_strategies.get(error_type, "Sorry, I didn't understand. Please try again.")
    self.get_logger().warning(f'NLP failure: {error_type}')

    # Send message to TTS or display
    return message
```

---

## Assessment Questions

### Traditional Questions

1. **What is the difference between intent classification and entity extraction?**
   - Answer: Intent classification determines what action the user wants (navigate, grasp, place). Entity extraction identifies specific parameters for that action (location="kitchen", object="cup"). Intent is the "what", entities are the "who/where/when".

2. **Compare rule-based and ML-based intent classification. When would you use each?**
   - Answer: Rule-based uses regex patterns—fast, deterministic, no training needed, but brittle and doesn't handle variations well. ML-based uses embeddings/models—handles paraphrasing and variations, requires examples/training, slightly slower. Use rules for limited, well-defined commands (industrial robots). Use ML for general-purpose consumer robots needing flexibility.

3. **Explain slot filling and why it's necessary for robot control.**
   - Answer: Slot filling requests missing required parameters from incomplete commands. E.g., "go to the" needs location slot filled. Necessary because natural speech is often incomplete, and robots need complete parameters to execute actions safely. Prevents errors from missing information.

4. **How would you handle the ambiguous command "turn left"?**
   - Answer: (1) Check context: is robot navigating (turn left = rotation) or selecting objects (left = leftmost object)? (2) Use intent classification: if intent=navigate, interpret as rotation. If intent=grasp, ask "which object? the left one or right one?" (3) Use conversation history: previous command provides context. (4) Default to most common interpretation with confirmation.

5. **Describe how to map extracted entities to ROS 2 action parameters.**
   - Answer: (1) Define mapping database (location names → coordinates), (2) Extract entities from NLP, (3) Look up entities in database (e.g., "kitchen" → x:5.0, y:2.0), (4) Format as ROS 2 message (PoseStamped for nav, target_pose for manipulation), (5) Validate parameters are within robot constraints, (6) Publish action goal to appropriate ROS 2 action server.

### Knowledge Check Questions

6. **Multiple Choice: Which NLP library provides pre-trained named entity recognition?**
   - A) NumPy
   - B) spaCy ✓
   - C) PyTorch
   - D) OpenCV
   - Answer: B. spaCy provides pre-trained NER models for extracting locations, objects, people, organizations, etc.

7. **True/False: Sentence transformers can classify intent without any training examples.**
   - Answer: False. Sentence transformers need few-shot examples for each intent class to compute reference embeddings. They match new inputs against these examples using semantic similarity.

8. **Fill in the blank: When a command is missing required parameters, the system should perform __________ to request the missing information.**
   - Answer: slot filling (or clarification, or interactive dialogue)

9. **Short Answer: Why use cosine similarity for intent classification instead of exact string matching?**
   - Answer: Cosine similarity measures semantic similarity between embeddings, allowing the system to match paraphrased or synonymous commands to the correct intent. "Go to kitchen" and "Navigate to the kitchen" have different words but similar embeddings. Exact matching would fail on variations.

10. **Scenario: User says "pick up the cup" but there are three cups visible. How should the NLP system handle this?**
    - Answer: (1) Detect multiple cup instances through perception, (2) Recognize ambiguity in entity extraction, (3) Request clarification: "I see three cups. Which one? The red cup, blue cup, or white cup?" or "Point to the cup you want", (4) Store conversation state while waiting for clarification, (5) Once specified, complete the grasp action with the selected cup.

---

## Summary

In this chapter, you learned about:

- **NLP Pipeline**: Intent classification, entity extraction, slot filling for robot commands
- **Intent Classification**: Rule-based patterns and ML-based semantic similarity
- **Entity Extraction**: Using spaCy NER and custom patterns for locations and objects
- **Complete Integration**: Full NLP to ROS 2 pipeline with real-time command processing
- **Edge Cases**: Handling ambiguity, missing parameters, and error recovery

NLP bridges the gap between human language and robot execution, enabling natural conversational control and reducing the need for complex UIs or programming.

---

**Next Chapter**: [Chapter 4: Multi-modal Interaction](./chapter4.md) - Combine vision, language, and sensor fusion for advanced human-robot interaction.
