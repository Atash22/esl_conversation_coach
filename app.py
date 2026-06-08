import os
from openai import OpenAI
import gradio as gr

# ── Client ──────────────────────────────────────────────────────────────────
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ── Free models with automatic fallback ─────────────────────────────────────
FREE_MODELS = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemma-3-4b-it:free",
    "mistralai/mistral-7b-instruct:free",
]

# ── System message by CEFR level ────────────────────────────────────────────
def get_system_message(level):
    levels = {
        "A1 - Beginner": """
You are a warm ESL coach for BEGINNERS.
- Use very simple words and short sentences
- Correct only the most critical mistakes, very gently
- 💡 Tip: use simple corrections like 'Try saying: ...'
- Always end with a very simple yes/no question
""",
        "A2 - Elementary": """
You are a friendly ESL coach for ELEMENTARY students.
- Use simple, everyday vocabulary and short sentences
- Correct up to 2 mistakes per reply, kindly
- 💡 Tip: 'Good try! Instead say: ...'
- Introduce basic new words with simple definitions
- End with a simple question about daily life
""",
        "B1 - Intermediate": """
You are an encouraging ESL coach for INTERMEDIATE students.
- Respond naturally, then correct grammar mistakes gently
- 💡 Tip: 'Instead of X, try Y — because...'
- Suggest one new vocabulary word per reply with an example sentence
- End with a follow-up question to keep conversation going
""",
        "B2 - Upper Intermediate": """
You are a motivating ESL coach for UPPER INTERMEDIATE students.
- Engage naturally and correct more subtle grammar mistakes
- 💡 Point out word choice issues and suggest better alternatives
- Introduce collocations and phrasal verbs related to the topic
- Challenge them with open-ended discussion questions
""",
        "C1 - Advanced": """
You are a sophisticated ESL coach for ADVANCED students.
- Engage in natural, nuanced conversation
- Focus on subtle grammar, style, and register issues
- 💡 Suggest precise academic or professional vocabulary
- Highlight idioms and collocations
- Challenge them with complex, thought-provoking questions
"""
    }
    return levels[level]

# ── Chat function with streaming + model fallback ────────────────────────────
def chat(message, history, level):
    system_message = get_system_message(level)

    history = [{"role": h["role"], "content": h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]

    for model in FREE_MODELS:
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                extra_headers={
                    "HTTP-Referer": "https://huggingface.co/spaces/atash22/esl-coach",
                    "X-Title": "ESL Conversation Coach"
                }
            )
            response = ""
            for chunk in stream:
                response += chunk.choices[0].delta.content or ""
                yield response
            return

        except Exception as e:
            print(f"Model {model} failed: {e} — trying next...")
            continue

    yield "⚠️ All free models are currently at their limit. Please try again in a minute!"

# ── Launch ───────────────────────────────────────────────────────────────────
gr.ChatInterface(
    fn=chat,
    title="🎓 ESL Conversation Coach",
    description="Select your English level and start practising! The AI will correct your grammar gently and help you improve naturally.",
    additional_inputs=[
        gr.Dropdown(
            choices=[
                "A1 - Beginner",
                "A2 - Elementary",
                "B1 - Intermediate",
                "B2 - Upper Intermediate",
                "C1 - Advanced"
            ],
            value="B1 - Intermediate",
            label="Your English Level"
        )
    ],
    examples=[
        ["Tell me about your weekend", "B1 - Intermediate"],
        ["I go to school yesterday", "A1 - Beginner"],
        ["I want to learn new words about food", "A2 - Elementary"],
        ["Can we discuss the impact of social media?", "B2 - Upper Intermediate"],
        ["Let's discuss the ethics of AI", "C1 - Advanced"],
    ],
    theme=gr.themes.Soft()
).launch()
