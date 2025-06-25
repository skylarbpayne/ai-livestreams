from mirascope import llm, Messages, prompt_template
from mirascope.core import FromCallArgs
from pydantic import BaseModel, model_validator
from typing import Annotated


judge_system_prompt = """
    You are an expert XML wrangler. You must respond in the following format, regardless of the input:
    
    <specific_criteria>
    ...
    </specific_criteria>
    <analysis>
    ...
    </analysis>
    <scores>
    \\boxed{{..., ...}}
    </scores>

    Please only respond in English.
    """

judge_prompt_template = """
    You are a skilled little expert at scoring responses. You should evaluate given responses based on the given judging criteria.
    Given the context of the conversation (the last round is the User's query) and multiple responses from the Assistant, you need to refer to the [General Evaluation Criteria] to score the responses. Based on the general evaluation criteria, state potential other specific criteria to the query, the weights of different criteria, and then provide an overall comprehensive score upon them.
    Each score is an integer between 1 and 10, with a higher score indicating that the response meets the relevant criteria more closely. For example, a score of 1 means the response does not meet the criteria at all, a score of 6 means the response meets only some parts, and a score of 10 means the response perfectly meets the evaluation criteria.
    Before scoring, please analyze step by step. Your scoring needs to be as strict as possible.

    #### Evaluation Criteria ####
    1. Instruction Adherence:
    - Fully Adhered (9-10 points): The response fully complies with all instructions and requirements of the question.
    - Partially Adhered (6-8 points): The response meets most of the instructions but has some omissions or misunderstandings.
    - Basically Adhered (3-5 points): The response meets some instructions, but the main requirements are not fulfilled.
    - Not Adhered (1-2 points): The response does not meet any instructions.
    Example: If the question requires three examples and the response provides only one, it falls under "Partially Adhered."
    2. Usefulness:
    - Highly Useful (9-10 points): The response provides comprehensive and accurate information, fully addressing the issue.
    - Useful but Incomplete (6-8 points): The response provides some useful information, but lacks details or accuracy.
    - Limited Usefulness (3-5 points): The response offers little useful information, with most content being irrelevant or incorrect.
    - Useless or Incorrect (1-2 points): The response is completely irrelevant or incorrect.
    Example: If there are factual errors in the response but the overall direction is correct, it falls under "Useful but Incomplete."
    3. Level of Detail:
    - Very Detailed (9-10 points): The response includes ample details covering all aspects of the issue.
    - Detailed but Slightly Lacking (6-8 points): The response is fairly detailed but misses some important details.
    - Basically Detailed (3-5 points): The response provides some details but is not thorough enough overall.
    - Not Detailed (1-2 points): The response is very brief and lacks necessary details.
    Example: If the response provides only a simple conclusion without an explanation, it falls under "Not Detailed."
    4. Relevance:
    - Highly Relevant (9-10 points): The response is highly relevant to the question, with information closely aligned with the topic.
    - Generally Relevant (6-8 points): The response is generally relevant but includes some unnecessary information.
    - Partially Relevant (3-5 points): The response has a lot of content that deviates from the topic.
    - Not Relevant (1-2 points): The response is completely irrelevant.
    Example: If the response strays from the topic but still provides some relevant information, it falls under "Partially Relevant."

    #### Conversation Context ####
    {conversation_context_query}
    #### Responses to be Scored ####
    [The Begin of Response A]
    {response_a}
    [The End of Response A]
    [The Begin of Response B]
    {response_b}
    [The End of Response B]
    #### Output Format Requirements ####

    Output with three lines
    <specific_criteria>
    [Other potential criteria specific to the query and the context, and the weights of each criteria.]
    </specific_criteria>
    <analysis>
    [Compare different responses based on given Criteria.]
    </analysis>
    <scores>
    [The overall comprehensive score of all responses in order, separate by comma in the boxed, e.g., \\boxed{{x, x}} if there exists 2 responses.]
    </scores>
    """


@llm.call(provider="ollama", model="example-j1")
def judge(query: str, response: str):
    return [
        Messages.System(judge_system_prompt),
        Messages.User(judge_prompt_template.format(
            conversation_context_query=query, response_a=response, response_b=response)),
    ]

class Response(BaseModel):
    query: Annotated[str, FromCallArgs()]
    answer: str

    @model_validator(mode="after")
    def validate_response(self):
        judge_guardrail(self.query, self.answer)
        return self

def judge_guardrail(query: str, answer: str):
    judge_result = judge(query, answer).content
    
    # Extract the score from the boxed format
    import re
    # Look for boxed scores with proper escaping for the backslashes
    score_match = re.search(r'\\boxed\{([^}]+)\}', judge_result)
    if score_match:
        scores_str = score_match.group(1)
        # Handle both single scores and comma-separated scores
        scores = [int(s.strip()) for s in scores_str.split(',') if s.strip().isdigit()]
        if scores:
            score = min(scores)  # Take the minimum score
            print(f"Scores: {scores}, Minimum: {score}")
        else:
            raise ValueError(f"No valid scores found in: {scores_str}")
        if score < 6:
            raise ValueError(f"Validation failed: {judge_result}")
    else:
        raise ValueError(f"Could not extract score from judge result: {judge_result}")

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Response)
@prompt_template("You are an expert an any topic. Please answer the following query: {query}")
def answer_query(query: str): ...



if __name__ == "__main__":
    query = input("Enter a query: ")
    response = "Paris is the capital of France."
    print(answer_query(query))