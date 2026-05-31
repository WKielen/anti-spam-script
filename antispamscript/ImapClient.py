import email
import email.header
import imaplib
import logging

logger = logging.getLogger(__name__)


class ImapClient:
    def __init__(self, recipient, password, server, portnumber=993, use_ssl=True, move_to_trash=False):
        if not recipient:
            raise ValueError('recipient email address is required')
        self.recipient = recipient
        self.password = password
        self.use_ssl = use_ssl
        self.move_to_trash = move_to_trash
        self.recipient_folder = 'INBOX'
        if self.use_ssl:
            self.imap = imaplib.IMAP4_SSL(server, port=portnumber)
        else:
            self.imap = imaplib.IMAP4(server, port=portnumber)

    def login(self):
        self.imap.login(self.recipient, self.password)

    def logout(self):
        # CLOSE issues an implicit EXPUNGE for messages flagged \Deleted
        self.imap.close()
        self.imap.logout()

    def select_folder(self, folder):
        self.recipient_folder = folder

    def get_messages(self):
        resp, _ = self.imap.select(self.recipient_folder)
        if resp != 'OK':
            raise RuntimeError(f'Unable to open folder {self.recipient_folder}')

        messages = []
        status, msgnums = self.imap.search(None, 'ALL')
        if status != 'OK' or not msgnums[0]:
            return messages

        for num in msgnums[0].split():
            retval, rawmsg = self.imap.fetch(num, '(RFC822)')
            if retval != 'OK':
                logger.warning('Error fetching message %s', num)
                continue
            try:
                msg = email.message_from_bytes(rawmsg[0][1])
                messages.append({
                    'num':     num,
                    'msgid':   msg.get('Message-ID', ''),
                    'to':      msg.get('To', ''),
                    'from':    msg.get('From', ''),
                    'subject': _decode_header(msg.get('Subject', '')),
                    'date':    msg.get('Date', ''),
                    'body':    _extract_body(msg),
                })
            except Exception:
                logger.exception('Error parsing message %s', num)

        return messages

    def mark_deleted(self, msg_num):
        """Flag a message \Deleted. Actual removal happens on logout (CLOSE)."""
        if not msg_num:
            return
        if self.move_to_trash:
            self.imap.store(msg_num, '+X-GM-LABELS', '\\Trash')
        else:
            self.imap.store(msg_num, '+FLAGS', '\\Deleted')


# ── helpers ────────────────────────────────────────────────────────────────────

def _decode_header(value):
    """Decode a MIME-encoded email header to a plain Unicode string."""
    if not value:
        return ''
    try:
        parts = []
        for word, enc in email.header.decode_header(value):
            if isinstance(word, bytes):
                parts.append(word.decode(enc or 'utf-8', errors='replace'))
            else:
                parts.append(word)
        return ''.join(parts)
    except Exception:
        return str(value)


def _extract_body(msg):
    """Return the plain-text body of an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            if (part.get_content_type() == 'text/plain'
                    and 'attachment' not in str(part.get('Content-Disposition', ''))):
                charset = part.get_content_charset() or 'utf-8'
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(charset, errors='replace')
    else:
        charset = msg.get_content_charset() or 'utf-8'
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(charset, errors='replace')
    return ''
