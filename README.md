---
title: ESL Conversation Coach
emoji: 🎓
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: "4.44.0"
python_version: "3.10"
app_file: app.py
pinned: false
---

# 🎓 ESL Conversation Coach

A conversational AI that helps English learners practice speaking and writing at any
CEFR level (A1–C1). The coach adapts its vocabulary, the depth of its grammar
corrections, and the difficulty of its follow-up questions to the level you select —
so a beginner gets gentle, simple feedback while an advanced learner gets notes on
register, style, and academic vocabulary.

Built with an LLM (via [OpenRouter](https://openrouter.ai)) and a
[Gradio](https://www.gradio.app/) chat interface.

## Why I built it

I taught ESL for eight years before moving into AI. This project combines both: it
encodes the kind of level-appropriate feedback a good language teacher gives into a
system prompt that changes with the learner's CEFR level, wrapped in a simple chat UI
that anyone can use.

## Features

- **Five CEFR levels (A1–C1)** — each with its own coaching persona and correction style
- **Level-appropriate feedback** — beginners get only critical corrections in simple
  words; advanced learners get subtle grammar, collocations, and style notes
- **Streaming responses** for a natural, real-time chat feel
- **Runs on free models** through OpenRouter, so it costs nothing to try

## How it works

The core idea is a `get_system_message(level)` function that returns a different
coaching instruction for each CEFR level. The selected level is passed from a Gradio
dropdown into the chat function on every turn, so the assistant's behaviour tracks the
learner's level throughout the conversation.

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/Atash22/esl-conversation-coach.git
   cd esl-conversation-coach
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your API key. Copy the example env file and paste in your OpenRouter key
   (get a free one at https://openrouter.ai/keys):
   ```bash
   cp .env.example .env
   # then edit .env and set OPENROUTER_API_KEY=sk-or-...
   ```

4. Run the notebook (`esl_coach.ipynb`) in Jupyter or VS Code and run all cells. The
   last cell launches the Gradio app and prints a local URL.

## Tech stack

- Python 3.12
- `openai` client pointed at the OpenRouter endpoint
- `gradio` for the chat UI
- `python-dotenv` for key management

## Possible next steps

- Detect the learner's level automatically from their messages instead of asking
- Track recurring mistakes across a session and summarise them at the end
- Add pronunciation practice with audio input/output

## License

MIT — see [LICENSE](LICENSE).
