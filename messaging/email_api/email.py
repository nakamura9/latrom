import os 
import smtplib
import ssl
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import quopri
from email import encoders
import email
from messaging.models import Email, EmailAddress
import datetime
import parse

class EmailBaseClass():
    

    def send_plaintext_email(self, to, message):
        '''sends plain text email over tls.'''
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
                self.SMTP_SERVER, self.SMTP_PORT, context=context) as server:
            server.login(self.profile.email_address, self.profile.email_password)
            server.sendmail(self.profile.email_address, to, message)

    def send_html_email(self, subject, to, html_message):
        mime_message = MIMEMultipart('alternative')
        mime_message['Subject'] = subject
        mime_message['From'] = self.profile.email_address
        mime_message['To'] = to
        mime_message.attach(MIMEText(html_message, 'html'))
        self.send_plaintext_email(to, mime_message.as_string())

    def send_email_with_attachment(self,
                                   subject,
                                   to,
                                   message,
                                   attachment,
                                   html=False):
        mime_message = MIMEMultipart('alternative')
        mime_message['Subject'] = subject
        mime_message['From'] = self.profile.email_address
        mime_message['To'] = to
        if html:
            mime_message.attach(MIMEText(message, 'html'))
        else:
            mime_message.attach(MIMEText(message, 'plain'))

        # open as binary
        #with open(filename, 'rb') as attachment:

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())

        # encoded into ASCII string
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={attachment.name}',
        )

        mime_message.attach(part)
        self.send_plaintext_email(to, mime_message.as_string())

    def fetch_mailbox(self):
        self.configured = True
        mailbox = imaplib.IMAP4_SSL(self.IMAP_HOST, self.IMAP_PORT)
        mailbox.login(self.profile.email_address, self.profile.email_password)
        return mailbox

    def process_email(self,mail, id):
        typ, data = mail.fetch(id, '(RFC822)')
        raw = data[0][1]

        try:
            as_string = raw.decode('utf-8')
            print('decoded')
        except Exception as e:
            print('error encountered decoding message')
            print(e)
            return
        
        return as_string

    def save_email_to_local_database(self, 
                                    msg, 
                                    id,
                                    draft=False, 
                                    sent=False, 
                                    incoming=False):
        print("##raw email: ", msg)
        msg_string = ""
        html_string = ""

        if msg.is_multipart():
            
            #TODO separate text parts from html parts
            for part in msg.walk():
                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)
                print(payload)
                if isinstance(payload, bytes):
                        payload = payload.decode('utf-8')
                    
                if content_type  == 'text/plain':
                    print('string content')
                    msg_string += payload

                if content_type == 'text/html':
                    print('html content')
                    html_string += payload

        else:
            print('direct msg')
            payload = msg.get_payload(decode=True)
            if isinstance(payload, bytes):
                payload = payload.decode('utf-8')
            print(payload)
            msg_string = payload

        from email.parser import HeaderParser
        headers = dict(HeaderParser().parsestr(msg.as_string()).items())
        print("##headers: ", headers)

        
        if headers.get('Received'):
            date = parse.parse('{}; {:te}', headers['Received'])
        elif headers.get('Date'):
            date = parse.parse('{:te}', headers['Date'])
        else:
            date = datetime.date.today()
        

        sent_from = None
        sent_to = None
        if draft or sent:
            if draft:
                folder='draft'
            else:
                folder='sent'
            sent_from =  EmailAddress.objects.get(
                address=self.profile.email_address)
            if not headers.get('To', None):
                print('##missing to')
            sent_to = EmailAddress.get_address(headers.get('To', ''))
        elif incoming:# i.e. inbox
            folder='inbox'
            if headers.get('From'):
                try:
                    sender_string = parse.parse('{} <{}>', headers["From"])[1]
                except TypeError:
                    print('##cannot parse header')
                    sender_string = headers['From']
            else:
                print('##no from')
                sender_string = 'test@email.com'
            
            print(sender_string)
            
            sent_to = EmailAddress.objects.get(
                address=self.profile.email_address)
            sent_from = EmailAddress.get_address(sender_string)

        if isinstance(id, bytes):
            id = id.decode('utf-8')

        email_msg = Email.objects.create(
            created_timestamp=date,
            subject=headers.get('Subject', ''),
            owner=self.profile.user,
            sent_from=sent_from,
            body= html_string.strip() + msg_string,
            to=sent_to,
            server_id=id,
            folder=folder,
            sent= sent if not incoming else True
        )

        if headers.get('Cc'):
            for address in headers['Cc'].split(', '):
                addr = EmailAddress.get_address(address)
                email_msg.copy.add(addr)

        if headers.get('Bcc'):
            for address in headers['Bcc'].split(', '):
                addr = EmailAddress.get_address(address)
                email_msg.blind_copy.add(addr)


    def download_email_attachment(self, msg_string, path):
        #TODO save the file temporarily and then add it to the filefield in the 
        #attachment folder
        
        for part in msg_string.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            fileName = part.get_filename()
        if bool(fileName):
            filePath = os.path.join(path, fileName)
            if not os.path.isfile(filePath) :
                fp = open(filePath, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

class EmailSMTP(EmailBaseClass):
    EMAIL_CONFIG = {
        'gmail': {
            'inbox': 'Inbox',
            'sent': '"[Gmail]/Sent Mail"',
            'drafts': '"[Gmail]/Drafts"'
        }
    }

    def __init__(self, profile):
        self.profile = profile
        self.SMTP_PORT = self.profile.smtp_port
        self.SMTP_SERVER = self.profile.smtp_server
        self.IMAP_HOST = self.profile.pop_imap_host
        self.IMAP_PORT = self.profile.pop_port

        if 'gmail' in self.SMTP_SERVER:
            self.config = self.EMAIL_CONFIG['gmail']

        self.configured =False

    def fetch_inbox(self):
        # only store the latest 100 emails and the emails stored in the system.
        mail = self.fetch_mailbox()

        mail.select(self.config['inbox'])
        type, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        latest = self.profile.latest_inbox
        recent = len(mail_ids) - 5
        for id in mail_ids[-10:]:
            if isinstance(id, bytes):
                id = id.decode('utf-8')
            if id < latest:
                continue
                
            as_string = self.process_email(mail, id)
            print("##called")
            #returns email.Message object
            email_message = email.message_from_string(as_string)
            try:
                self.save_email_to_local_database(email_message, id, incoming=True)
            except UnicodeDecodeError:
                pass
    
    def fetch_sent(self):
        mail = self.fetch_mailbox()

        mail.select(self.config('sent'))
        type, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        latest = None
        recent = len(mail_ids) - 5
        for id in mail_ids[recent:]:
            typ, data = mail.fetch(id, '(RFC822)')
            raw = data[0][1]

            as_string = raw.decode('utf-8')
            #returns email.Message object
            email_message = email.message_from_string(as_string)
            self.save_email_to_local_database(email_message, sent=True)

    def fetch_drafts(self):
        mail = self.fetch_mailbox()

        mail.select(self.config['drafts'])
        type, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        latest = None
        recent = len(mail_ids) - 5
        for id in mail_ids[recent:]:
            typ, data = mail.fetch(id, '(RFC822)')
            raw = data[0][1]

            as_string = raw.decode('utf-8')
            #returns email.Message object
            email_message = email.message_from_string(as_string)
            self.save_email_to_local_database(email_message, draft=True)




if __name__ == "__main__":
    pass