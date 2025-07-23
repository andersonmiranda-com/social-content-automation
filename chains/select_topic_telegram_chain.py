"""
Select Topic RAG Chain

This chain randomly selects a topic from the topics file for content generation.
"""

import random
from typing import Any, Dict

from langchain_core.runnables import RunnableLambda

from utils.config_loader import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def select_topic_logic(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select a random topic from the topics file.

    Args:
        input_data: Dictionary (not used, but required for chain compatibility)

    Returns:
        Dictionary containing the selected topic
    """
    try:
        config = load_config("rag")
        topics_file = config.get("topics_file", "data/topics/topics.txt")

        logger.info("--- 🎯 Selecting random topic ---")

        # Read topics from file
        topics = []
        with open(topics_file, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    topics.append(line)

        if not topics:
            raise ValueError("No topics found in topics file")

        # Select random topic
        selected_topic = random.choice(topics)

        logger.info(f"Selected topic: {selected_topic}")

        return {
            "status": "success",
            "selected_topic": selected_topic,
            "total_topics_available": len(topics),
            "topics_file": topics_file,
        }

    except Exception as e:
        logger.error(f"Error selecting topic: {e}")
        return {
            "status": "error",
            "message": f"Failed to select topic: {str(e)}",
            "selected_topic": None,
        }


# Create the chain
select_topic_telegram_chain = RunnableLambda(select_topic_logic)
