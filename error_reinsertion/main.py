"""
Error Reinsertion Example

This example demonstrates a common issue where an LLM provides overly formal 
or academic responses when users want casual, friendly explanations.
"""

import os
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field


@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template("""
Explain {topic}. Be thorough and detailed, but keep it simple and easy to understand.
Use plaintext, not markdown. Write like a human. Avoid being overly formal. Be a little messy, not too formulaic or structured.
Make sure to be engaging. Address feedback to the previous draft if provided.

<previous_draft>
{previous_draft}
</previous_draft>
<feedback>
{feedback}
</feedback>
""")
def explain_concept(topic: str, previous_draft: str = "", feedback: str = "") -> str: ...


class Feedback(BaseModel):
    """Feedback on the explanation."""
    reasoning: str = Field(description="The reasoning behind the judgement.")
    written_by_ai: bool = Field(description="Whether you believe the explanation was written by an AI.")
    feedback: str = Field(description="Feedback on the explanation.")


@llm.call(provider="openai", model="o4-mini", response_model=Feedback)
@prompt_template("""
You are a helpful assistant that provides feedback on explanations.
You will be given an explanation and a topic.
You will need to judge whether the explanation was written by an AI.
Be very thorough in your feedback. If I address ALL your feedback in one round,
you should not think AI wrote the explanation on the next round.

<topic>
{topic}
</topic>

<explanation>
{explanation}
</explanation>
""")
def judge_explanation(explanation: str, topic: str) -> Feedback: ...

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
    feedback = judge_explanation(response, topic)
    print(feedback.model_dump_json(indent=2))
    if feedback.written_by_ai:
        response = explain_concept(topic, response, feedback.feedback)
        print(response)
        feedback = judge_explanation(response, topic)
        print(feedback.model_dump_json(indent=2))
        

if __name__ == "__main__":
    main()