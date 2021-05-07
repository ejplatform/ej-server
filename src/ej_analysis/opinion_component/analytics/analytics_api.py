"""Hello Analytics Reporting API V4."""

import os
import argparse
import re
import httplib2
import datetime

from apiclient.discovery import build
from oauth2client import client
from oauth2client import file
from oauth2client import tools
CURR_DIR = os.path.dirname(os.path.realpath(__file__))
CLIENT_SECRETS_PATH = CURR_DIR + '/client_secrets.json'
ANALYTICS_REPORTING_PATH = CURR_DIR + '/analyticsreporting.dat'
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

def initialize_analyticsreporting():
    """Initializes the analyticsreporting service object.

    Returns:
      analytics an authorized analyticsreporting service object.
    """
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser])
    flags = parser.parse_args([])

    # Set up a Flow object to be used if we need to authenticate.
    flow = client.flow_from_clientsecrets(
        CLIENT_SECRETS_PATH, scope=SCOPES,
        message=tools.message_if_missing(CLIENT_SECRETS_PATH))

    # Prepare credentials, and authorize HTTP object with them.
    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to a file.
    storage = file.Storage(ANALYTICS_REPORTING_PATH)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=httplib2.Http())

    # Build the service object.
    analytics = build('analyticsreporting', 'v4',
                      http=http, cache_discovery=False)

    return analytics
