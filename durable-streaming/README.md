# Durable AI Streaming

Many people are discovering that streaming AI responses is awesome... But most solutions have the most naive implementation:

user --> client --> server --> AI --> output stream... --> server --> client --> user

This means that if the connection between server/client is ever broken, the data is basically lost.
It also means that you can't really see the streaming happen on two devices simultaneously.

For some use cases, you might want the stream to be "durable".

## What does "durable" mean anyway?

When we call something durable it means that once its committed, it remains. A durable database is one where if you write to it, the data is not accidentally lost. For example, MySQL would be a durable database, but Redis would not be.

The core design issue of most AI streaming implementations is that the chunks are sent directly to the client, and never persisted. There are many design trade offs to consider
depending on the rest of your system. For example, a partiioned SQL database could work perfectly for your use case. Or maybe a durable queue like Kafka makes more sense. We just
want to demonstrate the core concepts here.

## Our Setup

1. Frontend in React with a dev server runnings (we run a separate frontend server for the convenience of hot reloading; in production, more likely your backend would serve the frontend)
2. Backend with FastAPI

We'll start with a really basic streaming implementation using server side events to send events.

## Our Journey

1. We'll walk through the really basic FastAPI -> React streaming setup
2. We'll work through adding durability by storing in a sqlite database
3. Demonstrate by showing the output in two side-by-side windows & closing and re-opening one
4. Swap in a streaming AI response

## Why not use websockets?

Websockets are more appropriate when you have a bidirectional stream. In many apps e.g. AI chat, we really only want to stream in one direction.
