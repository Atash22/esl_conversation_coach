import os
from openai import OpenAI
import gradio as gr

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL = "gpt-4.1-mini"

def get_system_message(level):
    levels = {
        "A1 - Beginner": "You are a warm ESL coach for BEGINNERS. Use very simple words. Correct only critical mistakes gently. End with a simple yes/no question.",
        "A2 - Elementary": "You are a friendly ESL coach for ELEMENTARY students. Use simple everyday vocabulary. Correct up to 2 mistakes kindly. End with a simple question.",
        "B1 - Intermediate": "You are an encouraging ESL coach for INTERMEDIATE students. Respond naturally then correct grammar gently. Suggest one new vocabulary word. End with a follow-up question.",
        "B2 - Upper Intermediate": "You are a motivating ESL coach for UPPER INTERMEDIATE students. Correct subtle grammar mistakes. Introduce collocations and phrasal verbs. Ask open-ended questions.",
        "C1 - Advanced": "You are a sophisticated ESL coach for ADVANCED students. Focus on subtle grammar, style and register. Suggest academic vocabulary. Ask complex thought-provoking questions."
    }
    return levels.get(level, levels["B1 - Intermediate"])

def chat(message, history, level):
    system_message = get_system_message(level)

    messages = [{"role": "system", "content": system_message}]

    for item in history:
        if isinstance(item, dict):
            messages.append({"role": item["role"], "content": item["content"]})
        else:
            human, assistant = item
            messages.append({"role": "user", "content": human})
            messages.append({"role": "assistant", "content": assistant})

    messages.append({"role": "user", "content": message})

    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True
    )
    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content or ""
        yield response

# ---- Theme + styling ----
theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="blue",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "sans-serif"],
)

custom_css = """
.gradio-container {max-width: 900px !important; margin: auto !important;}
.message {border-radius: 16px !important;}
footer {visibility: hidden}
"""

gr.ChatInterface(
    fn=chat,
    title="🎓 ESL Conversation Coach",
    description=(
        "Practice speaking and writing English at your level — "
        "get instant, friendly feedback and new vocabulary as you chat."
    ),
    theme=theme,
    css=custom_css,
    chatbot=gr.Chatbot(
        avatar_images=(None, "🎓"),
        height=480,
        show_copy_button=True,
    ),
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
    additional_inputs_accordion=gr.Accordion(label="Your English Level", open=True),
    examples=[
        ["I apply to jobs", "B1 - Intermediate"],
        ["Yesterday I go to the store and buy some milk", "A2 - Elementary"],
        ["Can you help me practice for a job interview?", "B2 - Upper Intermediate"],
        ["I would like to elaborate on the socioeconomic implications", "C1 - Advanced"],
    ],
    cache_examples=False,
).launch()
