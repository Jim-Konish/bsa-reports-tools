import argparse
from email_handling.send_email import send_email
from login.get_login import get_email_login

(sender, password) = get_email_login()

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--recipient", required=True, help="Test recipient email address")
args = parser.parse_args()
test_recipient = args.recipient

send_email(subject='test', body='The email, the email, what what the email', sender=sender, recipients=[test_recipient], password=password)
