import smtplib, ssl
from email.mime.multipart import MIMEMultipart

class Mail:

    def __init__(self):
        self.port = "t.b.d."
        self.smtpServerDomainName = "t.b.d."
        self.senderMail = "t.b.d.m"
        self.receiverMail = ["t.b.d.", "t.b.d."]
        self.password = "t.b.d."


    def sendMail(self):
        sslContext = ssl.create_default_context()
        service = smtplib.SMTP_SSL(self.smtpServerDomainName, self.port, context=sslContext)
        service.login(self.senderMail, self.password)
        
        msg = MIMEMultipart()
        msg["Subject"] = "ALARM WOHNHAUS"

        for email in self.receiverMail:
            service.sendmail(self.senderMail, email, msg.as_string())

        service.quit()
