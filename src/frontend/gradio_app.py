import os

import gradio as gr
import requests

BASE_URL = "http://backend:9000"


# Login
def api_login(username, password):
    """
    Hits /login to get a JWT.
    Returns: Token, Visibility Updates
    """
    login_url = f"{BASE_URL}/login"
    try:
        # OAuth2PasswordRequestForm expects form-data
        response = requests.post(
            login_url, data={"username": username, "password": password}
        )

        if response.status_code == 200:
            token = response.json().get("access_token")
            return (
                token,
                gr.update(visible=False),  # login_view
                gr.update(visible=False),  # register_view
                gr.update(visible=True),  # app_view
                "",
            )
        else:
            return (
                None,
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
                f"❌ Error: {response.text}",
            )

    except Exception as e:
        return (
            None,
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            f"❌ Connection Error: {str(e)}",
        )


# Register api
def api_register(name, username, email, password):
    """
    Hits /register to create a user.
    Returns: Visibility Updates + Status Message
    """
    print("Registering user...")
    register_url = f"{BASE_URL}/register"
    payload = {"name": name, "username": username, "email": email, "password": password}

    try:
        response = requests.post(register_url, json=payload)

        if response.status_code == 200:
            print("Registration successful.", response.json())
            return (
                gr.update(visible=True),  # login_view
                gr.update(visible=False),  # register_view
                "✅ Registration successful! Please log in.",
            )
        else:
            print("Registration failed.", response.text)
            return (
                gr.update(visible=False),  # login_view
                gr.update(visible=True),  # register_view
                f"❌ Error: {response.text}",
            )
    except Exception as e:
        print("Connection error during registration.", str(e))
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            f"❌ Connection Error: {str(e)}",
        )


# Ingest Logic
def ingest_file(file_list, token):
    if not token:
        return "⚠️ Authentication Error: Please log in again."
    api_url = f"{BASE_URL}/api/v1/ingest"
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
            if response.status_code == 200:
                responses.append(f"{filename}: ✅ Success")
            else:
                responses.append(f"{filename}: ❌ Error: {response.text}")
        except Exception as e:
            responses.append(f"{filename}: ❌ System Error: {str(e)}")
    return "\n".join(responses)


# Chat logic to read stream response and show in gradio
def stream_chat(user_input, chat_history, conversation_id, token):
    if not token:
        chat_history.append(
            {"role": "assistant", "content": "⚠️ Session expired. Please log in."}
        )
        yield "", chat_history, conversation_id
        return

    CHAT_API_URL = f"{BASE_URL}/api/v1/chat"
    if not user_input.strip():
        yield user_input, chat_history, conversation_id
        return

    payload = {"conversation_id": conversation_id, "message": user_input}
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
    }

    chat_history.append({"role": "user", "content": user_input})
    yield "", chat_history, conversation_id

    try:
        with requests.post(
            CHAT_API_URL, json=payload, headers=headers, stream=True
        ) as response:
            if response.status_code == 401:
                chat_history.append(
                    {
                        "role": "assistant",
                        "content": "❌ Unauthorized.",
                    }
                )
                yield "", chat_history, conversation_id
                return

            event_type = None
            assistant_message = ""
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
                        conversation_id = data.strip()
                        yield "", chat_history, conversation_id
                        continue
                    if event_type == "token":
                        assistant_message += data
                        chat_history[-1]["content"] = assistant_message
                        yield "", chat_history, conversation_id
    except Exception as e:
        chat_history.append({"role": "assistant", "content": f"❌ Error: {str(e)}"})
        yield "", chat_history, conversation_id


def reset_logic():
    return [], "", None


# UI HELPERS (View Switching)
def show_register_page():
    # Hide Login, Show Register
    return gr.update(visible=False), gr.update(visible=True), ""


def show_login_page():
    # Show Login, Hide Register
    return gr.update(visible=True), gr.update(visible=False), ""


# GRADIO LAYOUT
with gr.Blocks() as demo:
    # Global States
    token_state = gr.State(None)
    conversation_state = gr.State(None)

    gr.Markdown("## Enterprise RAG Interface")

    # VIEW 1: LOGIN
    with gr.Column(visible=True) as login_view:
        gr.Markdown("### Login")
        l_user = gr.Textbox(label="Username")
        l_pass = gr.Textbox(label="Password", type="password")

        with gr.Row():
            login_btn = gr.Button("Login", variant="primary")
            goto_reg_btn = gr.Button("Register")

        login_msg = gr.Markdown("")

    # VIEW 2: REGISTER
    with gr.Column(visible=False) as register_view:
        gr.Markdown("### Create New Account")
        r_name = gr.Textbox(label="Full Name")
        r_user = gr.Textbox(label="Username")
        r_email = gr.Textbox(label="Email")
        r_pass = gr.Textbox(label="Password", type="password")

        with gr.Row():
            reg_submit_btn = gr.Button("Register", variant="primary")
            back_to_login_btn = gr.Button("Back to Login")

        reg_msg = gr.Markdown("")

    # VIEW 3: MAIN APP
    with gr.Column(visible=False) as app_view:
        with gr.Row(variant="panel"):
            with gr.Column(scale=1):
                file_input = gr.File(label="Upload Document", file_count="multiple")
            with gr.Column(scale=2):
                ingest_status = gr.Textbox(label="Status", interactive=False, lines=3)

        chatbot = gr.Chatbot(height=500)
        msg = gr.Textbox(placeholder="Ask a question...", show_label=False)

        with gr.Row():
            send_btn = gr.Button("Send", variant="primary")
            reset_btn = gr.Button("Reset", variant="stop")

        file_input.upload(
            ingest_file, inputs=[file_input, token_state], outputs=[ingest_status]
        )
        msg.submit(
            stream_chat,
            inputs=[msg, chatbot, conversation_state, token_state],
            outputs=[msg, chatbot, conversation_state],
        )
        send_btn.click(
            stream_chat,
            inputs=[msg, chatbot, conversation_state, token_state],
            outputs=[msg, chatbot, conversation_state],
        )
        reset_btn.click(reset_logic, outputs=[chatbot, msg, conversation_state])

    # NAVIGATION WIRING
    # 1. Login Button -> Try Login -> If Success, Show App
    login_btn.click(
        fn=api_login,
        inputs=[l_user, l_pass],
        outputs=[token_state, login_view, register_view, app_view, login_msg],
    )

    # 2. "Create Account" Button -> Switch to Register View
    goto_reg_btn.click(
        fn=show_register_page, outputs=[login_view, register_view, login_msg]
    )

    # 3. "Register" Submit Button -> Call API -> If Success, Switch to Login View
    reg_submit_btn.click(
        fn=api_register,
        inputs=[r_name, r_user, r_email, r_pass],
        outputs=[
            login_view,
            register_view,
            login_msg,
        ],
    )

    # 4. "Back to Login" Button -> Switch to Login View
    back_to_login_btn.click(
        fn=show_login_page, outputs=[login_view, register_view, reg_msg]
    )

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
