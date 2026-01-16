import os

import gradio as gr
import requests

from app.core.logging import get_logger

logger = get_logger(__name__)

BASE_URL = "http://backend:9000/api/v1"


def ingest_file(file_list):
    """
    Simulates sending the file to your backend FastAPI /ingest endpoint.
    """
    api_url = f"{BASE_URL}/ingest"
    if not file_list:
        return "No file selected."

    responses = []
    for f in file_list:
        filename = os.path.basename(f)
        files = {"file": open(f, "rb")}
        response = requests.post(api_url, files=files)
        if response.status_code != 200:
            responses.append(f"{filename}: ❌ Error: {response.text}")
        else:
            responses.append(f"{filename}: ✅ Success: {response.text}")
    return "\n".join(responses)


def stream_chat(user_input, chat_history, conversation_id):
    """
    Calls FastAPI SSE endpoint.
    - Receives conversation_id from backend (first event)
    - Streams tokens
    - Persists conversation_id in Gradio state
    """
    CHAT_API_URL = f"{BASE_URL}/chat"
    if not user_input.strip():
        # Yield current state unchanged
        yield user_input, chat_history, conversation_id
        return
    payload = {
        "conversation_id": conversation_id,  # None for first message
        "message": user_input,
    }

    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
    }

    assistant_message = ""
    chat_history.append({"role": "user", "content": user_input})
    yield "", chat_history, conversation_id

    with requests.post(
        CHAT_API_URL,
        json=payload,
        headers=headers,
        stream=True,
    ) as response:
        event_type = None
        chat_history.append({"role": "assistant", "content": ""})

        for raw_line in response.iter_lines(decode_unicode=True):
            logger.debug("Raw line: %s", raw_line)
            if not raw_line:
                continue

            # SSE event line
            if raw_line.startswith("event:"):
                event_type = raw_line.replace("event:", "").strip()
                continue

            # SSE data line
            if raw_line.startswith("data:"):
                data = raw_line.replace("data:", "")

                # Conversation ID from backend (first message only)
                if event_type == "conversation":
                    current_conversation_id = data.strip()
                    yield "", chat_history, current_conversation_id
                    continue

                # End of stream
                if event_type == "done":
                    break

                # Token streaming
                if event_type == "token":
                    assistant_message += data
                    chat_history[-1]["content"] = assistant_message

                    yield "", chat_history, current_conversation_id


def reset_conversation():
    """Start a fresh conversation"""
    return None, []


def reset_logic():
    """
    Resets Chatbot, Input Box, and Conversation ID State.
    """
    return [], "", None


# --- UI Layout ---
with gr.Blocks() as demo:
    gr.Markdown("### Chatbot with Send & Reset")

    # Hidden State for ID
    state = gr.State(None)
    with gr.Row(variant="panel"):
        with gr.Column(scale=1):
            # The File Upload Component
            file_input = gr.File(
                label="Upload Document (PDF/TXT/DOCX)",
                file_count="multiple",
                type="filepath",
            )
        with gr.Column(scale=2):
            # The Status Box
            ingest_status = gr.Textbox(
                label="Ingestion Status",
                placeholder="Waiting for file upload...",
                interactive=False,
                lines=3,
            )

    chatbot = gr.Chatbot(height=400)

    msg = gr.Textbox(placeholder="Type here...", show_label=False, scale=4)
    with gr.Row():
        send_btn = gr.Button("Send", variant="primary")
        reset_btn = gr.Button("Reset Chat", variant="stop")
    # with gr.Row():
    # Scale=4 makes the text box take up 80% of the row
    # Scale=1 makes the button take up 20%
    # send_btn = gr.Button("Send", variant="primary", scale=1)

    # reset_btn = gr.Button("Reset Conversation", variant="stop")

    # --- Event Wiring ---
    file_input.upload(fn=ingest_file, inputs=[file_input], outputs=[ingest_status])
    # 1. Pressing 'Enter' in the text box
    msg.submit(
        fn=stream_chat, inputs=[msg, chatbot, state], outputs=[msg, chatbot, state]
    )

    # 2. Clicking the 'Send' button (Same function!)
    send_btn.click(
        fn=stream_chat, inputs=[msg, chatbot, state], outputs=[msg, chatbot, state]
    )

    # 3. Clicking the 'Reset' button
    reset_btn.click(
        fn=reset_logic,
        inputs=None,
        outputs=[chatbot, msg, state],  # Clears all three
    )

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860)
