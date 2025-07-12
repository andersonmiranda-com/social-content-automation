"""
Pydantic schemas for API input and output validation.
This provides a clear contract for the API and helps LangServe build the playground UI.
"""

from pydantic import BaseModel, Field


class SocialPostInput(BaseModel):
    """
    The expected input schema for the social post pipeline.
    """

    topic: str = Field(
        ...,
        title="Topic",
        description="The main topic for the social media post generation.",
    )
