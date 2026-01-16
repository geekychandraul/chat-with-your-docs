def format_history(messages):
    """Format a sequence of ChatMessage objects into a single text blob.

    Args:
        messages (Iterable[ChatMessage]): ordered list of chat messages.

    Returns:
        str: a newline-separated representation of the conversation.
    """
    lines = []
    for msg in messages:
        if msg.role == "user":
            lines.append(f"User: {msg.content}")
        elif msg.role == "assistant":
            lines.append(f"Assistant: {msg.content}")
    return "\n".join(lines)
