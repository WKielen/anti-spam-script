#!/usr/bin/python
# -*- encoding: utf-8 -*-
from ImapClient import ImapClient
import sched
import time
import yaml
import imaplib
import sys
import base64
import email


with open("..\\config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)
    imap_param = cfg['imap']
    imap_userid = imap_param['userid']
    imap_password = imap_param['password']
    misc_param = cfg['misc']
    interval = int(misc_param['interval'])



def do_something(sc):
    print ("Doing stuff...")
    imap = ImapClient(recipient='secretaris@ttvn.nl')
    imap.login();
    messages = imap.get_messages(sender='noreply@sendcloud.sc')
    # Do something with the messages
    print("Messages in my inbox:")
    for msg in messages:
        # msg is a dict of {'num': num, 'body': body}
        print(msg['num'])
        # you could delete them after viewing
        # imap.delete_message(msg['num'])
    # when done, yo
    imap.delete_message()
    # do your stuff
    app.enter(interval, 1, do_something, (sc,))

s = None
app = sched.scheduler(time.time, time.sleep)
do_something(s)

def main():
    app.run()
# Net de applicatie gestart. Hieronder wordt de main thread levend gehouden.
    while True:
        time.sleep(30)


if __name__ == '__main__':
    main()


# def send_mail():
#     data = request.get_json()
#     email_user = data['UserId']
#     email_password = data['Password']
#
#     try:
#         with smtplib.SMTP('server72.hosting2go.nl', 2525) as smtp:
#             smtp.starttls()
#             smtp.login(email_user, email_password)
#
#             for mailItem in data['MailItems']:
#
#                 msg = MIMEMultipart()
#                 msg['From'] = mailItem['From']
#                 msg['To'] = mailItem['To']
#                 msg['CC'] = mailItem['CC']
#                 msg['BCC'] = mailItem['BCC']
#                 msg['Subject'] = mailItem['Subject']
#
#                 body = ''
#                 for line in mailItem['Message']:
#                     body += line + '\n'
#
#                 to_addresses = [mailItem['To']] + [mailItem['CC']] + [mailItem['BCC']]
#
#                 msg.attach(MIMEText(body, 'plain'))
#                 smtp.sendmail(mailItem['From'], to_addresses, msg.as_string())
#                 time.sleep(1)
#             smtp.quit()
#
#     except smtplib.SMTPRecipientsRefused:
#         return 'Mail Error. All recipients were refused. Nobody got the mail.', 200
#     except smtplib.SMTPHeloError:
#         return 'Mail Error. The server did not reply properly to the HELO greeting.', 200
#     except smtplib.SMTPSenderRefused as exc:
#         return 'Mail Error. The server did not accept the from_address.', 200
#     except smtplib.SMTPDataError as exc:
#         return 'Mail Error. The server replied with an unexpected error code (other than a refusal of a recipient).', 200
#     except smtplib.SMTPNotSupportedError as exc:
#         return 'Mail Error. SMTPUTF8 was given in the mail_options but is not supported by the server.', 200
#     except Exception as exc:
#         return 'Mail Error. Something went wrong. ', 200
#     return 'Success', 200



