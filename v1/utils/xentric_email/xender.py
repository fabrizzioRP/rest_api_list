import smtplib, ssl, multiprocessing
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from mongoengine.queryset.visitor import Q
from .config import settings
from .model import SourceEmail, QueueEmail, LogEmail, EMAIL_STATUS


class EmailControl():
    settings = None
    database = None
    email = None
    context = None

    def __init__(self, *args, **kwargs):
        self.settings = settings()
        self.database = self.settings['database']
        self.email = self.settings['email']
        #self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv3)
        
    def allocator(self, email_data):

        log_email = LogEmail(
            result = 'Assigned to the queue',
            status = 0
        )
        
        new_email = QueueEmail(
            reason = email_data.body_email,
            subject = email_data.subject,
            body = email_data.body,
            current_status = 0,
            log = [log_email]
        )
        try:
            new_email.save()
        except Exception as error:
            raise error
        # Create a secure SSL context
        #context = ssl.create_default_context()
    def sender(self):
        #manager = multiprocessing.Manager()
        queue = QueueEmail.objects.filter(Q(current_status=0) | Q(current_status=2)).filter(retries__lte=8)

        for email in queue:
            process = multiprocessing.Process(target=self.xmailer, args=(email,))
            process.start()



    def xmailer_user(self, user, email):
        message = MIMEMultipart()
        message["Subject"] = user['credenciales']['email']
        message["From"] = self.email['sender']
        message["To"] = user['credenciales']['email']
        text = MIMEText(email['body'], "plain")
        message.attach(text)
        try:
            with smtplib.SMTP_SSL(self.email['server'], self.email['port']) as server:
                try:
                    print(server)
                    server.login(self.email['sender'], self.email['passwd'])
                    print(self.email['sender'], self.email['passwd'])
                    smtp_result = server.sendmail(self.email['sender'], user['credenciales']['email'], message.as_string() )
                    email_log = LogEmail(
                        result = 'sended',
                        status = 1
                    )
                    user['email_log'].append(email_log)
                    user.save()
                except Exception as error:
                    email_log = LogEmail(
                        result = str(error),
                        status = 2
                    )
                    user['email_log'].append(email_log)
                    user.save()
        except Exception as error:
            email_log = LogEmail(
                result = str(error),
                status = 2
                )
            user['email_log'].append(email_log)
            user.save()

    def xmailer(self, email):
        message = MIMEMultipart()
        message["Subject"] = email.subject
        message["From"] = self.email['sender']
        message["To"] = self.email['recept']
        text = MIMEText(email.body, "plain")
        message.attach(text)
        try:
            with smtplib.SMTP_SSL(self.email['server'], self.email['port'], context=self.context) as server:
                try:
                    server.login(self.email['sender'], self.email['passwd'])
                    smtp_result = server.sendmail(self.email['sender'], self.email['recept'], message.as_string() )
                    email_log = LogEmail(
                        result = 'sended',
                        status = 1
                    )
                    email.log.append(email_log)
                    email.current_status = 1
                    email.retries = email.retries + 1
                    email.save()
                except Exception as error:
                    email_log = LogEmail(
                        result = str(error),
                        status = 2
                    )
                    email.log.append(email_log)
                    email.current_status = 2
                    email.retries = email.retries + 1
                    email.save()
        except Exception as error:
            email_log = LogEmail(
                result = str(error),
                status = 2
                )
            email.log.append(email_log)
            email.current_status = 2
            email.retries = email.retries + 1
            email.save()




