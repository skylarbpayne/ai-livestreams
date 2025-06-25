# 2025-06-24 Output Guardrails with j1-micro from HaizeLabs

In this livestream we are going to cover using j1-micro and mirascope to create output guardrails.

# Why?

Output guardrails are an effective way to provide nuanced validation. An important thread of current research right now investigates
how we can create effect models to 'judge', 'reward', or 'verify' a particular response.
Note that there is a lot of terminology like this, and they are often used somewhat interchangeably. Though some people consider them
to have slight nuances (for example "verifier" just tells you true/false while "reward" gives a real value number).

[Research from HaizeLabs](https://github.com/haizelabs/j1-micro) shows that we can have tiny, yet still mighty reward models.

This enables us to run the models locally on cheap available hardware, and at scale.
This makes it effective for being in our "hot path" for validation (e.g. input or output guardrail).

# What?

So today we'll do the following:

- Set up haizelabs j1-micro-1.7B to be served via Ollama (this requires creating a GGUF file of the LoRA adapter and then creating a new model in Ollama)
- Create a judge prompt following the [j1-micro template](https://huggingface.co/haizelabs/j1-micro-1.7B)
- Add the prompt as a pydantic validator to a mirascope function

Let's get started!