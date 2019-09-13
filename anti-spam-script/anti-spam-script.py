#!/usr/bin/python
# -*- encoding: utf-8 -*-
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
    # do your stuff
    app.enter(interval, 1, do_something, (sc,))
    mail = imaplib.IMAP4_SSL('server72.hosting2go.nl', 993)
    result = mail.login(imap_userid, imap_password)
    print(result)
    # ('OK', [b'LOGIN Ok.'])
    stat, cnt = mail.select('INBOX')
    print(cnt)

    messages = []

    mbox_response, msgnums = mail.search('INBOX')
    print(mbox_response)
    if mbox_response == 'OK':
        for num in msgnums[0].split():
            retval, rawmsg = mail.fetch(num, '(RFC822)')
            if retval != 'OK':
                print('ERROR getting message', num)
                continue
            msg = email.message_from_bytes(rawmsg[0][1])
            msg_subject = msg["Subject"]
            print(msg_subject)
            if subject in msg_subject:
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        type = part.get_content_type()
                        disp = str(part.get('Content-Disposition'))
                        # look for plain text parts, but skip attachments
                        if type == 'text/plain' and 'attachment' not in disp:
                            charset = part.get_content_charset()
                            # decode the base64 unicode bytestring into plain text
                            body = part.get_payload(decode=True).decode(encoding=charset, errors="ignore")
                            # if we've found the plain/text part, stop looping thru the parts
                            break
                else:
                    # not multipart - i.e. plain text, no attachments
                    charset = msg.get_content_charset()
                    body = msg.get_payload(decode=True).decode(encoding=charset, errors="ignore")
                messages.append({'num': num, 'body': body})


    mail.close()
    mail.logout()

    # # ('OK', [b'48'])
    # mail_type, mail_data = mail.search(None, 'ALL')
    # mail_ids = mail_data[0]
    # id_list = mail_ids.split()
    #
    # for num in mail_data[0].split():
    #     typ, data = mail.fetch(num, '(RFC822)')
    #     raw_email = data[0][1]
    #     # converts byte literal to string removing b''
    #     raw_email_string = raw_email.decode('utf-8')
    #     email_message = email.message_from_string(raw_email_string)
    #     for part in email_message.walk():
    #         print(part)


s = None
app = sched.scheduler(time.time, time.sleep)
do_something(s)


def login(self):
    try:
        rv, data = self.mail.login(imap_userid, imap_password)
    except (imaplib.IMAP4_SSL.error, imaplib.IMAP4.error) as err:
        print('LOGIN FAILED!')
        print(err)
        sys.exit(1)


def logout(self):
    self.imap.close()
    self.imap.logout()



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



