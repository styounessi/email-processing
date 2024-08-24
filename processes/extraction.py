import os
import email
import imaplib
import datetime
import polars as pl


# Pull Gmail IMAP server & credentials via environment variables
GMAIL_IMAP_SERVER = os.getenv('GMAIL_IMAP_SERVER')
GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')


# Current date, for appending to parquet filename
timestamp = datetime.datetime.now().strftime('%Y%m%d')


def connect_and_login(username, password):
    '''
    Connects to Gmail mail server using given credentials.
    '''
    mail_host = imaplib.IMAP4_SSL(GMAIL_IMAP_SERVER)
    mail_host.login(username, password)
    return mail_host


def get_unread_ids(mail_host):
    '''
    Fetches unread email IDs from within the inbox.
    '''
    mail_host.select('inbox')
    _, unread = mail_host.search(None, 'UNSEEN')
    unread_email_ids = unread[0].split()
    return unread_email_ids


def fetch_email_content(mail_host, email_id):
    '''
    Fetches the content of the emails from within the inbox for each email ID.
    '''
    _, data = mail_host.fetch(email_id, '(RFC822)')
    raw_email = data[0][1]
    return email.message_from_bytes(raw_email)


def parse_email(email_message):
    '''
    Parses for relevant information being sought from each email.
    '''
    sender = email_message['From']
    subject = email_message['Subject']
    date_sent = email_message['Date']
    email_body = ''
    
    for part in email_message.walk():
        if part.get_content_type() == 'text/plain':
            email_body = part.get_payload(decode=True).decode('utf-8').replace('\n\n', ' ')
            break
    
    return {
        'from': sender,
        'subject': subject,
        'body': email_body,
        'date': date_sent
    }


def process_unread_emails():
    '''
    Connects to inbox and gathers unread emails, converts contents
    of email(s) into a LazyFrame and saves as a parquet file.
    '''
    mailbox = connect_and_login(GMAIL_ADDRESS, GMAIL_PASSWORD)
    unread_email_ids = get_unread_ids(mailbox)
    
    # Exits if there are no new unread emails
    if not unread_email_ids:
        print('No new unread emails to process.')
        mailbox.close()
        exit()

    data = []
    
    for email_id in unread_email_ids:
        email_data = fetch_email_content(mailbox, email_id)
        extracted_data = parse_email(email_data)
        data.append(extracted_data)

    # Converts to Polars LazyFrame and writes to parquet
    lf = pl.LazyFrame(data)
    lf.sink_parquet(f'/opt/airflow/parquet/raw_files/emails_{timestamp}.parquet')
    
    print('Unread emails processed and saved successfully.')
    
    mailbox.close()


if __name__ == '__main__':
    process_unread_emails()
