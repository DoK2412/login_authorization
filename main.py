import smtplib as smtp
from settings import email_out, password_email


async def sendEmail(code, email_user):
    email = email_out
    password = password_email
    dest_email = email_user

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

