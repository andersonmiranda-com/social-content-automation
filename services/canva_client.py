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
from requests_oauthlib import OAuth2Session

from utils.config_loader import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Constants for OAuth
TOKEN_FILE = "canva_token.json"
AUTHORIZATION_URL = "https://www.canva.com/api/oauth/authorize"
TOKEN_URL = "https://api.canva.com/rest/v1/oauth/token"
SCOPES = [
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
CANVA_SCOPES_STRING = " ".join(sorted(list(set(SCOPES))))


class CanvaClient:
    """A client for interacting with the Canva API with automated OAuth handling."""

    def __init__(self, config_key: str = "canva"):
        self.config = load_config(config_key)
        self.client_id = self.config.get("client_id")
        self.client_secret = self.config.get("client_secret")
        self.base_url = "https://api.canva.com/rest/v1"
        self.redirect_uri = "http://127.0.0.1:8080/callback"

        if not self.client_id or not self.client_secret:
            raise ValueError("Canva client_id and client_secret must be configured.")

        logger.info(
            f"--- [DEBUG] Canva Client initialized with Client ID: {self.client_id[:5]}... ---"
        )
        self.session = self._get_credentials()

    def _get_credentials(self) -> OAuth2Session:
        token = None
        refresh_token = os.environ.get("CANVA_REFRESH_TOKEN")

        if refresh_token:
            logger.info(
                "Found CANVA_REFRESH_TOKEN. Building credentials from environment."
            )
            token = {
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "access_token": "will_be_refreshed",
                "expires_in": "-30",
            }
        elif os.path.exists(TOKEN_FILE):
            logger.info(f"Loading credentials from local file: {TOKEN_FILE}")
            with open(TOKEN_FILE, "r") as f:
                token = json.load(f)

        def token_saver(t: Dict[str, Any]):
            logger.info(f"Saving new/refreshed token to {TOKEN_FILE}")
            with open(TOKEN_FILE, "w") as f:
                json.dump(t, f)
            if "refresh_token" in t:
                logger.warning(
                    "A new refresh token was issued. Please update your CANVA_REFRESH_TOKEN environment variable."
                )
                logger.info(f"✅ New Canva Refresh Token: \n{t['refresh_token']}\n")

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
            redirect_uri=self.redirect_uri,
        )

        if not session.authorized:
            self._initiate_auth_flow()

        return session

    def _initiate_auth_flow(self):
        """Initiates the full browser-based OAuth2 authorization flow."""
        logger.info("Canva token not found or invalid. Starting authorization flow...")

        code_verifier = secrets.token_urlsafe(64)
        code_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode("utf-8")).digest()
            )
            .decode("utf-8")
            .rstrip("=")
        )
        state = secrets.token_urlsafe(16)

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": CANVA_SCOPES_STRING,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        auth_url = f"{AUTHORIZATION_URL}?{urlencode(params)}"

        print("✅ Please authorize this application with Canva:")
        print("   (Opening browser automatically...)")
        webbrowser.open(auth_url)

        auth_code = self._wait_for_auth_code(state)

        logger.info("Authorization code received. Fetching token manually...")
        token_payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code_verifier": code_verifier,
        }

        response = httpx.post(TOKEN_URL, data=token_payload)
        response.raise_for_status()
        token = response.json()

        self.session.token = token
        self.session.token_updater(token)
        logger.info("✅ Canva token fetched and saved successfully.")

    def _wait_for_auth_code(self, expected_state: str) -> str:
        # ... [omitted for brevity, this part is synchronous and correct]
        pass  # Placeholder for the synchronous _wait_for_auth_code logic
        return ""  # Added to satisfy linter

    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        content: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Makes an asynchronous, authenticated request to the Canva API."""
        if not self.session.authorized:
            logger.info("Token is expired, refreshing synchronously...")
            self.session.refresh_token(
                TOKEN_URL, client_id=self.client_id, client_secret=self.client_secret
            )

        auth_header = f"Bearer {self.session.token['access_token']}"
        final_headers = {"Authorization": auth_header, "Accept": "application/json"}
        if headers:
            final_headers.update(headers)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=f"{self.base_url}/{endpoint}",
                json=json_data,
                content=content,
                headers=final_headers,
            )
            response.raise_for_status()
            return {} if response.status_code == 204 else response.json()

    async def upload_asset(
        self, file_content: bytes, name_base64: str
    ) -> Dict[str, Any]:
        logger.info(f"Uploading asset with name (base64): {name_base64}")
        headers = {
            "Content-Type": "application/octet-stream",
            "Canva-Upload-File-Name": name_base64,
        }
        return await self._request(
            "POST", "/asset-uploads", content=file_content, headers=headers
        )

    async def get_asset_upload_status(self, job_id: str) -> Dict[str, Any]:
        logger.info(f"Getting status for asset upload job: {job_id}")
        return await self._request("GET", f"/asset-uploads/{job_id}")

    async def autofill_template(
        self, asset_id: str, title: str, subtitle: str
    ) -> Dict[str, Any]:
        logger.info(f"Autofilling template with asset: {asset_id}")
        template_id = self.config.get("template_id")
        if not template_id:
            raise ValueError("Canva template_id must be configured in canva.yaml")
        data = {
            "data": {
                "image": {"type": "ASSET", "ref": asset_id},
                "title": {"type": "TEXT", "text": title},
                "subtitle": {"type": "TEXT", "text": subtitle},
            }
        }
        return await self._request(
            "POST", f"/brand-templates/{template_id}/autofill", json_data=data
        )

    async def get_autofill_status(self, job_id: str) -> Dict[str, Any]:
        logger.info(f"Getting status for autofill job: {job_id}")
        return await self._request("GET", f"/brand-templates/autofill/{job_id}")

    async def export_design(
        self, design_id: str, format: str = "png"
    ) -> Dict[str, Any]:
        logger.info(f"Exporting design: {design_id}")
        data = {"design_id": design_id, "format": {"type": format}}
        return await self._request("POST", "/designs/export", json_data=data)

    async def get_export_status(self, job_id: str) -> Dict[str, Any]:
        logger.info(f"Getting status for export job: {job_id}")
        return await self._request("GET", f"/designs/export/{job_id}")


# The _wait_for_auth_code implementation is synchronous and remains unchanged.
# It's a bit of a hybrid model, but it's the most stable approach.
def _wait_for_auth_code_impl(self, expected_state: str) -> str:
    auth_data_holder = {}

    class OAuthCallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            received_state = query_params.get("state", [None])[0]
            if received_state != expected_state:
                auth_data_holder["error"] = "Invalid state parameter."
                self.send_response(400)
                self.wfile.write(b"<h1>Error: Invalid state.</h1>")
                return
            if "code" in query_params:
                auth_data_holder["code"] = query_params["code"][0]
                self.send_response(200)
                self.wfile.write(b"<h1>Success!</h1>")
            else:
                auth_data_holder["error"] = "No code found."
                self.send_response(400)
                self.wfile.write(b"<h1>Error: No code found.</h1>")

    server_address = ("", 8080)
    httpd = HTTPServer(server_address, OAuthCallbackHandler)
    httpd.handle_request()
    httpd.server_close()
    if "error" in auth_data_holder:
        raise RuntimeError(auth_data_holder["error"])
    return auth_data_holder["code"]


CanvaClient._wait_for_auth_code = _wait_for_auth_code_impl
