import os
import tempfile

from openai import OpenAI
import gradio as gr

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

CHAT_MODEL = "gpt-4.1-mini"
TTS_MODEL = "tts-1"
TTS_VOICE = "alloy"
STT_MODEL = "whisper-1"


def get_system_message(level, topic):
    base_persona = {
        "A1 - Beginner": "You are a warm ESL coach for BEGINNERS. Use very simple words and short sentences. Correct only critical mistakes, gently, one at a time.",
        "A2 - Elementary": "You are a friendly ESL coach for ELEMENTARY students. Use simple everyday vocabulary. Correct up to 2 mistakes kindly, one at a time.",
        "B1 - Intermediate": "You are an encouraging ESL coach for INTERMEDIATE students. Respond naturally, then correct grammar gently. Suggest one new vocabulary word per turn.",
        "B2 - Upper Intermediate": "You are a motivating ESL coach for UPPER INTERMEDIATE students. Correct subtle grammar mistakes. Introduce collocations and phrasal verbs naturally.",
        "C1 - Advanced": "You are a sophisticated ESL coach for ADVANCED students. Focus on subtle grammar, style, and register. Suggest academic or nuanced vocabulary.",
    }
    persona = base_persona.get(level, base_persona["B1 - Intermediate"])

    conversational_style = (
        "You are having a real, natural spoken conversation, not running a drill. "
        "Talk like a curious, friendly human, not a grammar checker. "
        "Weave any correction smoothly into your reply instead of listing it separately "
        "(e.g. 'Ah, so you go to the store yesterday? *Nice - I went to the store yesterday.* What did you buy?'). "
        "Never correct more than what's needed to keep the conversation flowing naturally. "
        "Ask genuine follow-up questions about what the student just said, and steer the conversation "
        "toward things they'd actually enjoy talking about. "
        "Keep replies short and conversational (2-4 sentences), like real speech, not an essay."
    )

    if topic and topic.strip():
        interest_line = (
            f"The student is interested in: {topic.strip()}. "
            "Bring this topic into the conversation naturally, ask about it, and use it "
            "as a recurring thread - don't force it into every single turn, but return to it "
            "when it fits, the way a good conversation partner would."
        )
    else:
        interest_line = (
            "You don't yet know what the student is interested in. Early in the conversation, "
            "ask a friendly question to find out (hobbies, work, movies, sports, food, travel - anything), "
            "then build the conversation around whatever they share."
        )

    return f"{persona}\n\n{conversational_style}\n\n{interest_line}"


def transcribe_audio(audio_path):
    """Convert a recorded voice message into text using Whisper."""
    if audio_path is None:
        return ""
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model=STT_MODEL,
            file=f,
        )
    return transcript.text


def synthesize_speech(text):
    """Convert the assistant's reply into a playable audio file."""
    if not text:
        return None
    response = client.audio.speech.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=text,
    )
    tmp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    response.stream_to_file(tmp_file.name)
    return tmp_file.name


def respond(message, mic_audio, chat_history, level, topic):
    chat_history = chat_history or []

    # Prefer typed text; fall back to transcribing the microphone recording
    user_text = (message or "").strip()
    if not user_text and mic_audio is not None:
        user_text = transcribe_audio(mic_audio)

    if not user_text:
        return chat_history, None, "", None

    system_message = get_system_message(level, topic)
    api_messages = [{"role": "system", "content": system_message}] + chat_history
    api_messages.append({"role": "user", "content": user_text})

    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=api_messages,
    )
    reply_text = completion.choices[0].message.content

    chat_history = chat_history + [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": reply_text},
    ]

    audio_path = synthesize_speech(reply_text)

    # clear the text box and mic input after sending
    return chat_history, audio_path, "", None


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

with gr.Blocks(theme=theme, css=custom_css, title="ESL Conversation Coach") as demo:
    gr.Markdown(
        "# \U0001F393 ESL Conversation Coach\n"
        "### Talk (or type) about anything you like - get natural, spoken feedback as you go"
    )

    with gr.Accordion("Your English Level & Interests", open=True):
        with gr.Row():
            level = gr.Dropdown(
                choices=[
                    "A1 - Beginner",
                    "A2 - Elementary",
                    "B1 - Intermediate",
                    "B2 - Upper Intermediate",
                    "C1 - Advanced",
                ],
                value="B1 - Intermediate",
                label="Your English Level",
            )
            topic = gr.Textbox(
                label="Topics you enjoy (optional)",
                placeholder="e.g. football, cooking, sci-fi movies, travel...",
            )

    chatbot = gr.Chatbot(
        type="messages",
        avatar_images=(None, "\U0001F393"),
        height=440,
        show_copy_button=True,
    )

    reply_audio = gr.Audio(label="Coach's voice", autoplay=True)

    with gr.Row():
        msg = gr.Textbox(
            placeholder="Type a message, or record your voice below...",
            scale=4,
            show_label=False,
        )
        send_btn = gr.Button("Send", variant="primary", scale=1)

    mic = gr.Audio(sources=["microphone"], type="filepath", label="Or speak instead")

    gr.Examples(
        examples=[
            ["I apply to jobs"],
            ["Yesterday I go to the store and buy some milk"],
            ["Can you help me practice for a job interview?"],
        ],
        inputs=msg,
    )

    inputs = [msg, mic, chatbot, level, topic]
    outputs = [chatbot, reply_audio, msg, mic]

    send_btn.click(respond, inputs=inputs, outputs=outputs)
    msg.submit(respond, inputs=inputs, outputs=outputs)
    mic.stop_recording(respond, inputs=inputs, outputs=outputs)

demo.launch()
