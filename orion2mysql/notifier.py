
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from ConfigParser import SafeConfigParser
import sys

__version__ = "1.0"

class Email(object):
    """"
    Send a email using this class.

    Suppported methods:
        __init__():         constructor that initializes sender email account, password, mail server and mail server port
        default_settings(): optional constructor that uses the predefined settings for the sender and the email server
        send_email():       send a email to a list of receivers 
    """    

    def __init__(self, sender, password):
        """ Constructor """
        
        self.sender = sender
        self.password = password
        

        # email server settings
        self.email_host = "smtp.gmail.com" 
        self.port = 587 


    @classmethod
    def default_settings(cls):
        """ Optional constructor"""
    
        parser = SafeConfigParser()
        parser.read('/etc/sysconfig/fallRiskEvaluation/fallRiskEvaluation.conf')
        receiver = parser.get('notifications', 'EMAIL') 
        password = parser.get('notifications', 'PASSWORD')
        return cls(receiver, password)


    def send_email(self, receiver_list, text):
        """ Send email """

        gmail_user = self.sender
        gmail_pwd = self.password
        FROM = self.sender
        TO = receiver_list       # list

        SUBJECT = "[ANGEL] Angel platform notification"
        TEXT = text

        # Prepare actual message
        message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

        try:
        
            server = smtplib.SMTP(self.email_host, self.port)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, TO, message)
            server.quit()

        except:
            import traceback
            #traceback.print_stack()
            traceback.print_exc()


    def send_html_email(self, receiver_list, text, html):
        """
        Send email included HTML table
        """

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart('alternative')

        msg['Subject'] = "[ANGEL] Angel platform notification"
        msg['From'] = self.sender
        msg['To'] = receiver_list
        

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        msg.attach(part1)
        msg.attach(part2)

        try:     
            server = smtplib.SMTP(self.email_host, self.port)
            server.ehlo()
            server.starttls()
            server.login(self.sender, self.password)
            server.sendmail(self.sender, receiver_list, msg.as_string())
            server.quit()
        except:
            import traceback
            #traceback.print_stack()
            traceback.print_exc()


    def send_email_xls_attachment(self, receiver, text, pathfile):
        """
        Send a mail notification included a .xlsx file with details in high falling risk

        """

        msg = MIMEMultipart()

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('mixed')
        msg['Subject'] = "[ANGEL] Angel platform notification"
        msg['From'] = self.sender
        msg['To'] = receiver

        part1 = MIMEText(text, 'html')
        #attach an excel file:
        fp = open(pathfile, 'rb')
        file1 = MIMEBase('application','vnd.ms-excel')
        file1.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(file1)
        file1.add_header('Content-Disposition','attachment;filename=detailed-notification.xlsx')

        #======================================
        # Attach parts into message container
        #======================================
        msg.attach(part1)
        msg.attach(file1)
        composed = msg.as_string()

        fp = open('msgtest.eml', 'w')
        fp.write(composed)

        #=======================
        # The actual mail send  
        #=======================
        try:
            # list of receiver
            receiver_list = list()
            receiver_list.append(receiver)

            #================================
            # send the email with attachment
            #================================
            server = smtplib.SMTP(self.email_host, self.port)
            server.ehlo()
            server.starttls()
            server.login(self.sender, self.password)
            server.sendmail(self.sender, receiver_list, composed)
            server.quit()
            fp.close()
            return 1

        except smtplib.SMTPException, s:
            print >> sys.stderr, "a"
            return -1
        except smtplib.socket.error, a:
            print >> sys.stderr, "b"
            return -1
        except:
            import traceback
            traceback.print_exc()
            return -1
