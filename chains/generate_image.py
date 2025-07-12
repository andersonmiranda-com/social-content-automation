"""
Generate Image Chain
"""

from langchain_core.runnables import RunnableLambda


def generate_image_logic(state: dict) -> dict:
    """
    Placeholder for image generation logic.
    It should take a topic or text and return an image URL.
    """
    print("Generating image for:", state.get("topic"))
    # In a real scenario, this would call Canva or another image service
    state["image_url"] = "https://picsum.photos/1080/1080"
    return state


generate_image_chain = RunnableLambda(generate_image_logic)
