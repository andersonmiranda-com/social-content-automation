import json

from langchain.prompts import PromptTemplate

from modules.llm.utils import prompt_llm
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Prompt template for reels in JSON format
json_template = """
You are an expert scriptwriter for inspiring Instagram reels. Create a short script for a reel based on the following topic and respond only in JSON format with the following structure:

{{
  "content": "",     // Full script for the reel
  "title": "",       // Short headline, like a Facebook ad
  "subtitle": "",    // Short subtitle
  "caption": "",     // Summary of the reel in 2 short paragraphs, for the post text (no hashtags)
  "hashtags": ""     // 10 relevant hashtags separated by space
}}

Topic: {topic}

Requirements:
- The script must have a powerful hook, brief and emotional development, and a closing with reflection or call to action.
- The title must be very short and catchy, Facebook ad style.
- The subtitle must be short and complement the title.
- The caption must be a summary of the reel in 2 short, natural, and emotional paragraphs.
- The hashtags must be 10, relevant, separated by space, and each must start with the # symbol.
- Respond only with the JSON, no explanations or extra text.
- The script must be in Spanish.
"""

prompt = PromptTemplate.from_template(json_template)


def run(topic: str, output_file: str = "output.json") -> str:
    """
    Generate a reel script for a given topic.

    Args:
        topic (str): The topic for the reel.
        output_file (str, optional): Path to the output JSON file. Defaults to 'output.json'.

    Returns:
        str: The generated JSON string with the script, title, subtitle, caption, and hashtags.
    """
    formatted_prompt = prompt.format(topic=topic)
    result = prompt_llm(formatted_prompt)

    if output_file and result:
        try:
            data = json.loads(result)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return f"Error: Failed to parse JSON response"

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Content successfully saved to {output_file}")
            return f"Result saved to {output_file}"
        except IOError as e:
            logger.error(f"Failed to write file {output_file}: {e}")
            return f"Error: Failed to write file {output_file}"

    return result
