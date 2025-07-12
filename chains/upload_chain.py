"""
This chain represents the business logic for uploading media.

It acts as an abstraction layer. It knows *what* to do (upload media for a post),
while the 'tool' it calls knows *how* to do it (e.g., call the Cloudinary API).

This makes the system more modular. If we wanted to switch from Cloudinary to S3,
we would only need to change this file to point to a new 's3_tool', and none of the
main pipelines would need to be updated.
"""

# We import the specific tool implementation
from tools.cloudinary_tool import upload_to_cloudinary_chain

# For now, the business logic is simple: just use the Cloudinary tool.
# This provides a stable import path for all pipelines.
upload_chain = upload_to_cloudinary_chain
