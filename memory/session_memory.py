from strands.agent.conversation_manager import SlidingWindowConversationManager


def make_session_memory(window_size: int = 10):
    """Bounded short-term memory: keeps only the most recent `window_size`
    messages in context. Resets whenever the Agent object is recreated
    (e.g. on process restart) — unrelated to the long-term SQLite store.
    """
    return SlidingWindowConversationManager(window_size=window_size)
