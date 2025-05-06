"""
VolleyStat Lite - Google Sheets Adapter
This module implements the adapter for Google Sheets API interactions.
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from adapters.adapter_base import ThirdPartyAdapter

class GoogleSheetsAdapter(ThirdPartyAdapter):
    """Adapter for Google Sheets API."""
    def __init__(self, credentials_file, scopes=None):
        self.credentials_file = credentials_file
        self.scopes = scopes or ['https://www.googleapis.com/auth/spreadsheets']
        self.service = None
    
    def connect(self):
        """Connect to Google Sheets API."""
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=self.scopes
            )
            self.service = build('sheets', 'v4', credentials=creds)
            return True
        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
            return False
    
    def read_data(self, spreadsheet_id, range_name="Sheet1!A1:Z1000"):
        """Read data from a Google Sheet."""
        if not self.service:
            if not self.connect():
                return None
                
        try:
            sheet = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            return sheet.get('values', [])
        except Exception as e:
            print(f"Error reading from Google Sheets: {e}")
            return None
    
    def write_data(self, spreadsheet_id, range_name, data):
        """Write data to a Google Sheet."""
        if not self.service:
            if not self.connect():
                return False
                
        try:
            # Convert any date objects to strings before sending to API
            processed_data = []
            for row in data:
                processed_row = []
                for item in row:
                    # Check if the item is a date or datetime object
                    if hasattr(item, 'strftime'):
                        processed_row.append(item.strftime('%Y-%m-%d'))
                    else:
                        processed_row.append(item)
                processed_data.append(processed_row)
            
            body = {
                'values': processed_data
            }
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            return result.get('updatedCells', 0) > 0
        except Exception as e:
            print(f"Error writing to Google Sheets: {e}")
            return False