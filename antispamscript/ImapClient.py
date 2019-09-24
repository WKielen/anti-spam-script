import email
import email.header
import imaplib
import sys
# inspiratie opgedaan: https://www.timpoulsen.com/2018/reading-email-with-python.html

class ImapClient:
    imap = None

    def __init__(self,
                 recipient,
                 password,
                 server,
                 use_ssl=False,
                 move_to_trash=False):
        # check for required param
        if not recipient:
            raise ValueError('You must provide a recipient email address')
        self.recipient = recipient
        self.password = password
        self.use_ssl = use_ssl
        self.move_to_trash = move_to_trash
        self.recipient_folder = 'INBOX'
        # instantiate our IMAP client object
        if self.use_ssl:
            self.imap = imaplib.IMAP4_SSL(server)
        else:
            self.imap = imaplib.IMAP4(server)

    def login(self):
        try:
            rv, data = self.imap.login(self.recipient, self.password)
            # print(self.imap.list())
        except (imaplib.IMAP4_SSL.error, imaplib.IMAP4.error) as err:
            print('LOGIN FAILED!')
            print(err)
            # sys.exit(1)

    def logout(self):
        self.imap.close()
        self.imap.logout()

    def select_folder(self, folder):
        """
        Select the IMAP folder to read messages from. By default
        the class will read from the INBOX folder
        """
        self.recipient_folder = folder

    def get_messages(self):

        try:
            # select the folder, by default INBOX
            resp, _ = self.imap.select(self.recipient_folder)
            if resp != 'OK':
                print(f"ERROR: Unable to open the {self.recipient_folder} folder")
                sys.exit(1)

            messages = []

            mbox_response, msgnums = self.imap.search(None, 'ALL')
            if mbox_response == 'OK':
                for num in msgnums[0].split():
                    # We hebben een lijst van bericht nummers. We gaan ze per stuk ophalen
                    retval, rawmsg = self.imap.fetch(num, '(RFC822)')
                    if retval != 'OK':
                        print('ERROR getting message', num)
                        continue
                    msg = email.message_from_bytes(rawmsg[0][1])
                    msg_subject = decode_mime_words(msg["Subject"])
                    msg_to = msg["To"]
                    msg_from = msg["From"]
                    msg_id = msg['Message-ID']
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
                    messages.append({'num': num, 'msgid': msg_id, 'to': msg_to, 'from': msg_from, 'subject': msg_subject, 'body': body})
            return messages
        except Exception as err:
            print('Get Messages Failed!')
            print(err)

    def delete_message(self, msg_id):
        try:
            if not msg_id:
                return
            if self.move_to_trash:
                # move to Trash folder
                self.imap.store(msg_id, '+X-GM-LABELS', '\\Trash')
                self.imap.expunge()
            else:
                self.imap.store(msg_id, '+FLAGS', '\\Deleted')
                # print(self.imap.expunge())
        except Exception as err:
            print('Delete messages Failed!')
            print(err)


def decode_mime_words(s):
    return u''.join(
        word.decode(encoding or 'utf8') if isinstance(word, bytes) else word
        for word, encoding in email.header.decode_header(s))