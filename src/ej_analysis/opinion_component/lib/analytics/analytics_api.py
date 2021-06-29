"""Hello Analytics Reporting API V4."""

import os
import argparse
import re
import httplib2
import datetime

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

CURR_DIR = os.path.dirname(os.path.realpath(__file__))
CLIENT_SECRETS_PATH = CURR_DIR + "/client_secrets.json"
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


def initialize_analyticsreporting():
    """Initializes the analyticsreporting service object.

    Returns:
      analytics an authorized analyticsreporting service object.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRETS_PATH, SCOPES)
    analytics = build("analyticsreporting", "v4", credentials=credentials)
    return analytics
