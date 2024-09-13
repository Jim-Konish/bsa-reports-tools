from email_handling.send_email import send_email
from login.get_login import get_email_login

(sender, password) = get_email_login()

send_email(subject='test', body='The email, the email, what what the email', sender=sender, recipients=['Jim Konish <jim.konish@sphero.com'], password=password)
