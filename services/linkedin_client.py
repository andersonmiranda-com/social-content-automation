"""
Client for handling communication with the LinkedIn API.

This client is responsible for low-level HTTP requests to the
LinkedIn API, including handling authentication and request/response
parsing for actions like posting content.
"""

import os
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, Any

import requests
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from utils.config_loader import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Constants for LinkedIn OAuth2
TOKEN_FILE = "linkedin_token.json"
AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
API_BASE_URL = "https://api.linkedin.com"


class LinkedInClient:
    """A client for interacting with the LinkedIn API with automated OAuth handling."""

    def __init__(self, config_key: str = "linkedin"):
        """Initializes the LinkedIn client."""
        self.config = load_config(config_key)
        self.client_id = os.environ.get("LINKEDIN_CLIENT_ID") or self.config.get(
            "client_id"
        )
        self.client_secret = os.environ.get(
            "LINKEDIN_CLIENT_SECRET"
        ) or self.config.get("client_secret")
        self.base_url = API_BASE_URL
        self.scopes = self.config.get("scopes")
        self.access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")

        if not self.client_id or not self.client_secret:
            raise ValueError("LinkedIn client_id and client_secret must be configured.")

        if not self.scopes:
            raise ValueError("LinkedIn scopes must be configured in linkedin.yaml.")

        logger.info(
            f"LinkedIn Client initialized with Client ID: {self.client_id[:5]}..."
        )
        self.session = self._get_credentials()

    def _get_credentials(self) -> OAuth2Session:
        """
        Handles the OAuth2 flow to get a valid session.
        - Tries to load token from an environment variable (for production).
        - Falls back to a local token file (for development).
        - If no valid token, initiates the browser-based authorization flow.
        """
        token = None
        redirect_uri = "http://localhost:8080/callback"

        # 1. Production-first: Try to load a full access token from env
        if self.access_token:
            logger.info(
                "Found LINKEDIN_ACCESS_TOKEN in environment. Using it directly."
            )
            token = {
                "access_token": self.access_token,
                "token_type": "Bearer",
            }
            # Create a session directly with this token
            return OAuth2Session(
                client_id=self.client_id, token=token, scope=self.scopes
            )

        # 2. Production-fallback: Try to load from environment variable (for refresh)
        refresh_token_env = os.environ.get("LINKEDIN_REFRESH_TOKEN")
        if refresh_token_env:
            logger.info("Found LINKEDIN_REFRESH_TOKEN in environment. Using it.")
            token = {
                "refresh_token": refresh_token_env,
                "token_type": "Bearer",
                "access_token": "will_be_refreshed",  # Force refresh
                "expires_in": "-30",
            }

        # 3. Fallback: Try to load from local file
        elif os.path.exists(TOKEN_FILE):
            logger.info(f"Loading credentials from local file: {TOKEN_FILE}")
            with open(TOKEN_FILE, "r") as f:
                token = json.load(f)

        def token_saver(t: Dict[str, Any]):
            logger.info(f"Saving new token to {TOKEN_FILE}")
            with open(TOKEN_FILE, "w") as f:
                json.dump(t, f)
            # Also log the refresh token for easy use in production env vars
            if "refresh_token" in t:
                logger.info(
                    f"✅ New Refresh Token obtained. Set this as LINKEDIN_REFRESH_TOKEN environment variable for production:\n"
                    f"LINKEDIN_REFRESH_TOKEN='{t['refresh_token']}'"
                )

        session = OAuth2Session(
            client_id=self.client_id,
            token=token,
            auto_refresh_url=TOKEN_URL,
            auto_refresh_kwargs={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            token_updater=token_saver,
            scope=self.scopes,
            redirect_uri=redirect_uri,
        )

        if not session.authorized:
            logger.info("Not authorized. Starting LinkedIn authorization flow...")
            authorization_url, state = session.authorization_url(AUTHORIZATION_URL)

            print("✅ Please authorize this application with LinkedIn:")
            print("   (Opening browser automatically...)")
            webbrowser.open(authorization_url)

            # Wait for the user to authorize and the local server to capture the redirect
            authorization_response = self._wait_for_auth_code()

            logger.info(
                f"Full authorization callback URL received: {authorization_response}"
            )

            logger.info("Authorization response received. Fetching token manually...")
            try:
                # Manual token fetch using requests to bypass oauthlib issues
                parsed_url = urlparse(authorization_response)
                query_params = parse_qs(parsed_url.query)

                # Check for an error returned from LinkedIn
                if "error" in query_params:
                    error = query_params.get("error", ["Unknown"])[0]
                    error_description = query_params.get(
                        "error_description", ["No description provided."]
                    )[0]
                    error_message = (
                        f"LinkedIn authorization failed. Error: '{error}'. "
                        f"Description: '{error_description}'"
                    )
                    logger.error(error_message)
                    raise ValueError(error_message)

                auth_code = query_params.get("code", [None])[0]

                if not auth_code:
                    raise ValueError("Authorization code not found in callback URL.")

                token_payload = {
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "redirect_uri": redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                }

                response = requests.post(TOKEN_URL, data=token_payload)
                response.raise_for_status()
                token_data = response.json()

                # Manually update the session with the new token
                session.token = token_data

                logger.info("✅ LinkedIn token fetched and saved successfully.")
                token_saver(session.token)

            except Exception as e:
                logger.error(f"Error fetching token manually: {e}")
                if isinstance(e, requests.exceptions.HTTPError):
                    logger.error(f"Response Body: {e.response.text}")
                raise

        return session

    def _wait_for_auth_code(self) -> str:
        """
        Starts a local server to wait for the OAuth redirect and returns the full redirect URL.
        """
        auth_code_holder = {}

        class OAuthCallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                # We need the full URL for requests-oauthlib
                auth_code_holder["url"] = self.path
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<h1>Authorization successful!</h1><p>You can close this tab now.</p>"
                )
                logger.info("Authorization code received successfully via callback.")

        server_address = ("", 8080)
        httpd = HTTPServer(server_address, OAuthCallbackHandler)
        logger.info("Waiting for authorization on http://localhost:8080/callback ...")
        httpd.handle_request()  # Handle one request and close
        httpd.server_close()

        if "url" not in auth_code_holder:
            raise RuntimeError("Could not capture authorization redirect.")

        return f"http://localhost:8080{auth_code_holder['url']}"

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """
        Makes an authenticated request to the LinkedIn API.
        Handles token refreshes automatically.
        """
        url = f"{self.base_url}/{endpoint}"

        # Default headers for LinkedIn API
        request_headers = {
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.request(
                method,
                url,
                json=json_data,
                data=data,
                headers=request_headers,
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"API request to {url} failed: {e}")
            if e.response is not None:
                logger.error(f"Response Body: {e.response.text}")
            raise
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during API request to {url}: {e}"
            )
            raise

    def get_user_profile(self) -> Dict[str, Any]:
        """
        Fetches the authenticated user's profile information using the OIDC /userinfo endpoint.
        The user URN (e.g., 'urn:li:person:xxxx') is required for posting.
        """
        # This endpoint is part of OIDC and has a fixed, absolute URL,
        # separate from the versioned /rest API.
        userinfo_url = "https://api.linkedin.com/v2/userinfo"
        logger.info(
            f"Fetching user profile from LinkedIn's OIDC endpoint: {userinfo_url}"
        )

        try:
            # We make a direct request here instead of using self._request
            # because _request is designed for the versioned /rest/ API.
            response = self.session.get(userinfo_url)
            response.raise_for_status()
            profile_data = response.json()

            # Adapt the OIDC userinfo response to the structure our app needs.
            # The 'sub' field from /userinfo corresponds to the person URN for posting.
            user_id = profile_data.get("sub")
            if not user_id:
                raise ValueError(
                    "Could not find 'sub' (person ID) in OIDC userinfo response."
                )

            # Ensure the ID is in the full URN format required by the UGC Posts API.
            if not user_id.startswith("urn:li:person:"):
                author_urn = f"urn:li:person:{user_id}"
            else:
                author_urn = user_id

            profile_data["id"] = author_urn
            profile_data["localizedFirstName"] = profile_data.get("given_name")
            profile_data["localizedLastName"] = profile_data.get("family_name")
            full_name = profile_data.get("name", "")

            logger.info(
                f"Successfully fetched profile for: {full_name} (URN: {author_urn})"
            )
            return profile_data

        except requests.exceptions.RequestException as e:
            logger.error(f"API request to {userinfo_url} failed: {e}")
            if e.response is not None:
                logger.error(f"Response Body: {e.response.text}")
            raise

    def publish_text_post(self, text: str) -> Dict[str, Any]:
        """Publishes a text-only post to LinkedIn."""
        profile = self.get_user_profile()
        author_urn = profile["id"]

        post_body = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        logger.info("Publishing text post to LinkedIn...")
        response = self._request("POST", "v2/ugcPosts", json_data=post_body)
        post_data = response.json()
        logger.info(f"Successfully published post with ID: {post_data['id']}")
        return post_data

    def _register_image_upload(self, author_urn: str) -> Dict[str, Any]:
        """
        Step 1: Register the image for upload with LinkedIn.
        Returns the asset URN and the upload URL.
        """
        logger.info("Registering image upload with LinkedIn...")
        logger.info(f"Author URN being sent: {author_urn}")

        url = f"{self.base_url}/v2/assets?action=registerUpload"

        # Manually construct headers to ensure no unexpected values are added
        # by the requests-oauthlib session object.
        headers = {
            "Authorization": f"Bearer {self.session.token['access_token']}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        register_body = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": author_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        }

        logger.info(f"Request body: {register_body}")

        try:
            # Using requests.post directly to make a clean, isolated call.
            response = requests.post(url, headers=headers, json=register_body)

            # Log response details for debugging
            logger.info(f"Response Status: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")

            if response.status_code != 200:
                logger.error(f"LinkedIn API returned status {response.status_code}")
                logger.error(f"Response body: {response.text}")

            response.raise_for_status()

            upload_data = response.json()
            logger.info("Successfully registered image upload")

            return {
                "asset_urn": upload_data["value"]["asset"],
                "upload_url": upload_data["value"]["uploadMechanism"][
                    "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
                ]["uploadUrl"],
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to register image upload: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise
        except KeyError as e:
            logger.error(f"Unexpected response structure: {e}")
            logger.error(f"Response data: {upload_data}")
            raise ValueError(f"Unexpected response structure from LinkedIn API: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during image upload registration: {e}")
            raise

    def _upload_image_data(self, upload_url: str, image_data: bytes):
        """Step 2: Upload the raw image bytes to the provided URL."""
        logger.info(f"Uploading image data to LinkedIn's storage...")
        response = self.session.post(
            upload_url,
            data=image_data,
            headers={"Content-Type": "application/octet-stream"},
        )
        response.raise_for_status()
        logger.info("Image data uploaded successfully.")

    def publish_post_with_image(self, text: str, image_url: str) -> Dict[str, Any]:
        """
        Downloads an image from a URL, uploads it to LinkedIn, and publishes a post.
        """
        # Get author URN first
        profile = self.get_user_profile()
        author_urn = profile["id"]

        # Step 1: Register the upload
        upload_info = self._register_image_upload(author_urn)
        asset_urn = upload_info["asset_urn"]
        upload_url = upload_info["upload_url"]

        # Download the image from the public URL
        logger.info(f"Downloading image from {image_url}...")
        try:
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            image_data = image_response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download image from {image_url}: {e}")
            raise

        # Step 2: Upload the image data
        self._upload_image_data(upload_url, image_data)

        # Step 3: Create the post with the image asset
        post_body = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "media": asset_urn,
                        }
                    ],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        logger.info("Publishing post with image to LinkedIn...")
        response = self._request("POST", "v2/ugcPosts", json_data=post_body)
        post_data = response.json()
        logger.info(f"Successfully published post with ID: {post_data['id']}")
        return post_data
