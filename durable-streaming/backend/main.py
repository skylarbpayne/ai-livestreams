from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List
from contextlib import asynccontextmanager
import asyncio
import json
import random
from mirascope import llm, prompt_template
from dotenv import load_dotenv
load_dotenv()


class StreamChunk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    stream_id: str = Field(index=True)
    event_id: int = Field(index=True)
    data: str
    timestamp: float = Field(default_factory=lambda: asyncio.get_event_loop().time())


DATABASE_URL = "sqlite:///./stream_data.db"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

# Create the FastAPI application instance
app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow requests from React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_stream_chunks(stream_id: str) -> List[StreamChunk]:
    with Session(engine) as session:
        statement = select(StreamChunk).where(StreamChunk.stream_id == stream_id).order_by(StreamChunk.event_id)
        return list(session.exec(statement))

def save_chunk(stream_id: str, event_id: int, data: str):
    with Session(engine) as session:
        chunk = StreamChunk(stream_id=stream_id, event_id=event_id, data=data)
        session.add(chunk)
        session.commit()



@llm.call(provider="openai", model="gpt-4o-mini", stream=True)
@prompt_template("""
You are a storyteller. You are given a story query and you need to tell a story.
Make the story really long and suspenseful.
Story Query: {story_query}
""")
async def tell_story(story_query: str): ...



async def generate_story(stream_id: str, last_event_id: int = -1):
    chunks = get_stream_chunks(stream_id)
    if len(chunks) > 0:
        done = False
        while not done:
            for chunk in chunks:
                if chunk.event_id > last_event_id:
                    last_event_id = chunk.event_id
                    yield f"data: {chunk.data}\n\n"
                    done = json.loads(chunk.data).get('end', False)
            await asyncio.sleep(1)
            chunks = get_stream_chunks(stream_id)
        return
    
    i = 0
    async for chunk, _ in await tell_story("Tell me a story about goblins"):
        data = json.dumps({'story': chunk.content, 'streamId': stream_id, 'eventId': i, 'end': False})
        save_chunk(stream_id, i, data)
        yield f"data: {data}\n\n"
        i += 1
    yield f"data: {json.dumps({'story': '', 'streamId': stream_id, 'eventId': i, 'end': True})}\n\n"

# Define the SSE endpoint that React will connect to
@app.get("/events/{stream_id}")
async def stream_events(stream_id: str):
    # Return a StreamingResponse that uses our generator function
    return StreamingResponse(
        generate_story(stream_id),  # The async generator that provides the data
        media_type="text/event-stream",  # Required content type for SSE
        headers={
            # Prevent caching so events are always fresh
            "Cache-Control": "no-cache",
            # Keep the connection alive for streaming
            "Connection": "keep-alive",
        }
    )