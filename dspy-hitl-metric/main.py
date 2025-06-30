import pandas as pd
from typing import Literal
import dspy
from dotenv import load_dotenv
from dspy.teleprompt import BootstrapFewShot

load_dotenv()


lm = dspy.LM('openai/gpt-4o-mini')
dspy.configure(lm=lm)

EmotionLabel = Literal['happiness', 'sadness', 'neutral', 'anger', 'love', 'fear', 'disgust', 'confusion', 'surprise', 'shame', 'guilt', 'sarcasm', 'desire']

class Emotion(dspy.Signature):
    """Classify emotion."""

    sentence: str = dspy.InputField()
    sentiment: EmotionLabel = dspy.OutputField()

classify_emotion = dspy.Predict(Emotion)


def load_dataset():
    df = pd.read_parquet("hf://datasets/boltuix/emotions-dataset/emotions_dataset.parquet")
    return df.iloc[:20], df.iloc[20:40]


def bootstrap_few_shot(dspy_program, trainset, metric, **cfg):
    teleprompter = BootstrapFewShot(metric=metric, **cfg)
    return teleprompter.compile(dspy_program, trainset=trainset)


def create_trainset(df):
    return [dspy.Example(sentence=sentence, sentiment=sentiment).with_inputs("sentence") for sentence, sentiment in zip(df['Sentence'], df['Label'])]


def hitl_metric(example: dspy.Example, pred: str, trace=None) -> bool:
    print(f"Example:\n\t{example.sentence}")
    print(f"Pred:\n\t{pred}")
    return input("Is this correct? (y/n)") == "y"


def main():
    dtr, dte = load_dataset()
    dte['predicted_emotion'] = dte['Sentence'].apply(lambda x: classify_emotion(sentence=x).sentiment)
    print((dte['Label'] == dte['predicted_emotion']).astype(float).mean())

    trainset = create_trainset(dtr)
    optimized_program = bootstrap_few_shot(classify_emotion, trainset, hitl_metric)
    dte['predicted_emotion_optimized'] = dte['Sentence'].apply(lambda x: optimized_program(sentence=x).sentiment)
    print((dte['Label'] == dte['predicted_emotion_optimized']).astype(float).mean())




if __name__ == "__main__":
    main()