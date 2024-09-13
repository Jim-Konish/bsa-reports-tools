import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, sender, recipients, password):
    # Create a MIMEText object with the body of the email.
    msg = MIMEText(body)
    # Set the subject of the email.
    msg['Subject'] = subject
    # Set the sender's email.
    msg['From'] = sender
    # Join the list of recipients into a single string separated by commas.
    msg['To'] = ', '.join(recipients)
   
    # Connect to Gmail's SMTP server using SSL.
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        # Login to the SMTP server using the sender's credentials.
        smtp_server.login(sender, password)
        # Send the email. The sendmail function requires the sender's email, the list of recipients, and the email message as a string.
        smtp_server.sendmail(sender, recipients, msg.as_string())
    # Print a message to console after successfully sending the email.
    print("Message sent!")


if(__name__ == '__main__'):
    # Define the subject and body of the email.
    subject = "Email Subject"
    body = "This is the body of the text message"
    # Define the sender's email address.
    sender = "@gmail.com"
    # List of recipients to whom the email will be sent.
    recipients = ["recipient1@gmail.com", "recipient2@gmail.com"]
    # Password for the sender's email account.
    password = "password"

    # Call the function to send the email.
    send_email(subject, body, sender, recipients, password)