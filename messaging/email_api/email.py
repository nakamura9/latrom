import os 
import smtplib
import ssl
import imaplib
from email.mime.text import MIMEText
from django.core.files import File

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import quopri
from email import encoders
import email
from messaging.models import Email, EmailAddress, UserProfile
import datetime
import parse
from email.parser import HeaderParser
import logging
from latrom.settings import MEDIA_ROOT


logger =logging.getLogger(__name__)


class EmailBaseClass():
    def send_plaintext_email(self, to, message):
        '''sends plain text email over tls.
        Args
        ======
        to - list of strings  email addresses
        message - plain text string 
        '''
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
                self.SMTP_SERVER, 
                self.SMTP_PORT, 
                context=context) as server:
            server.login(
                    self.profile.email_address, 
                    self.profile.email_password)
            try:
                resp = server.sendmail(self.profile.email_address, to, message)
            except smtplib.SMTPException:
                logger.error(f'Email to {to.split(", ")} not sent')
            else:
                if len(resp) == 0:
                    pass
                else:
                    logger.error(f'Email to {", ".join(resp.keys())} not sent')

            finally:
                server.quit()

    def send_html_email(self, 
                        subject, 
                        to, cc, bcc, 
                        html_message, 
                        hook=None, 
                        **hook_kwargs):
        '''Used to send multipart emails with HTML content.
            calls the send plaintext email method to actually send emails
            applies headers and adds an html part to the message.
            Args
            =======
            subject - string describes message
            to - string, email address of recepient
            cc - list of strings, carbon copy of message
            bcc - list of strings, blind carbon copy
            hook - func - used to attach additional mime parts
            hook_kwargs - variable length kwargs passed on to hook function '''

        mime_message = MIMEMultipart('alternative')
        mime_message['Subject'] = subject
        mime_message['From'] = self.profile.email_address
        mime_message['To'] = to
        mime_message['Cc'] = ','.join(cc)
        mime_message.attach(MIMEText(html_message, 'html'))
        

        if hook:
            parts = hook(**hook_kwargs)
            for part in parts:
                mime_message.attach(part)

        self.send_plaintext_email([to] + cc + bcc, mime_message.as_string())

    def send_email_with_attachment(self,
                                   subject,
                                   to, cc, bcc,
                                   message,
                                   attachment,
                                   html=False):

        def add_attachment_hook(a=None):
            '''Used to add files to emails. returns a one element list
            with the mime-part of the encoded attachment'''
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(a.read())

            # encoded into ASCII string
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={a.name}',
            )
            return [part]

        self.send_html_email(subject, 
                            to, cc, bcc, 
                            message, 
                            hook=add_attachment_hook,
                            a=attachment)

    def fetch_mailbox(self):
        '''Used to retrueve an instance of the mailbox'''
        self.configured = True
        mailbox = imaplib.IMAP4_SSL(self.IMAP_HOST, self.IMAP_PORT)
        mailbox.login(self.profile.email_address, self.profile.get_plaintext_password)
        return mailbox

    def process_email(self, mail, id):
        '''Used to retrieve a complete email from the server, and decode it in UTF-8. Logs any errors. 

        Args
        ==========
        mail -  object mailbox
        id - string -represents the index of the email in the folder.

        Returns
        ==========
        the decoded string
        '''

        typ, data = mail.fetch(id, '(RFC822)')
        raw = data[0][1]

        try:
            as_string = raw.decode('utf-8', errors="ignore")
        except Exception as e:
            logger.error(
                f'Error encountered decoding message {id} with error {e}')
            return
        
        return as_string

    def save_email_to_local_database(self, 
                                    msg, 
                                    id,
                                    draft=False, 
                                    sent=False, 
                                    incoming=False):
        '''Iterates over the message parts and combines the text sections together while decoding them as well.'''

        msg_string = ""
        html_string = ""
        file= None

        #multipart vs singular message
        charset = msg.get_content_charset()
        charset = charset if charset else 'utf-8'
        if msg.is_multipart():
            
            for part in msg.walk():
                content_type = part.get_content_type()
                try:
                    payload = part.get_payload(decode=True) 
                except:
                    payload = part.get_payload()

                if payload and isinstance(payload, bytes):
                        payload = payload.decode(charset, errors="ignore")
                    
                if content_type  == 'text/plain':
                    msg_string += payload

                if content_type == 'text/html':
                    html_string += payload

            file, file_name = self.download_email_attachment(msg, 
                                           os.path.join(MEDIA_ROOT, 'temp'))
            if file:
                file_rb = open(file, 'rb')
                django_file = File(file_rb,
                        os.path.join('messaging', file_name))
                
        else:
            payload = msg.get_payload(decode=True)
            if payload and isinstance(payload, bytes):
                payload = payload.decode(charset, errors="ignore")
            msg_string = payload

        headers = dict(HeaderParser().parsestr(msg.as_string()).items())
        print(headers)
        
        if headers.get('Received'):
            date = parse.parse('{}; {:te}', headers['Received'])
        elif headers.get('Date'):
            date = parse.parse('{:te}', headers['Date'])
        else:
            print('wrong date')
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
            
            
            sent_to = EmailAddress.objects.get(
                address=self.profile.email_address)
            sent_from = EmailAddress.get_address(sender_string)

        if isinstance(id, bytes):
            id = id.decode('utf-8')
        subject = headers.get('Subject', '')
        
        if subject and isinstance(subject, bytes):
            subject.decode('utf-8', errors="ignore")

        email_msg = Email.objects.create(
            created_timestamp=date,
            subject=subject,
            owner=self.profile.user,
            sent_from=sent_from,
            body= html_string.strip() + msg_string,
            to=sent_to,
            server_id=id,
            folder=folder,
            sent= sent if not incoming else True,
        )
        if file:
            try:
                email_msg.attachment.save(file_name, django_file)
            except Exception as e:
                print(f'file related exception {e}')

            file_rb.close()
            os.remove(file)

        if headers.get('Cc'):
            for address in headers['Cc'].split(', '):
                addr = EmailAddress.get_address(address)
                email_msg.copy.add(addr)

        if headers.get('Bcc'):
            for address in headers['Bcc'].split(', '):
                addr = EmailAddress.get_address(address)
                email_msg.blind_copy.add(addr)

        email_msg.save()

    def download_email_attachment(self, msg_string, path):
        #TODO save the file temporarily and then add it to the filefield in the 
        #attachment folder
        fileName =None
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
                payload = part.get_payload(decode=True) 
                if payload:
                    fp.write(payload)
                    fp.close()

            return filePath, fileName
        return (None, fileName)

    def fetch_messages(self, 
                        mail,
                        mail_ids,
                        latest, 
                        incoming=False, 
                        sent=False,
                        draft=False):
        skipped = 0
        errors = 0
        queryset = self.profile.emails
        

        for id in mail_ids:
            if isinstance(id, bytes):
                id = id.decode('utf-8')
            
            folder = None
            if incoming:
                folder = 'inbox'
            elif sent:
                folder='sent'
            else:
                folder='drafts'
                
            if queryset.filter(server_id=id, folder=folder).exists():
                print(f'Email skipped: {id}')
                continue

            as_string = self.process_email(mail, id)
            
            #returns email.Message object
            
            email_message = email.message_from_string(as_string)
            try:
                self.save_email_to_local_database(
                    email_message, 
                    id, 
                    incoming=incoming,
                    sent=sent,
                    draft=draft)

            except UnicodeDecodeError:
                errors += 1
                logger.error(f'Failed to decode email {id}')
            except Exception as e:
                errors += 1
                logger.error(f'An unexpected error occurred: {e}')

        logger.warn(f'{skipped} emails skipped')
        logger.warn(f'{errors} errors handled')

    def fetch_inbox(self):
        mail = self.fetch_mailbox()

        mail.select(self.config['inbox'])
        type, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        latest = self.profile.latest_inbox
        self.fetch_messages(mail, mail_ids, latest, incoming=True)
        

    def fetch_sent(self):
        mail = self.fetch_mailbox()

        mail.select(self.config['sent'])
        type, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        latest = self.profile.latest_sent
        self.fetch_messages(mail, mail_ids, latest, sent=True)
        

    def fetch_drafts(self):
        mail = self.fetch_mailbox()

        mail.select(self.config['drafts'])
        type, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        latest = self.profile.latest_drafts
        self.fetch_messages(mail, mail_ids, latest,draft=True)

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


if __name__ == "__main__":
    profile = UserProfile.objects.first()
    client = EmailSMTP(profile)
    client.fetch_inbox()
    client.fetch_drafts()
    client.fetch_sent()