"""
User will require to update this file.
settings.py will get updated using custom_settings.py
"""
RUN_TYPE = ['bvt', 'ceph_qa']

DEFAULT_RUN_LIST = {
'bvt' : 'runlist/bvt_runlist',
'ceph_qa' : 'runlist/ceph_qa_runlist'}

#for emails not required to send mail
#either comment it using '#' or remove them
# from the list
SEND_MAIL_LIST = ['xyz.xyz@web.com',
'abc.abc@web.com',
]
#IP Address of SMTP Server for email
#configuration
SMTP_SERVER = ''

LOG_PATH_LOCAL = {
'bvt' : '/tmp/teuthology/logs/bvt/',
'ceph_qa' : '/tmp/teuthology/logs/ceph_qa/'}
