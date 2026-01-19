import os

import gradio as gr
import requests

BASE_URL = "http://backend:9000/api/v1"


def api_login(username, password):
    """
    Hits the FastAPI /login endpoint to get a JWT.
    """
    print(f"Attempting login for user: {username}")
    login_url = "http://backend:9000/login"
    try:
        response = requests.post(
            login_url, data={"username": username, "password": password}
        )

        if response.status_code == 200:
            print(f"Login successful! {response.json()}")
            token = response.json().get("access_token")
            return token, gr.update(visible=False), gr.update(visible=True), ""
        else:
            print(f"Login failed: {response.text}")
            return (
                None,
                gr.update(visible=True),
                gr.update(visible=False),
                f"Error: {response.text}",
            )

    except Exception as e:
        return (
            None,
            gr.update(visible=True),
            gr.update(visible=False),
            f"Connection Error: {str(e)}",
        )


def ingest_file(file_list, token):
    """
    Uploads file with Bearer Token.
    """
    if not token:
        return "⚠️ Authentication Error: Please log in again."

    api_url = f"{BASE_URL}/ingest"
    if not file_list:
        return "No file selected."

    headers = {"Authorization": f"Bearer {token}"}

    responses = []
    for f in file_list:
        filename = os.path.basename(f)
        try:
            with open(f, "rb") as file_obj:
                files = {"file": file_obj}
                response = requests.post(api_url, files=files, headers=headers)

            if response.status_code != 200:
                responses.append(f"{filename}: ❌ Error: {response.text}")
            else:
                responses.append(f"{filename}: ✅ Success. Response: {response.json()}")
        except Exception as e:
            responses.append(f"{filename}: ❌ System Error: {str(e)}")

    return "\n".join(responses)


def stream_chat(user_input, chat_history, conversation_id, token):
    """
    Streams chat with Bearer Token.
    """
    if not token:
        chat_history.append(
            {
                "role": "assistant",
                "content": "⚠️ Session expired. Please refresh and log in.",
            }
        )
        yield "", chat_history, conversation_id
        return

    CHAT_API_URL = f"{BASE_URL}/chat"

    if not user_input.strip():
        yield user_input, chat_history, conversation_id
        return

    payload = {
        "conversation_id": conversation_id,
        "message": user_input,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
    }

    assistant_message = ""
    chat_history.append({"role": "user", "content": user_input})
    yield "", chat_history, conversation_id

    try:
        with requests.post(
            CHAT_API_URL,
            json=payload,
            headers=headers,
            stream=True,
        ) as response:
            # Handle 401 specifically
            if response.status_code == 401:
                chat_history.append(
                    {
                        "role": "assistant",
                        "content": "❌ Unauthorized. Check your login.",
                    }
                )
                yield "", chat_history, conversation_id
                return

            event_type = None
            chat_history.append({"role": "assistant", "content": ""})

            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue

                if raw_line.startswith("event:"):
                    event_type = raw_line.replace("event:", "").strip()
                    continue

                if raw_line.startswith("data:"):
                    data = raw_line.replace("data:", "")

                    if event_type == "conversation":
                        current_conversation_id = data.strip()
                        yield "", chat_history, current_conversation_id
                        continue

                    if event_type == "done":
                        break

                    if event_type == "token":
                        assistant_message += data
                        chat_history[-1]["content"] = assistant_message
                        yield "", chat_history, current_conversation_id
    except Exception as e:
        chat_history.append(
            {"role": "assistant", "content": f"❌ Connection Error: {str(e)}"}
        )
        yield "", chat_history, conversation_id


def reset_logic():
    return [], "", None


with gr.Blocks() as demo:
    token_state = gr.State(None)  # Stores the JWT Token
    conversation_state = gr.State(None)  # Stores Conversation ID

    gr.Markdown("## Enterprise RAG Interface")

    # VIEW 1: LOGIN SCREEN
    with gr.Column(visible=True) as login_view:
        gr.Markdown("### Please Log In")
        username_input = gr.Textbox(label="Username")
        password_input = gr.Textbox(label="Password", type="password")
        login_btn = gr.Button("Login", variant="primary")
        login_msg = gr.Markdown("")

    # VIEW 2: MAIN APP (Hidden)
    with gr.Column(visible=False) as app_view:
        with gr.Row(variant="panel"):
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="Upload Document",
                    file_count="multiple",
                    type="filepath",
                )
            with gr.Column(scale=2):
                ingest_status = gr.Textbox(
                    label="Ingestion Status",
                    placeholder="Waiting for upload...",
                    interactive=False,
                    lines=3,
                )

        chatbot = gr.Chatbot(height=500)

        with gr.Row():
            msg = gr.Textbox(
                placeholder="Ask a question about your documents...",
                show_label=False,
                scale=4,
            )
            send_btn = gr.Button("Send", variant="primary", scale=1)
            reset_btn = gr.Button("Reset", variant="stop", scale=1)

        # Ingest needs the Token
        file_input.upload(
            fn=ingest_file,
            inputs=[file_input, token_state],  # Pass token state
            outputs=[ingest_status],
        )

        # Chat needs the Token
        msg.submit(
            fn=stream_chat,
            inputs=[msg, chatbot, conversation_state, token_state],  # Pass token state
            outputs=[msg, chatbot, conversation_state],
        )

        send_btn.click(
            fn=stream_chat,
            inputs=[msg, chatbot, conversation_state, token_state],  # Pass token state
            outputs=[msg, chatbot, conversation_state],
        )

        reset_btn.click(
            fn=reset_logic,
            outputs=[chatbot, msg, conversation_state],
        )

    login_btn.click(
        fn=api_login,
        inputs=[username_input, password_input],
        outputs=[token_state, login_view, app_view, login_msg],
    )

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
