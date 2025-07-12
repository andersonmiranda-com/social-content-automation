"""
This is an example of how to run the full social post pipeline.
This script is the "entry point" that triggers the execution.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
# Make sure you have your OPENAI_API_KEY set in a .env file
load_dotenv()

# We need to check if the API key is set, otherwise, the LLM will fail.
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable not set.")
    print("Please create a .env file and add your OpenAI API key to it.")
else:
    # Import the pipeline we built
    from pipelines.social_post_pipeline import social_post_pipeline

    # Define the initial input for the pipeline
    input_data = {"topic": "The benefits of meditation for developers"}

    print("--- Starting Pipeline ---")
    print(f"Input Topic: {input_data['topic']}")
    print("-" * 20)

    # HERE IS THE INVOKE CALL
    # We call .invoke() on the fully constructed pipeline object
    final_result = social_post_pipeline.invoke(input_data)

    print("-" * 20)
    print("--- Pipeline Finished ---")
    print("Final Result:")
    print(final_result)
