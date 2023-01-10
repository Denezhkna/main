import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from api.views.parametrs import SCAN_FOLDER_PATH

subject = 'Документ'
body = 'тест'
sender_email = 'scan@baltoftech.ru'
password = '1#Qwerty'

def send_email(receiver_email, data_file_name, id_session):
    session_folder = SCAN_FOLDER_PATH+id_session+"/"
    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        
        message.attach(MIMEText(body, 'plain'))
        for file_name in data_file_name:
            with open(session_folder + file_name, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                "attachment; filename = "+id_session+"_"+file_name
            )
            message.attach(part)
        text = message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.mastermail.ru", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)

        return True    
    except:
        return False
