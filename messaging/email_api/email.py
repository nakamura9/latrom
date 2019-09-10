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
import mailparser

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
                    self.profile.get_plaintext_password)
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

        def add_attachment_hook(a=None):#meta
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
        '''Used to retrieve an instance of the mailbox'''
        return self.profile.login_incoming()

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
                                    folder):
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
        better_headers = mailparser.parse_from_string(msg.as_string())
        
        to = EmailAddress.get_address(better_headers.to[0][1])
        from_ = EmailAddress.get_address(better_headers.from_[0][1])
        

        email_msg = Email.objects.create(
            created_timestamp=better_headers.date,
            subject=better_headers.subject,
            owner=self.profile.user,
            to=to,
            sent_from=from_,
            server_id=id,
            folder=folder,
        )
            
        email_msg.write_body(html_string.strip() + msg_string)

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
                        folder):
        skipped = 0
        errors = 0
        queryset = self.profile.emails
        

        for id in reversed(mail_ids):
            if isinstance(id, bytes):
                id = id.decode('utf-8')
            
                
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
                    folder)

            except UnicodeDecodeError:
                errors += 1
                logger.error(f'Failed to decode email {id}')
            except Exception as e:
                errors += 1
                logger.error(f'An unexpected error occurred: {e}')

        logger.warn(f'{skipped} emails skipped')
        logger.warn(f'{errors} errors handled')

    def fetch_all_folders(self):
        mail = self.fetch_mailbox()
        for folder in self.profile.folders:
            mail.select(folder.label)
            try:
                type, data = mail.search(None, 'ALL')
            except imaplib.IMAP4.error:
                continue
            mail_ids = data[0].split()
            latest = folder.latest
            self.fetch_messages(mail, mail_ids, latest, folder)
        


class EmailSMTP(EmailBaseClass):

    def __init__(self, profile):
        self.profile = profile
        self.SMTP_PORT = self.profile.outgoing_port
        self.SMTP_SERVER = self.profile.outgoing_server


if __name__ == "__main__":
    profile = UserProfile.objects.first()
    client = EmailSMTP(profile)
    client.fetch_all_folders()