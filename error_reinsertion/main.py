from mirascope.core import openai
import os


@openai.call("gpt-4o-mini")
def explain_topic(topic: str) -> str:
    """
    Explain a technical topic in a clear and accessible way.
    Be concise but informative.
    """
    return f"Explain {topic} in a way that's easy to understand."


def main():
    # Example topic that we want explained
    topic = "machine learning"
    
    print(f"Getting explanation for: {topic}")
    print("-" * 50)
    
    try:
        response = explain_topic(topic)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()