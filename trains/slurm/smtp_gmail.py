import smtplib, ssl
import json, os, subprocess
from email.message import EmailMessage

port = 465

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(THIS_DIR, 'gmail-credentials.json'), 'r') as f:
    credentials = json.load(f)
sender_email = credentials['sender_email']
sender_password = credentials['sender_password']
receiver_email = credentials['receiver_email']

context = ssl.create_default_context()

def send_finish_email():
    message = '''\
Hi Dear Furkan,

Mailing from cmpeinspurgpu. No more jobs to run! 🎉

Best,
Furkan
    '''
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = 'No more jobs to run on cmpeinspurgpu!'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)