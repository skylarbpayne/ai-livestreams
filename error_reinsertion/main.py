"""
Error Reinsertion Example

This example demonstrates a common issue where an LLM provides overly formal 
or academic responses when users want casual, friendly explanations.
"""

import os
from mirascope import llm, prompt_template


@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template("Explain what {topic}. Keep it simple and easy to understand.")
def explain_concept(topic: str) -> str: ...


def main():
    # Set up OpenAI API key (user should set this)
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("Please set your OPENAI_API_KEY environment variable")
    
    # Example query that often gets overly formal responses
    topic = input("Enter a topic to explain: ")
    
    print(f"Asking for explanation of: {topic}")
    print("-" * 50)
    
    try:
        response = explain_concept(topic)
        print(response)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()