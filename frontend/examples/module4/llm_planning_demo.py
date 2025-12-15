#!/usr/bin/env python3
"""
llm_planning_demo.py

Example demonstrating LLM-based cognitive planning for robotics.
Shows how GPT-4/Claude can generate high-level plans from natural language commands.
"""

import openai
import json
import os
from typing import Dict, List, Optional
import time

class LLMCognitivePlanner:
    """
    LLM-based cognitive planner that generates robot action plans from natural language.
    Uses GPT-4 or Claude for sophisticated planning and task decomposition.
    """

    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize the cognitive planner.

        Args:
            api_key: OpenAI API key (if not provided, will try to get from environment)
            model: LLM model to use for planning
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")

        openai.api_key = self.api_key
        self.model = model

        # Define system prompt for robotic planning
        self.system_prompt = """
You are an intelligent robot cognitive planner. Your job is to decompose high-level natural language commands into executable robot tasks.
Each plan should be a sequence of atomic actions that can be executed by a ROS 2 robot system.
Focus on navigation, manipulation, perception, and interaction tasks.
Return your response as valid JSON with the following structure:
{
    "plan_id": "unique identifier",
    "command": "original user command",
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
        "constraints": ["constraint1", ...],
        "safety_considerations": ["safety_point1", ...]
    },
    "metadata": {
        "confidence": 0.0-1.0,
        "reasoning": "brief explanation of planning decisions"
    }
}
Be precise, efficient, and consider safety constraints. Prioritize actions that ensure robot safety and successful task completion.
"""

    def generate_plan(self, command: str, context: Dict = None) -> Optional[Dict]:
        """
        Generate a plan for the given command using LLM.

        Args:
            command: Natural language command to plan for
            context: Additional context information (environment, robot state, etc.)

        Returns:
            Generated plan as dictionary, or None if failed
        """
        try:
            # Prepare the user message
            user_message = f"Generate a plan for this command: '{command}'"

            if context:
                user_message += f"\nAdditional context: {json.dumps(context, indent=2)}"

            print(f"Sending to LLM: {command}")

            # Call the LLM
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for more consistent outputs
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
        """
        Validate the generated plan structure and content.

        Args:
            plan: Plan dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['plan_id', 'command', 'tasks', 'context', 'metadata']
        if not all(field in plan for field in required_fields):
            return False

        # Validate tasks
        tasks = plan.get('tasks', [])
        for task in tasks:
            required_task_fields = ['id', 'type', 'action', 'parameters', 'estimated_duration']
            if not all(field in task for field in required_task_fields):
                print(f"Invalid task structure: {task}")
                return False

            valid_types = ['navigation', 'manipulation', 'perception', 'interaction', 'safety_check']
            if task['type'] not in valid_types:
                print(f"Invalid task type: {task['type']}")
                return False

        return True

    def execute_plan_simulation(self, plan: Dict):
        """
        Simulate execution of the plan (for demonstration purposes).

        Args:
            plan: Plan to simulate execution for
        """
        print(f"\n--- Executing Plan: {plan['command']} ---")
        print(f"Plan ID: {plan['plan_id']}")
        print(f"Total Tasks: {len(plan['tasks'])}")

        for i, task in enumerate(plan['tasks'], 1):
            print(f"\nTask {i}/{len(plan['tasks'])}:")
            print(f"  Type: {task['type']}")
            print(f"  Action: {task['action']}")
            print(f"  Parameters: {task['parameters']}")
            print(f"  Estimated Duration: {task['estimated_duration']}s")

            # Simulate task execution
            print(f"  Status: EXECUTING...")
            time.sleep(min(1.0, task['estimated_duration']))  # Simulate execution time
            print(f"  Status: COMPLETED")

        print(f"\n--- Plan Execution Complete ---")

def main():
    """Main function to demonstrate LLM cognitive planning."""
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key before running this example.")
        return

    # Initialize planner
    planner = LLMCognitivePlanner(api_key=api_key)

    # Example commands to test
    test_commands = [
        "Go to the kitchen and pick up the red cup",
        "Navigate to the living room and find the remote control",
        "Move to the bedroom, locate the book on the table, and bring it to me",
        "Go to the office, turn on the computer, and wait for it to boot up",
        "Find the blue ball in the playroom and put it in the toy box"
    ]

    print("LLM Cognitive Planning Demo")
    print("=" * 50)

    for i, command in enumerate(test_commands, 1):
        print(f"\nExample {i}: {command}")
        print("-" * 30)

        # Generate plan
        plan = planner.generate_plan(command)

        if plan and planner.validate_plan(plan):
            print("✓ Plan generated successfully!")

            # Display plan summary
            print(f"Plan ID: {plan['plan_id']}")
            print(f"Command: {plan['command']}")
            print(f"Confidence: {plan['metadata'].get('confidence', 'N/A')}")
            print(f"Reasoning: {plan['metadata'].get('reasoning', 'N/A')[:100]}...")

            # Show task breakdown
            print(f"\nTask Breakdown ({len(plan['tasks'])} tasks):")
            for task in plan['tasks']:
                print(f"  - {task['type'].upper()}: {task['action']}")

            # Show context
            context = plan['context']
            print(f"\nContext:")
            print(f"  Environment: {context.get('environment', 'Unknown')}")
            print(f"  Constraints: {context.get('constraints', [])}")
            print(f"  Safety: {context.get('safety_considerations', [])}")

            # Uncomment the next line to simulate plan execution
            # planner.execute_plan_simulation(plan)

        else:
            print("✗ Failed to generate valid plan")

        print("\n" + "="*50)

    # Interactive mode
    print("\nInteractive Mode (type 'quit' to exit):")
    while True:
        try:
            user_command = input("\nEnter a command for the robot: ").strip()
            if user_command.lower() in ['quit', 'exit', 'q']:
                break

            if user_command:
                print(f"\nGenerating plan for: {user_command}")
                plan = planner.generate_plan(user_command)

                if plan and planner.validate_plan(plan):
                    print("✓ Plan generated successfully!")
                    print(f"Tasks: {len(plan['tasks'])}")

                    for task in plan['tasks']:
                        print(f"  - {task['type']}: {task['action']}")
                else:
                    print("✗ Failed to generate plan")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nLLM Cognitive Planning Demo completed!")

if __name__ == '__main__':
    main()