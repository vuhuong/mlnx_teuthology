"""
This the utilities python module.
All the commonly used function to be
implemented in this utilities module
"""

import os
import subprocess
import yaml

from prettytable import PrettyTable


#--------#
##########
# Mailer #
##########
#--------#
class Mailer:
    """
    User needs to configure sendmail sever on which the
    automation framework is running.
    """
    command = "/usr/sbin/sendmail -oi -t"

    def __init__(self, recipient, sender, subject=None, reply=None):
        self.msg = []

        self.recipient = recipient
        self.sender = sender
        self.reply = reply and reply or sender
        self.subject = subject and subject or 'No Subject'

    def __str__(self):
        return '%s --> %s: "%s" [...]x%d' % \
              (self.sender, self.recipient, self.subject, len(self.msg))

    def header(self):
        head = []
        head.append('To: %s' % self.recipient)
        head.append('From: %s' % self.sender)
        head.append('Reply-to: %s' % self.reply)
        head.append('Subject: %s' % self.subject)
        head.append('')
        return head

    def write(self, msg):
        self.msg.append(msg)

    def send(self):
        mail = subprocess.Popen(self.command, stdout=subprocess.PIPE, \
                                stdin=subprocess.PIPE, shell=True)
        mail.stdin.write("\n".join(self.header() + self.msg))
        mail.stdin.write("\n\0")
        mail.stdin.close()

    def show(self):
        print "\n".join(self.header() + self.msg)

def read_yaml(path):
    """
    This function will read the yaml file
    and read the structure in the dictionary format
    """
    if not is_file_valid(path):
        raise RuntimeError("Yaml file %s not present" % path)
    with open(path, 'r') as fh:
        return yaml.load(fh)

def sms_email(number, provider):
    provider = provider.lower()
    n_fmt = {'att': lambda n:  '%d' % n}
    p_fmt = {'att': '%s@txt.att.net'}
    return p_fmt[provider] % n_fmt(number)

def send_sms(number, provider, sender, title, msg):
    sms_limit = 140
    m = Mailer(sms_email(number, provider), sender, title)
    if len(msg) > sms_limit:
        print ("WARN: SMS is %d (>%d) characters, might be truncated" %
               (len(msg), sms_limit))
    m.write(msg)
    m.send()

def is_file_valid(file_path):
    return os.path.isfile(file_path)

def is_path(dir):
    return os.path.isdir(dir)

def create_dir(path):
    return os.makedirs(path)

def prettytable(padding_w, l_dict ,arg):
    x = PrettyTable(arg)
    x.padding_width = padding_w
    for k,v in l_dict.items():
        x.add_row([k,v])
    return x
