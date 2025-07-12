"""
Fake Cloudinary Tool
- Simulates uploading an image URL and returns a new "cloudinary" URL.
"""

from langchain_core.runnables import RunnableLambda


def _upload_image_logic(data: dict) -> dict:
    """
    Receives image data, prints it, and returns a (fake) Image URL.
    """
    image_url_to_upload = data.get("image_url", "no_url_provided")

    print(f"--- ☁️ Uploading to Cloudinary ---")
    print(f"   Uploading image from: {image_url_to_upload}")

    # Simulate a new URL after upload
    fake_cloudinary_url = f"https://res.cloudinary.com/demo/image/upload/v1/{image_url_to_upload.split('/')[-1]}.jpg"
    print(f"   ✅  Upload complete. New URL: {fake_cloudinary_url}")

    # Return a generic key, not a service-specific one.
    return {"image_url": fake_cloudinary_url}


upload_to_cloudinary_chain = RunnableLambda(_upload_image_logic)
