import os
import json
import random
from typing import Annotated, Dict

import chainlit as cl
from autogen import ConversableAgent
from autogen.events.agent_events import ExecuteFunctionEvent, ExecutedFunctionEvent

# ---------------------------
#  In-memory example datasets
# ---------------------------

movies_state: Dict[str, list] = {
    "Inception": [
        {
            "title": "Inception",
            "year": 2010,
            "director": "Christopher Nolan",
            "genres": ["Sci-Fi", "Thriller"],
            "runtime_min": 148,
        }
    ],
    "The Godfather": [
        {
            "title": "The Godfather",
            "year": 1972,
            "director": "Francis Ford Coppola",
            "genres": ["Crime", "Drama"],
            "runtime_min": 175,
        }
    ],
    "Spirited Away": [
        {
            "title": "Spirited Away",
            "year": 2001,
            "director": "Hayao Miyazaki",
            "genres": ["Animation", "Fantasy"],
            "runtime_min": 125,
        }
    ],
}

# ---------------------------
#  Tools (plain functions)
# ---------------------------


def list_movies() -> Dict:
    """Return all available movies with basic metadata summary.

    Output mirrors the previous dataset-style list: each entry includes the
    movie title, year, genres and number of metadata fields.
    """
    movies_info = []
    for name, rows in movies_state.items():
        num_records = len(rows)
        example = rows[0] if num_records > 0 else {}
        num_fields = len(example) if num_records > 0 else 0
        year = example.get("year") if isinstance(example, dict) else None
        genres = example.get("genres") if isinstance(example, dict) else []
        movies_info.append(
            {
                "title": name,
                "year": year,
                "genres": genres,
                "fields": num_fields,
            }
        )
    return {"movies": movies_info}


def describe_movie(
    movie_title: Annotated[
        str,
        "Title of the movie to describe. Accepts exact or best-effort titles.",
    ],
) -> Dict:
    """Return concise metadata for a single movie.

    If the movie is not found, return an error dict similar to the previous
    dataset-style responses.
    """
    if movie_title not in movies_state:
        return {
            "ok": False,
            "error": "movie_not_found",
            "message": (
                f"Movie '{movie_title}' not found. "
                f"Available movies: {', '.join(movies_state.keys())}."
            ),
        }

    rows = movies_state[movie_title]
    num_records = len(rows)
    example = rows[0] if num_records > 0 else {}
    num_fields = len(example) if num_records > 0 else 0
    field_names = list(example.keys()) if num_records > 0 else []

    # Build a one-sentence synopsis placeholder (kept short for demo)
    synopsis = None
    if example:
        synopsis = (
            f"{example.get('title')} ({example.get('year')}) is a "
            f"{', '.join(example.get('genres', []))} film directed by "
            f"{example.get('director')}."
        )

    return {
        "ok": True,
        "movie": movie_title,
        "year": example.get("year"),
        "director": example.get("director"),
        "main_cast": example.get("main_cast", None),
        "genres": example.get("genres", []),
        "synopsis": synopsis,
        "num_fields": num_fields,
        "example_row": example if num_records > 0 else None,
    }


def rate_movie(
    movie_title: Annotated[
        str,
        "Title of the movie to rate. Accepts exact or best-effort titles.",
    ],
) -> Dict:
    """Return a demonstration rating for a given movie.

    The rating is randomly chosen from 1 to 5 (inclusive) to demonstrate tool
    usage and separation of concerns. If the movie is not found, return an
    error dict similar to other tools.
    """
    if movie_title not in movies_state:
        return {
            "ok": False,
            "error": "movie_not_found",
            "message": (
                f"Movie '{movie_title}' not found. "
                f"Available movies: {', '.join(movies_state.keys())}."
            ),
        }

    rating = random.randint(1, 5)
    return {
        "ok": True,
        "movie": movie_title,
        "rating": rating,
        "note": "This rating is randomly generated for demonstration purposes (1-5).",
    }


# ---------------------------
#  LLM configuration
# ---------------------------

api_base_url = os.getenv("API_BASE_URL")
api_key = os.getenv("API_KEY")
model = os.getenv("MODEL", "qwen/qwen3-32b")

if not api_key:
    raise RuntimeError(
        "API_KEY is not set. "
        "Set it in your .env file or docker compose environment."
    )

llm_config = {
    "config_list": [
        {
            "model": model,
            "api_key": api_key,
            "base_url": api_base_url,
            "price": [0, 0],
        }
    ],
}

# ---------------------------
#  System prompt
# ---------------------------

SYSTEM_PROMPT = """\
You are a movie information and rating agent. You work with a small in-memory
catalog of movies that are already loaded into memory and exposed via tools.

Currently you have example movies stored in memory.

You have the following tools:
- list_movies: show all available movies and basic metadata (title, year,
  genres, number of metadata fields).
- describe_movie: describe a specific movie in more detail, including
  director, sample cast, genres, a one-sentence synopsis and an example
  metadata row.
- rate_movie: return a demonstration rating for a selected movie. The
  rating must be randomly chosen from 1 to 5 (inclusive).

Rules:
1) If the user asks what movies are available or wants an overview, always
    call list_movies.
2) If the user asks about a specific movie (director, year, genres, cast),
    call describe_movie for that movie.
3) If the user explicitly asks for a demo rating for a specific movie,
    call rate_movie for that movie. The returned rating must be an integer
    in the range 1-5, chosen randomly.
4) For general movie discussion or suggestions, use the tools to gather
    the structured facts first, then answer in natural language based on the
    tool results.
5) For casual small talk (hello, how are you), answer briefly, but if the
    question concerns the movie catalog focus on using the tools.

Always answer in English.
"""


def _format_content(content: object) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, (dict, list, tuple)):
        return json.dumps(content, ensure_ascii=True, indent=2)
    return str(content)

# ---------------------------
#  Chainlit event handlers
# ---------------------------


@cl.on_chat_start
async def on_chat_start():
    """Create the AG2 assistant and store it in the user session."""
    assistant = ConversableAgent(
        name="movie_agent",
        system_message=SYSTEM_PROMPT,
        llm_config=llm_config,
        human_input_mode="NEVER",
        functions=[list_movies, describe_movie, rate_movie],
    )

    cl.user_session.set("assistant", assistant)


@cl.on_message
async def on_message(message: cl.Message):
    """Handle each user message using AG2 async single-agent execution."""
    assistant: ConversableAgent = cl.user_session.get("assistant")

    response = await assistant.a_run(
        message=message.content,
        clear_history=False,
        max_turns=6,
        summary_method="last_msg",
        user_input=False,
    )

    tool_inputs: dict[str, dict[str, str]] = {}

    async for event in response.events:
        if isinstance(event, ExecuteFunctionEvent):
            event_data = event.content
            tool_key = getattr(event_data, "call_id", None) or event_data.func_name
            tool_inputs[tool_key] = {
                "name": event_data.func_name,
                "input": _format_content(event_data.arguments) or "(no arguments)",
            }
            continue

        if not isinstance(event, ExecutedFunctionEvent):
            continue

        event_data = event.content
        tool_key = getattr(event_data, "call_id", None) or event_data.func_name
        step_data = tool_inputs.get(
            tool_key,
            {
                "name": event_data.func_name,
                "input": "(no arguments)",
            },
        )
        async with cl.Step(name=step_data["name"], type="tool") as step:
            step.input = step_data["input"]
            step.output = _format_content(event_data.content)

    summary = await response.summary
    final_text = _format_content(summary)
    await cl.Message(content=final_text).send()
