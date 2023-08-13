import smtplib as smtp
import random
from email.mime.text import MIMEText


async def sendEmail(code):
    email = 'DoK2.4.12@yandex.ru'
    password = 'ddyqwbhkhlwyhyat'
    dest_email = 'snd_test@mail.ru'

    subject = 'Confirmation of registration.'
    email_text = f'Your registration confirmation code: {str(code.encode("utf8"))}\n'

    message = 'From: {}\nTo: {}\nSubject: {}\n\n{}'.format(email,
                                                           dest_email,
                                                           subject,
                                                           email_text)
    server = smtp.SMTP_SSL('smtp.yandex.com', 465)
    server.set_debuglevel(1)
    server.ehlo(email)
    server.login(email, password)
    server.auth_plain()
    server.sendmail(email, dest_email, message)
    server.quit()






# def sendEmail(massege):
#     print(massege)
#     sender: str = 'dok24.12.93@gmail.com'
#     password: str = 'buevotribdwprwxy'
#
#     recipient = 'snd_test@mail.ru'
#
#     server = smtp.SMTP('smtp.gmail.com', 587)
#     server.starttls()
#     subject = 'Код подтверждения.'
#
#     # try:
#     # massege = 'Ваш код подтверждения:' + str(massege)
#     server.login(sender, password)
#     msg_massege = MIMEText(str(massege))
#     # print(msg_massege)
#     # msg_subject = MIMEText(str(subject))
#     server.sendmail(sender, recipient, msg_massege.as_string())
#
#     # server.sendmail(sender, recipient, f'Subject:{msg_subject.as_string()}Ваш код водтверждения{msg_massege.as_string()}')
#     # except Exception:
#     #     print('yt hf,jnfyn')

