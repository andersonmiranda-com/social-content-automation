"""
MindEssence Telegram Content Generation Chain

This chain generates content using RAG (Retrieval-Augmented Generation) based on a selected topic.
"""

from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from services.vector_store import vector_store_service
from utils.config_loader import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def generate_me_telegram_content_logic(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate content using RAG based on the selected topic.

    Args:
        data: Dictionary containing:
            - selected_topic: The topic to generate content about

    Returns:
        Dictionary containing the generated content
    """
    try:
        selected_topic = data.get("selected_topic")
        if not selected_topic:
            raise ValueError("No topic provided for content generation")

        logger.info("--- 🤖 Generating content with RAG ---")
        logger.info(f"Topic: {selected_topic}")

        # Load configuration
        config = load_config("rag")
        search_k = config.get("default_search_k", 4)

        # Search for relevant documents in vector store
        relevant_docs = vector_store_service.similarity_search(
            query=selected_topic, k=search_k
        )

        # Prepare context from relevant documents
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        logger.info(f"Found {len(relevant_docs)} relevant documents")

        # Generate content using LLM
        llm = ChatOpenAI(
            model=config.get("content_model", "gpt-4o-mini"),
            temperature=config.get("content_temperature", 0.4),
        )

        # Load prompt template from file
        from utils.file_utils import load_prompt_template

        prompt_template_str = load_prompt_template("prompts/rag_content_prompt.txt")
        prompt_template = ChatPromptTemplate.from_template(prompt_template_str)

        # Generate content
        chain = prompt_template | llm
        result = chain.invoke({"question": selected_topic, "context": context})

        # Parse JSON response
        import json

        try:
            response_content = str(result.content).strip()
            # Extract JSON from the response
            if "```json" in response_content:
                json_start = response_content.find("```json") + 7
                json_end = response_content.find("```", json_start)
                json_str = response_content[json_start:json_end].strip()
            else:
                json_str = response_content

            parsed_response = json.loads(json_str)
            generated_content = parsed_response.get("text", "")
            quote = parsed_response.get("quote", "")

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            # Fallback to raw content
            generated_content = str(result.content)
            quote = ""

        logger.info("✅ Content generated successfully")

        return {
            "status": "success",
            "generated_content": generated_content,
            "quote": quote,
            "topic": selected_topic,
            "context_documents_count": len(relevant_docs),
            "model_used": config.get("content_model", "gpt-4o-mini"),
        }

    except Exception as e:
        logger.error(f"Error generating RAG content: {e}")
        return {
            "status": "error",
            "message": f"Failed to generate content: {str(e)}",
            "generated_content": None,
        }


# Create the chain
me_telegram_content_chain = RunnableLambda(generate_me_telegram_content_logic)
