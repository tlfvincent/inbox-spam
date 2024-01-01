import base64
import logging
import re
import requests

from urlextract import URLExtract
from tqdm import tqdm


class NewsletterCollector(object):
    """
    Extract all valid URLs found in newsletters

    Parameters
    ----------
    service : googleapiclient.discovery.Resource
        A valid Google API client connection
    start_date : string
        Start date from which to collect email data
    end_date : string
        End date from which to collect email data
    """
    def __init__(
        self,
        service,
        start_date,
        end_date
    ):

        self._service = service
        self.start_date = start_date
        self.end_date = end_date

    def collect_email_data(self):

        all_emails = []  # To store data from all pages
        next_page_token = None

        while True:
            print(next_page_token)
            response = self.make_api_request(page_token=next_page_token)
            
            # Extract data from the current page
            current_page_data = response.get("messages", [])  # Replace 'data' with the key containing the actual data
            
            # Append data from the current page to the all_data list
            all_emails.extend(current_page_data)
            
            # Check if there's a nextPageToken in the response
            next_page_token = response.get("nextPageToken")
            
            # If there is no nextPageToken, break the loop
            if not next_page_token:
                break

        return all_emails
    
    def extract_email_metadata(self, all_emails):

        sender_metadata = {}

        for email in tqdm(all_emails):
            email_id = email["id"]
            email_sender, email_address, email_send_date, email_size = self.get_message_metadata(email_id)
            sender_metadata["message_id"] = [email_sender, email_address, email_send_date, email_size]

        return sender_metadata
    
    def make_api_request(self, page_token=None):
        """
        Extract all emails sent by input email address

        Parameters
        ------
        page_token : string
            A token for the specific page to read from

        Returns
        -------
        unread_msgs : dict-like
            contains message ids corresponding to emails
            sent by input email address

        Notes
        -----
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list
        """
        logging.info(f"Getting all unread messages sent between {self.start_date} and {self.end_date}")

        unread_msgs = (
            self._service
            .users()
            .messages()
            .list(
                userId="me",
                labelIds=["INBOX"],
                maxResults=500,
                pageToken=page_token,
                q=f"after:{self.start_date} before:{self.end_date}"
            )
            .execute()
        )

        return unread_msgs
        
    def get_message_metadata(self, message_id):
        """
        Extract all message ids

        Parameters
        ----------
        message_id : string
            message id

        Returns
        -------
        email_sender : string
            list of message ids
        email_address : string
        """

        # extract medatata associated to message ID
        msg_metadata = (
            self._service
            .users()
            .messages()
            .get(
                userId='me',
                id=f'{message_id}',
                format='full'
            )
            .execute()
        )

        if msg_metadata is None:

            return [None]*4

        # extract email size
        email_size = msg_metadata["sizeEstimate"]

        # extract send date of message
        email_send_date = msg_metadata["internalDate"]

        # extract metadata on sender
        sender_metadata = [data["value"] for data in msg_metadata["payload"]["headers"] if data["name"] == "From"]
        
        if len(sender_metadata) > 0:
            sender = sender_metadata[0]

            # Regular expression pattern to extract text outside < and > symbols
            pattern = r'([^<]+)\s*<([^>]+)>'

            # Using re.search to extract text outside < and > symbols
            match = re.search(pattern, sender)

            if match:
                email_sender = match.group(1).strip()
                email_address = match.group(2)
                
            else:
                email_sender, email_address = None, None

        else:
            email_sender, email_address = None, None

        return email_sender, email_address, email_send_date, email_size