import json
import os.path
from typing import Any

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
                    logger.error(
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

    def read_sheet(self, range_name: str | None = None):
        if not self.creds:
            logger.error("Authentication failed. Cannot read from sheet.")
            return None

        try:
            service = build("sheets", "v4", credentials=self.creds)
            sheet = service.spreadsheets()

            current_range = range_name if range_name else self.config["range_name"]

            result = (
                sheet.values()
                .get(
                    spreadsheetId=self.config["spreadsheet_id"],
                    range=current_range,
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

    def upsert_row(
        self,
        filter_key: str,
        filter_value: str,
        row_data: dict,
        range_name: str | None = None,
    ):
        """
        Updates a row if a matching filter_value is found in the filter_key column.
        Otherwise, appends a new row with the provided data.
        """
        if not self.creds:
            logger.error("Authentication failed. Cannot upsert row.")
            return None

        try:
            service = build("sheets", "v4", credentials=self.creds)
            sheet_values = service.spreadsheets().values()

            current_range = range_name if range_name else self.config["range_name"]
            sheet_name = current_range.split("!")[0]

            # Read the sheet to find the row and get headers
            read_result = sheet_values.get(
                spreadsheetId=self.config["spreadsheet_id"],
                range=sheet_name,  # Read the whole sheet
            ).execute()
            values = read_result.get("values", [])

            if not values:
                logger.warning("Sheet is empty. Will append a new row.")
                header = list(row_data.keys())
                new_row_values = list(row_data.values())
                body = {"values": [header, new_row_values]}
                return sheet_values.update(
                    spreadsheetId=self.config["spreadsheet_id"],
                    range=f"{sheet_name}!A1",
                    valueInputOption="USER_ENTERED",
                    body=body,
                ).execute()

            header = [h.strip() for h in values[0]]
            try:
                filter_col_index = header.index(filter_key)
            except ValueError:
                logger.error(f"Filter key '{filter_key}' not found in header: {header}")
                return None

            row_number_to_update = -1
            for i, row in enumerate(values[1:], start=2):
                if len(row) > filter_col_index and str(row[filter_col_index]) == str(
                    filter_value
                ):
                    row_number_to_update = i
                    break

            if row_number_to_update != -1:
                # --- UPDATE PATH ---
                data_to_update = []
                for col_name, value in row_data.items():
                    if col_name in header:
                        col_index = header.index(col_name)
                        col_letter = chr(ord("A") + col_index)
                        range_spec = f"{sheet_name}!{col_letter}{row_number_to_update}"
                        data_to_update.append(
                            {"range": range_spec, "values": [[value]]}
                        )

                if not data_to_update:
                    logger.warning("No valid columns to update found in sheet header.")
                    return {"status": "no_op", "reason": "No valid columns to update"}

                body = {"valueInputOption": "USER_ENTERED", "data": data_to_update}
                result = sheet_values.batchUpdate(
                    spreadsheetId=self.config["spreadsheet_id"], body=body
                ).execute()
                logger.info(
                    f"Successfully updated {len(data_to_update)} cells in row {row_number_to_update}."
                )
                return result
            else:
                # --- INSERT PATH ---
                new_row: list[Any] = [None] * len(header)
                # Place filter value in its column
                new_row[filter_col_index] = filter_value
                for col_name, value in row_data.items():
                    if col_name in header:
                        col_index = header.index(col_name)
                        new_row[col_index] = value

                body = {"values": [new_row]}
                result = sheet_values.append(
                    spreadsheetId=self.config["spreadsheet_id"],
                    range=sheet_name,
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body=body,
                ).execute()
                logger.info(
                    f"Appended a new row as '{filter_key}={filter_value}' was not found."
                )
                return result

        except HttpError as err:
            logger.error(f"An API error occurred during upsert: {err}")
            return None
