
# movie-rating-agent

## 1. Agent Name

**movie-rating-agent**

---

## 2. Agent Purpose

The purpose of this agent is to demonstrate **basic agent development with tool usage** focused on movie information and ratings.  
This agent is designed to:
- interact with the user about available movies,
- retrieve structured movie information via tools,
- provide a demonstration "rating" for specific movies (randomly chosen from 1 to 5),
- reason about and explain movie metadata in natural language.

This description serves as a **technical task specification for the agent's system prompt**.

> **Educational focus:**  
> This agent operates on small, in-memory example movie records. It is intentionally simplified and does not represent a complete or production-ready recommender or critic.

---

## 3. Agent Tools

This agent uses **three tools**, each illustrating a different level of data preparation and a specific role.

### 3.1 `list_movies`

**Purpose:**  
Provides an overview of all available movies.

**Output includes:**
- movie title,
- year,
- genre(s),
- number of metadata fields.

**Design principle:**  
The tool returns **fully prepared metadata**, allowing the agent to immediately reason about the catalogue.

Example output:
- The tool returns a structured list like:
  - title: "Inception", year: 2010, genres: ["Sci-Fi","Thriller"], fields: 5
  - title: "The Godfather", year: 1972, genres: ["Crime","Drama"], fields: 5

---

### 3.2 `describe_movie(movie_title)`

**Purpose:**  
Provides detailed information about a single movie.

**Input:**
- `movie_title` – exact or best-effort movie title to describe.

**Output includes:**
- movie title,
- year,
- director,
- main cast (sample),
- genres,
- one-sentence synopsis,
- one example metadata row.

**Design principle:**  
The tool summarizes the movie instead of exposing raw or excessive data. It supplies concise, structured facts for the agent to interpret.

---

### 3.3 `rate_movie(movie_title)`

**Purpose:**  
Returns a demonstration rating for a selected movie.

**Input:**
- `movie_title` – exact or best-effort movie title to rate.

**Output includes:**
- movie title,
- rating: an integer randomly chosen from 1 to 5 (inclusive),
- note indicating the rating is generated randomly for demo purposes.

**Important behavior (explicit requirement):**  
When the user asks the agent to provide a rating for a specific movie, the agent must call this tool (or otherwise produce output) that returns a rating randomly selected from 1 to 5. The randomness is intentional and educational: it demonstrates tool-driven outputs and separation of concerns (data generation vs. agent reasoning).

**Educational note:**  
Random ratings are only for demonstration and testing; they do not reflect real critic scores or aggregated user reviews.

---

## 4. Tool–Agent Responsibility Split

This agent demonstrates the following fundamental rule:

> **Tools are responsible for data retrieval, preparation, and structuring.**  
> **The agent is responsible for reasoning, explanation, and interpretation.**

Examples:
- Tools compute and return movie metadata and the demonstration rating.
- The agent explains what the movie contains, what the rating means in this demo context, and suggests follow-up actions.
- The agent should not invent structured metadata; it must rely on tool outputs for factual fields. For ratings, the agent reports the random value and clarifies its demo nature.

This separation is a **core expectation** for student agents in this course.

---

## 5. Implementation Details

This agent uses:
- **AG2** `ConversableAgent` for the LLM-powered assistant,
- **AG2** `register_function` to expose tools to the agent,
- **Chainlit** for the chat UI with **Step visualization** of tool calls.

### AG2 Two-Agent Tool Pattern

AG2 uses a two-agent architecture for tool usage:
- **Assistant agent** (`movie_agent`): the LLM-powered agent that decides *when* and *which* tool to call.
- **Executor agent** (`tool_executor`): a non-LLM agent that *runs* the tool functions and returns results.

Tools are registered with `register_function(fn, caller=assistant, executor=executor)`.

In this example, the tool-calling loop is implemented explicitly in the `@cl.on_message` handler, making it fully transparent to the student how the process works:
1. The assistant generates a reply (which may include `tool_calls`).
2. Tool functions are executed and their results added to the conversation history.
3. The assistant processes tool results and generates a final text answer.

Each tool call is shown in the Chainlit UI as an expandable **Step**, displaying both input arguments and output data. The `rate_movie` tool is implemented so that each execution returns a fresh random integer in [1,5].

---

## 6. Example Interaction

```
User: what movies do we have available?

Agent: Here are the movies currently available:
  | Title           | Year | Genres                | Fields |
  |-----------------|------|-----------------------|--------|
  | Inception       | 2010 | Sci-Fi, Thriller      | 5      |
  | The Godfather   | 1972 | Crime, Drama          | 5      |
  | Spirited Away   | 2001 | Animation, Fantasy    | 5      |

  Let me know if you'd like more details on any of them!

User: describe Inception

Agent: Inception (2010)
  - Director: Christopher Nolan
  - Main cast: Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page
  - Genres: Sci-Fi, Thriller
  - Synopsis: A skilled thief leads a team into dream worlds to perform corporate espionage.
  - Example metadata row: {title: "Inception", year: 2010, director: "Christopher Nolan", genres: ["Sci-Fi","Thriller"], runtime_min: 148}

  Would you like a demo rating for this movie?

User: rate Inception

Agent (calls rate_movie):
  - Inception — Rating: 4
  Note: This rating was generated randomly from 1 to 5 for demonstration purposes.

  Let me know if you'd like another rating or more details.
```

---

## 7. Limitations of This Example

- Movies and metadata are hard-coded and stored in memory.
- No external review sources, databases, or APIs are used.
- The `rate_movie` tool returns a random rating; this is intentionally non-authoritative and only for educational demonstration.

> **Note:**  
> This agent is a **reference example**, not a production recommender. Student agents should design tools that return meaningful, structured data and clearly document any synthetic behavior (like random ratings).

---

## Additional Notes

- This agent represents the **minimum acceptable level** of tool usage for the movie-rating demo.
- It demonstrates good practices (structured metadata tools) and an intentional demo-only tool (`rate_movie`) that returns random ratings.
- Understanding this example is essential before moving on to:
  - agent-as-tool patterns,
  - multi-agent systems,
  - attacker–evaluator–defender scenarios.

