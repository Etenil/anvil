import smtplib
import string
import config

def send(origin, dest, subject, message):
    body = string.join((
            "From: %s" % origin,
            "To: %s" % dest,
            "Subject: %s" % subject,
            "",
            message),
            "\r\n")
    try:
        s = smtplib.SMTP(config.val('smtp'))
        s.sendmail(origin, dest.split(","), body)
        s.quit()
    except:
        pass
