"""
Main FastAPI application to serve the LangChain pipelines.
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from langserve import add_routes

# Import the main pipeline and the input schema
from pipelines.social_post_pipeline import social_post_pipeline
from schemas import SocialPostInput

# Load environment variables
load_dotenv()

# Create a new, typed pipeline by attaching the Pydantic model.
# This does NOT change the runtime behavior of the pipeline (it still gets a dict),
# but it gives LangServe the necessary information to build the UI.
typed_pipeline = social_post_pipeline.with_types(input_type=SocialPostInput)  # type: ignore

# Create the FastAPI app
app = FastAPI(
    title="Social Content Automation API",
    version="1.0",
    description="An API for generating social media content using LangChain.",
)

# Add the LangServe route for our NEW typed pipeline
add_routes(
    app,
    typed_pipeline,
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
