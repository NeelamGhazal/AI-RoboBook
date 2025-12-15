# Module 4: Voice Control and LLM Integration Examples

This directory contains code examples for Module 4 of the RoboBook textbook, focusing on voice-controlled humanoid robots with LLM cognitive planning, NLP processing, and multi-modal interaction.

## Examples Included

### 1. voice_control_demo.py
Complete example of a voice-controlled robot system that integrates:
- OpenAI Whisper for speech recognition
- LLM cognitive planning with GPT-4/Claude
- NLP intent classification and entity extraction
- Multi-modal interaction with vision and gestures
- ROS 2 action execution

### 2. llm_planning_demo.py
Demonstrates LLM-based cognitive planning for robotics:
- Shows how GPT-4/Claude generates high-level plans from natural language commands
- Includes plan validation and simulation
- Interactive mode for testing custom commands

### 3. nlp_processing_demo.py
Example of NLP processing for voice command understanding:
- Intent classification using sentence embeddings
- Entity extraction using spaCy
- Performance testing and interactive mode

### 4. multimodal_demo.py
Demonstrates multi-modal interaction combining voice, vision, and gesture inputs:
- Object detection and scene analysis
- Hand gesture recognition using MediaPipe
- Fusion of multiple input modalities

## Prerequisites

Before running these examples, ensure you have:

1. Python 3.8 or higher
2. ROS 2 Humble Hawksbill (for ROS 2 integration examples)
3. OpenAI API key (for LLM planning examples)
4. Required Python packages (see requirements.txt)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. If using spaCy models:
```bash
python -m spacy download en_core_web_sm
```

3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Voice Control Demo
```bash
python voice_control_demo.py
```

### LLM Planning Demo
```bash
python llm_planning_demo.py
```

### NLP Processing Demo
```bash
python nlp_processing_demo.py
```

### Multi-modal Demo
```bash
python multimodal_demo.py
```

## Configuration

Some examples may require configuration files or environment variables:
- Set `OPENAI_API_KEY` environment variable for LLM-based examples
- Adjust model parameters in the code as needed
- Configure ROS 2 parameters if using ROS integration

## Key Concepts Demonstrated

- **Speech Recognition**: Using OpenAI Whisper for real-time voice command processing
- **Intent Classification**: Machine learning-based classification of user intentions
- **Entity Extraction**: Identification of objects, locations, and parameters from voice commands
- **LLM Cognitive Planning**: High-level task decomposition using large language models
- **Multi-modal Interaction**: Integration of voice, vision, and gesture inputs
- **ROS 2 Integration**: Execution of plans as ROS 2 actions and services

## Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure OPENAI_API_KEY is properly set for LLM examples
2. **GPU Memory**: Reduce model size if experiencing memory issues with Whisper
3. **Audio Quality**: Use high-quality microphone for better speech recognition
4. **Network Latency**: LLM calls may be slow over poor connections

### Performance Tuning

- Use GPU acceleration for Whisper model when available
- Adjust confidence thresholds in NLP components
- Optimize camera resolution for vision processing
- Tune processing frequencies based on system capabilities

## Integration with ROS 2

The examples demonstrate integration with ROS 2 systems:
- Publishers and subscribers for different message types
- Action clients for navigation and manipulation
- Parameter management for configuration
- Node lifecycle management

## Contributing

These examples are designed to be educational and practical. Contributions are welcome:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the RoboBook textbook and is licensed under the MIT License - see the main repository for details.

## Acknowledgments

- OpenAI for Whisper and GPT models
- NVIDIA for Isaac Sim and CUDA
- ROS 2 community for robot operating system
- spaCy for NLP processing
- MediaPipe for gesture detection