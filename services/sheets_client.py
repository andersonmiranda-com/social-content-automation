import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.config_loader import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GoogleSheetsClient:
    def __init__(self, config_key="google_sheets"):
        self.config = load_config(config_key)
        self.creds = self._get_credentials()

    def _get_credentials(self):
        creds = None
        token_file = self.config["token_file"]
        credentials_file = self.config["credentials_file"]
        scopes = self.config["scopes"]

        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_file):
                    logger.error(f"Missing credentials file: '{credentials_file}'")
                    print(
                        f"❌ Missing credentials file: '{credentials_file}'\n"
                        f"Please download it from your Google Cloud project and place it in the root directory."
                    )
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, scopes
                )
                creds = flow.run_local_server(port=0)

            with open(token_file, "w") as token:
                token.write(creds.to_json())
        return creds

    def read_sheet(self):
        if not self.creds:
            logger.error("Authentication failed. Cannot read from sheet.")
            return None

        try:
            service = build("sheets", "v4", credentials=self.creds)
            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(
                    spreadsheetId=self.config["spreadsheet_id"],
                    range=self.config["range_name"],
                )
                .execute()
            )
            values = result.get("values", [])

            if not values:
                logger.warning("No data found in the sheet.")
                return []

            # Assume the first row is the header, strip whitespace from each header
            header = [h.strip() for h in values[0]]
            data = [dict(zip(header, row)) for row in values[1:]]
            return data

        except HttpError as err:
            logger.error(f"An API error occurred: {err}")
            return None
