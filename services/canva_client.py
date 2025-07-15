"""
Client for handling communication with the Canva API.

This client is responsible for low-level HTTP requests to the
Canva REST API, including handling authentication (OAuth2)
and request/response parsing. It manages the OAuth token lifecycle,
refreshing it automatically when needed.
"""

import os
import json
import webbrowser
import hashlib
import base64
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, urlencode
from typing import Optional, Dict, Any, Callable, Awaitable

import httpx
import requests  # Add plain requests for manual token fetching
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import WebApplicationClient

from utils.config_loader import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Constants for OAuth
TOKEN_FILE = "canva_token.json"
AUTHORIZATION_URL = "https://www.canva.com/api/oauth/authorize"
TOKEN_URL = "https://api.canva.com/rest/v1/oauth/token"
# Updated list of scopes to match the Canva developer portal configuration
SCOPES = list(
    set(
        [
            "brandtemplate:content:read",
            "design:permission:read",
            "app:write",
            "brandtemplate:meta:read",
            "profile:read",
            "folder:permission:write",
            "folder:read",
            "app:read",
            "design:content:write",
            "folder:permission:read",
            "design:permission:write",
            "design:meta:read",
            "design:content:read",
            "asset:read",
            "comment:read",
            "asset:write",
            "folder:write",
            "comment:write",
        ]
    )
)
CANVA_SCOPES_STRING = " ".join(SCOPES)


class CanvaClient:
    """A client for interacting with the Canva API with automated OAuth handling."""

    def __init__(self, config_key: str = "canva"):
        self.config = load_config(config_key)
        self.client_id = self.config.get("client_id")
        self.client_secret = self.config.get("client_secret")
        self.base_url = "https://api.canva.com/rest/v1"  # Correct base URL

        if not self.client_id or not self.client_secret:
            raise ValueError("Canva client_id and client_secret must be configured.")

        logger.info(
            f"--- [DEBUG] Canva Client initialized with Client ID: {self.client_id[:5]}... ---"
        )

        self.session = self._get_credentials()

    def _get_credentials(self) -> OAuth2Session:
        token = None

        # --- Production-first: Try to load from environment variables ---
        refresh_token = os.environ.get("CANVA_REFRESH_TOKEN")
        if refresh_token:
            logger.info(
                "Found CANVA_REFRESH_TOKEN. Building credentials from environment."
            )
            # Construct a token object that requests_oauthlib can use
            token = {
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                # The access token is empty, forcing a refresh on the first call
                "access_token": "will_be_refreshed",
                "expires_in": "-30",  # Negative expires_in forces refresh
            }

        # --- Fallback to local file for development ---
        elif os.path.exists(TOKEN_FILE):
            logger.info(f"Loading credentials from local file: {TOKEN_FILE}")
            with open(TOKEN_FILE, "r") as f:
                token = json.load(f)

        def token_saver(t):
            with open(TOKEN_FILE, "w") as f:
                json.dump(t, f)

        redirect_uri = "http://127.0.0.1:8080/callback"

        session = OAuth2Session(
            client_id=self.client_id,
            token=token,
            auto_refresh_url=TOKEN_URL,
            auto_refresh_kwargs={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            token_updater=token_saver,
            scope=CANVA_SCOPES_STRING,
            redirect_uri=redirect_uri,
        )

        if not session.authorized:
            logger.info(
                "Canva token not found or invalid. Starting authorization flow..."
            )

            # --- Step 1: Manually create PKCE and Authorization URL ---
            code_verifier = secrets.token_urlsafe(
                64
            )  # Use secrets module for a more robust verifier
            logger.debug(f"Generated PKCE Code Verifier: {code_verifier}")

            code_challenge_bytes = hashlib.sha256(
                code_verifier.encode("utf-8")
            ).digest()
            code_challenge = (
                base64.urlsafe_b64encode(code_challenge_bytes)
                .decode("utf-8")
                .rstrip("=")
            )
            logger.debug(f"Generated PKCE Code Challenge: {code_challenge}")

            state = secrets.token_urlsafe(16)
            params = {
                "response_type": "code",
                "client_id": self.client_id,
                "redirect_uri": redirect_uri,
                "scope": CANVA_SCOPES_STRING,
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            }
            query_string = urlencode(params)
            auth_url = f"{AUTHORIZATION_URL}?{query_string}"

            print("✅ Please authorize this application with Canva:")
            print("   (Opening browser automatically...)")
            webbrowser.open(auth_url)

            # --- Step 2: Wait for the authorization code from the local server ---
            auth_code = self._wait_for_auth_code(state)

            # --- Step 3: Manually exchange the code for a token ---
            logger.info("Authorization code received. Fetching token manually...")

            token_payload = {
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code_verifier": code_verifier,  # Use the verifier from Step 1
            }

            response = requests.post(TOKEN_URL, data=token_payload)

            if response.status_code != 200:
                logger.error(
                    f"Failed to fetch token. Status: {response.status_code}, Body: {response.text}"
                )
                raise RuntimeError(f"Could not fetch Canva token: {response.text}")

            token = response.json()

            # --- Step 4: Save token and update the session ---
            token_saver(token)
            session.token = token
            logger.info("✅ Canva token fetched and saved successfully.")

        return session

    def _wait_for_auth_code(self, expected_state: str) -> str:
        """
        Starts a local server to wait for the OAuth redirect, validates state,
        and returns the code.
        """
        auth_data_holder = {}

        class OAuthCallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)

                # --- Security Check: Validate State ---
                received_state = query_params.get("state", [None])[0]
                if received_state != expected_state:
                    logger.error(
                        f"Invalid state. Expected '{expected_state}', got '{received_state}'"
                    )
                    auth_data_holder["error"] = "Invalid state parameter. CSRF attack?"
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<h1>Error: Invalid state parameter.</h1>")
                    return

                # --- Check for Code or Error from Canva ---
                if "code" in query_params:
                    auth_data_holder["code"] = query_params["code"][0]
                    logger.info(
                        "Authorization code received successfully via callback."
                    )
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(
                        b"<h1>Authorization successful!</h1><p>You can close this tab now.</p>"
                    )
                elif "error" in query_params:
                    error = query_params["error"][0]
                    error_description = query_params.get(
                        "error_description", ["No description provided."]
                    )[0]
                    logger.error(
                        f"Canva returned an OAuth error: {error} - {error_description}"
                    )
                    auth_data_holder["error"] = f"Canva error: {error}"
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(
                        f"<h1>Error during Canva authorization:</h1><p>{error_description}</p>".encode(
                            "utf-8"
                        )
                    )
                else:
                    logger.error(
                        "OAuth callback received without a 'code' or 'error' parameter."
                    )
                    auth_data_holder["error"] = "Malformed response from Canva."
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<h1>Error: Invalid callback parameters.</h1>")

        server = HTTPServer(("127.0.0.1", 8080), OAuthCallbackHandler)
        logger.info(
            "Waiting for authorization callback on http://127.0.0.1:8080/callback..."
        )
        server.handle_request()
        server.server_close()

        if "error" in auth_data_holder:
            raise RuntimeError(
                f"Failed to retrieve authorization code from Canva: {auth_data_holder['error']}"
            )

        if "code" not in auth_data_holder:
            raise RuntimeError(
                "Failed to retrieve authorization code from Canva for an unknown reason."
            )

        return auth_data_holder["code"]

    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        content: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Makes an asynchronous request to the Canva API using the OAuth session."""

        request_url = f"{self.base_url}{endpoint}"

        # httpx doesn't integrate directly with requests-oauthlib, so we manage headers manually.
        # The session object handles token refresh for us when we access .token
        auth_header = f"Bearer {self.session.token['access_token']}"

        final_headers = {"Authorization": auth_header, "Accept": "application/json"}
        if headers:
            final_headers.update(headers)

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=request_url,
                    json=json_data,
                    content=content,
                    headers=final_headers,
                )
                response.raise_for_status()
                return {} if response.status_code == 204 else response.json()
            except httpx.HTTPStatusError as e:
                # If token expired or is forbidden, refresh and retry.
                # Some APIs return 403 for expired tokens.
                if e.response.status_code in [401, 403]:
                    logger.info(
                        f"Token may be invalid ({e.response.status_code}). Refreshing and retrying..."
                    )
                    # Note: This refresh part is synchronous. For a fully async app,
                    # this might need a dedicated async-oauth library.
                    self.session.refresh_token(
                        TOKEN_URL,
                        client_id=self.client_id,
                        client_secret=self.client_secret,
                    )

                    auth_header = f"Bearer {self.session.token['access_token']}"
                    final_headers["Authorization"] = auth_header

                    response = await client.request(
                        method=method,
                        url=request_url,
                        json=json_data,
                        content=content,
                        headers=final_headers,
                    )
                    response.raise_for_status()
                    return {} if response.status_code == 204 else response.json()

                logger.error(
                    f"API error calling {e.request.url!r}: {e.response.status_code} - {e.response.text}"
                )
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error calling {e.request.url!r}: {e}")
                raise

    async def upload_asset(
        self, file_content: bytes, name_base64: str
    ) -> Dict[str, Any]:
        """
        Uploads an asset to Canva.

        This corresponds to the 'Canva API - Upload Image' node in the n8n workflow.

        Args:
            file_content: The binary content of the file to upload.
            name_base64: The base64-encoded name of the asset.

        Returns:
            A dictionary containing the response from the Canva API,
            which includes the upload job details.
        """
        logger.info(f"Uploading asset with name (base64): {name_base64}")
        endpoint = "/asset-uploads"

        # Metadata header as specified in the n8n workflow
        metadata_header = f'{{"name_base64":"{name_base64}"}}'

        headers = {
            "Content-Type": "application/octet-stream",
            "Asset-Upload-Metadata": metadata_header,
        }

        return await self._request(
            method="POST",
            endpoint=endpoint,
            content=file_content,
            headers=headers,
        )

    async def get_asset_upload_status(self, job_id: str) -> Dict[str, Any]:
        """
        Gets the status of an asset upload job.

        This corresponds to the 'Get Asset ID' node in the n8n workflow.

        Args:
            job_id: The ID of the upload job returned by `upload_asset`.

        Returns:
            A dictionary with the job status and asset details upon completion.
        """
        logger.info(f"Getting status for asset upload job: {job_id}")
        endpoint = f"/asset-uploads/{job_id}"

        return await self._request(method="GET", endpoint=endpoint)

    async def autofill_template(
        self, asset_id: str, title: str, subtitle: str
    ) -> Dict[str, Any]:
        """
        Populates a brand template with data (text and an image asset).

        This corresponds to the 'AutoFill Template' node in the n8n workflow.

        Args:
            asset_id: The ID of the uploaded image asset.
            title: The main title text to insert into the template.
            subtitle: The subtitle text to insert into the template.

        Returns:
            A dictionary containing the job details for the autofill task.
        """
        logger.info(f"Autofilling template with asset ID: {asset_id}")
        endpoint = "/autofills"
        brand_template_id = self.config.get("brand_template_id")

        if not brand_template_id:
            raise ValueError("Canva brand_template_id is not configured.")

        json_data = {
            "brand_template_id": brand_template_id,
            "data": {
                "title": {"type": "text", "text": title},
                "subtitle": {"type": "text", "text": subtitle},
                "image": {"type": "image", "asset_id": asset_id},
            },
        }

        return await self._request(
            method="POST",
            endpoint=endpoint,
            json_data=json_data,
        )

    async def get_autofill_status(self, job_id: str) -> Dict[str, Any]:
        """
        Gets the status of an autofill job.

        This corresponds to the 'Get Design ID' node in the n8n workflow.

        Args:
            job_id: The ID of the autofill job from `autofill_template`.

        Returns:
            A dictionary with the job status and the resulting design details.
        """
        logger.info(f"Getting status for autofill job: {job_id}")
        endpoint = f"/autofills/{job_id}"

        return await self._request(method="GET", endpoint=endpoint)

    async def export_design(
        self, design_id: str, format: str = "png"
    ) -> Dict[str, Any]:
        """
        Requests an export of a design.

        This corresponds to the 'Export Design' node in the n8n workflow.

        Args:
            design_id: The ID of the design to export.
            format: The desired export format (e.g., 'png', 'jpg').

        Returns:
            A dictionary containing the job details for the export task.
        """
        logger.info(f"Requesting export for design ID: {design_id}")
        endpoint = "/exports"
        json_data = {
            "design_id": design_id,
            "format": {"type": format},
        }

        return await self._request(
            method="POST",
            endpoint=endpoint,
            json_data=json_data,
        )

    async def get_export_status(self, job_id: str) -> Dict[str, Any]:
        """
        Gets the status of an export job.

        This corresponds to the 'Get Export' node in the n8n workflow.

        Args:
            job_id: The ID of the export job from `export_design`.

        Returns:
            A dictionary with the job status and download URLs upon completion.
        """
        logger.info(f"Getting status for export job: {job_id}")
        endpoint = f"/exports/{job_id}"

        return await self._request(method="GET", endpoint=endpoint)
