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

gr.ChatInterface(
    fn=chat,
    title="🎓 ESL Conversation Coach",
    description="Select your English level and start practising!",
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
    ]
).launch()