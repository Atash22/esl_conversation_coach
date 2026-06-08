import os
from openai import OpenAI
import gradio as gr

openrouter_client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

FREE_MODELS = [
    "nvidia/llama-3.1-nemotron-nano-8b-v1:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemma-3-4b-it:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "openai/gpt-4.1-mini",  # paid fallback — only charges if ALL free models fail
]

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
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})

    # Try free OpenRouter models first
    for model in FREE_MODELS:
        try:
            stream = openrouter_client.chat.completions.create(
                model=model, messages=messages, stream=True,
                extra_headers={"HTTP-Referer": "https://huggingface.co/spaces/Atash22/esl-coach", "X-Title": "ESL Coach"}
            )
            response = ""
            for chunk in stream:
                response += chunk.choices[0].delta.content or ""
                yield response
            return
        except Exception as e:
            print(f"{model} failed: {e}")
            continue

    # OpenAI as final fallback
    try:
        print("Trying OpenAI fallback...")
        stream = openai_client.chat.completions.create(
            model="gpt-4.1-mini", messages=messages, stream=True
        )
        response = ""
        for chunk in stream:
            response += chunk.choices[0].delta.content or ""
            yield response
    except Exception as e:
        yield f"⚠️ All models failed. Last error: {e}"

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