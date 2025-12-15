#!/usr/bin/env python3
"""
nlp_processing_demo.py

Example demonstrating NLP processing for voice command understanding.
Shows intent classification and entity extraction using sentence transformers and spaCy.
"""

import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from typing import Dict, List, Tuple
import re

class IntentClassifier:
    """
    Intent classification using sentence embeddings.
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
                'Go to the entrance',
                'Drive to the kitchen',
                'Head to the bedroom',
                'Travel to the office'
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
                'Carry the bag',
                'Collect the keys',
                'Retrieve the remote'
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
                'Examine the bag',
                'Search for the keys',
                'Scan the room'
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
                'Dance',
                'Tell a joke',
                'Set an alarm'
            ]
        }

        # Pre-compute embeddings for all intent examples
        self.intent_embeddings = {}
        for intent, examples in self.intent_examples.items():
            example_embeddings = self.model.encode(examples)
            # Store mean embedding for the intent
            self.intent_embeddings[intent] = np.mean(example_embeddings, axis=0)

        print(f"Intent classifier initialized with {len(self.intent_examples)} intent types")

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

    def get_all_similarities(self, text: str) -> Dict[str, float]:
        """Get similarity scores for all intents."""
        text_embedding = self.model.encode([text])[0]
        similarities = {}

        for intent, intent_embedding in self.intent_embeddings.items():
            similarity = cosine_similarity([text_embedding], [intent_embedding])[0][0]
            similarities[intent] = similarity

        return similarities

class EntityExtractor:
    """
    Named Entity Recognition and Extraction using spaCy.
    Identifies locations, objects, and other entities in text.
    """

    def __init__(self):
        # Load English model for spaCy
        try:
            self.nlp = spacy.load('en_core_web_sm')
            print("spaCy English model loaded successfully")
        except OSError:
            print("Warning: spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            print("Using basic keyword-based extraction instead.")
            self.nlp = None

        # Define custom entity patterns
        self.location_patterns = [
            'kitchen', 'living room', 'bedroom', 'office', 'garage', 'hallway',
            'dining room', 'bathroom', 'garden', 'entrance', 'corridor',
            'study', 'patio', 'balcony', 'basement', 'attic', 'closet',
            'kitchen', 'pantry', 'laundry room', 'mudroom', 'sunroom'
        ]

        self.object_patterns = [
            'ball', 'cup', 'book', 'toy', 'box', 'chair', 'table', 'pen',
            'bottle', 'bag', 'laptop', 'phone', 'keys', 'wallet', 'hat',
            'glasses', 'watch', 'ring', 'jacket', 'shoes', 'umbrella',
            'remote', 'bowl', 'plate', 'fork', 'knife', 'spoon', 'napkin',
            'computer', 'tablet', 'camera', 'headphones', 'backpack'
        ]

        self.person_patterns = [
            'me', 'you', 'him', 'her', 'them', 'person', 'man', 'woman',
            'child', 'boy', 'girl', 'adult', 'someone', 'anyone'
        ]

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from the given text.

        Args:
            text: Input text to extract entities from

        Returns:
            Dictionary containing extracted entities
        """
        entities = {
            'locations': [],
            'objects': [],
            'persons': [],
            'quantities': [],
            'custom_entities': []
        }

        if self.nlp:
            # Use spaCy for advanced NER
            doc = self.nlp(text)

            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    entities['persons'].append(ent.text)
                elif ent.label_ == 'QUANTITY':
                    entities['quantities'].append(ent.text)
                elif ent.label_ == 'GPE':  # Geopolitical entity (could be extended for locations)
                    entities['locations'].append(ent.text)

        # Extract custom entities using pattern matching
        text_lower = text.lower()

        # Find locations using pattern matching
        for loc in self.location_patterns:
            if loc in text_lower:
                # Use regex to capture the full location phrase (handles multi-word locations)
                pattern = r'\b' + re.escape(loc) + r'\b'
                matches = re.findall(pattern, text_lower)
                entities['locations'].extend(matches)

        # Find objects
        for obj in self.object_patterns:
            if obj in text_lower:
                entities['objects'].append(obj)

        # Find persons
        for person in self.person_patterns:
            if person in text_lower:
                entities['persons'].append(person)

        # Remove duplicates while preserving order
        for key in entities:
            entities[key] = list(dict.fromkeys(entities[key]))

        return entities

class NLPProcessor:
    """
    Complete NLP processing pipeline combining intent classification and entity extraction.
    """

    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()

    def process_command(self, text: str) -> Dict:
        """
        Process a voice command through the complete NLP pipeline.

        Args:
            text: Input command text

        Returns:
            Dictionary with processed command information
        """
        # Classify intent
        intent, confidence = self.intent_classifier.classify(text)

        # Extract entities
        entities = self.entity_extractor.extract_entities(text)

        # Get detailed similarity scores
        all_similarities = self.intent_classifier.get_all_similarities(text)

        # Create processed command structure
        processed_command = {
            'raw_text': text,
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'all_intent_similarities': all_similarities,
            'timestamp': __import__('time').time()
        }

        return processed_command

    def batch_process(self, texts: List[str]) -> List[Dict]:
        """Process multiple texts at once."""
        return [self.process_command(text) for text in texts]

def main():
    """Main function to demonstrate NLP processing."""
    print("NLP Processing Demo for Voice Commands")
    print("=" * 50)

    # Initialize NLP processor
    nlp_processor = NLPProcessor()

    # Test commands
    test_commands = [
        "Go to the kitchen and pick up the red cup",
        "Navigate to the living room and find my keys",
        "Move to the bedroom and bring me the book",
        "Look at the table and locate the laptop",
        "Grasp the blue ball from the floor",
        "Turn on the lights in the office",
        "Take the remote control to the couch",
        "Find the bottle in the kitchen",
        "Move the chair to the dining room",
        "Say hello to everyone in the room"
    ]

    print(f"Processing {len(test_commands)} test commands...\n")

    for i, command in enumerate(test_commands, 1):
        print(f"Command {i}: {command}")
        print("-" * 40)

        # Process the command
        result = nlp_processor.process_command(command)

        # Display results
        print(f"Intent: {result['intent']} (confidence: {result['confidence']:.3f})")
        print(f"Entities: {result['entities']}")

        # Show all similarity scores
        print(f"All Intent Similarities:")
        sorted_similarities = sorted(result['all_intent_similarities'].items(),
                                   key=lambda x: x[1], reverse=True)
        for intent, score in sorted_similarities[:3]:  # Show top 3
            print(f"  {intent}: {score:.3f}")

        print()

    # Interactive mode
    print("Interactive Mode (type 'quit' to exit):")
    while True:
        try:
            user_command = input("\nEnter a voice command: ").strip()
            if user_command.lower() in ['quit', 'exit', 'q']:
                break

            if user_command:
                result = nlp_processor.process_command(user_command)

                print(f"\nProcessed Command: {result['raw_text']}")
                print(f"Intent: {result['intent']} (confidence: {result['confidence']:.3f})")
                print(f"Entities: {result['entities']}")

                # Show detailed breakdown
                print(f"\nDetailed Analysis:")
                print(f"  Intent Confidence: {result['confidence']:.3f}")
                print(f"  Locations: {result['entities']['locations']}")
                print(f"  Objects: {result['entities']['objects']}")
                print(f"  Persons: {result['entities']['persons']}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

    # Performance test
    print(f"\nPerformance Test:")
    import time

    test_batch = ["Go to the kitchen", "Pick up the cup", "Find the keys"] * 10  # 30 commands

    start_time = time.time()
    results = nlp_processor.batch_process(test_batch)
    end_time = time.time()

    processing_time = end_time - start_time
    avg_time_per_command = processing_time / len(test_batch)

    print(f"Processed {len(test_batch)} commands in {processing_time:.3f}s")
    print(f"Average time per command: {avg_time_per_command:.3f}s")
    print(f"Commands per second: {1/avg_time_per_command:.2f}")

    print("\nNLP Processing Demo completed!")

if __name__ == '__main__':
    main()