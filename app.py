"""
Main FastAPI application to serve the LangChain pipelines.
"""

import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from langserve import add_routes

# Import the main pipeline
from pipelines.social_post_pipeline import social_post_pipeline

# Load environment variables
load_dotenv()

# Create the FastAPI app
app = FastAPI(
    title="Social Content Automation API",
    version="1.0",
    description="An API for generating social media content using LangChain.",
)


@app.post("/invoke")
async def invoke_pipeline() -> List[dict]:
    """
    Invokes the social post pipeline.
    This endpoint uses .batch() to run the pipeline in a controlled manner,
    which is more stable for heavy, CPU-intensive tasks under a server environment.
    We pass a list with a single empty dictionary to trigger one full run.
    """
    # Use .batch() for a more stable, controlled execution of the pipeline.
    results = await social_post_pipeline.abatch([{}])
    return results


# Add the LangServe routes for interactive development and playground.
# This provides a UI but may be less stable for very heavy, parallel loads.
add_routes(
    app,
    social_post_pipeline,
    path="/social-post",
)


# A simple root endpoint for health checks
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Social Content Automation API!"}


# Optional: Add a check for the API key on startup
@app.on_event("startup")
async def startup_event():
    if not os.getenv("OPENAI_API_KEY"):
        print("\n" + "=" * 80)
        print("WARNING: OPENAI_API_KEY environment variable not set.")
        print("The application will run, but any calls to OpenAI will fail.")
        print("Please create a .env file and add your OpenAI API key to it.")
        print("=" * 80 + "\n")
