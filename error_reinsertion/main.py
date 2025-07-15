"""
Error Reinsertion Example

This example demonstrates a common issue where an LLM provides overly formal 
or academic responses when users want casual, friendly explanations.
"""

import os
from mirascope import llm, prompt_template


@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template("""
Explain {topic}. Be thorough and detailed, but keep it simple and easy to understand.
Use plaintext, not markdown. Write like a human. Avoid being overly formal. Be a little messy, not too formulaic or structured.
Make sure to be engaging.
""")
def explain_concept(topic: str) -> str: ...


def main():
    # Set up OpenAI API key (user should set this)
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("Please set your OPENAI_API_KEY environment variable")
    
    # Example query that often gets overly formal responses
    topic = input("Enter a topic to explain: ")
    
    print(f"Asking for explanation of: {topic}")
    print("-" * 50)

    response = explain_concept(topic)
    print(response)

if __name__ == "__main__":
    main()