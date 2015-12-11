import smtplib

class SMTPlibexception(Exception): pass

def sendmail(from_addr, to_addr_list, subject, message, smtpserver='10.177.1.10'):
    header = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
    try:
        server = smtplib.SMTP(smtpserver)
        server.sendmail(from_addr, to_addr_list, message)
        server.quit()
    except SMTPlibexception:
        raise SMTPException("Error sending mail")


