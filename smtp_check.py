import smtplib
from email.message import EmailMessage

def send_email(subject:str,message:str, to_email:str) -> str:
    sender = 'tasievbajel2@gmail.com'
    password = 'lwfwbcqvqcxrexxd'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    msg = EmailMessage()
    msg.set_content('ihihia')


    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email

    try:
        server.login(sender, password)
        server.send_message(msg)
        return '200 OK'
    except Exception as error:
        return f"{error}"

print(send_email('Python', 'HEllo', 'olegivanov81360@gmail.com'))

emails = ['adsa81360@gmail.com', 'olegivanov81360@gmail.com', 'dobryjdenoleg@gmail.com', 'h4peryt@gmail.com']
for i in emails:
    send_email('Python', 'HEllo', i)