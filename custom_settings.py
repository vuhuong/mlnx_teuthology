"""
User will require to update this file.
settings.py will get updated using custom_settings.py
"""
RUN_TYPE = ['bvt', 'bst', 'fvt_inktank', 'fvt_storm']

DEFAULT_RUN_LIST = {
'bvt' : 'runlist/bvt_runlist',
'bst' : 'runlist/bst_runlist',
'fvt_inktank': 'runlist/fvt_inktank_runlist',
'fvt_storm' : 'runlist/fvt_storm_runlist'}

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
'bst' : '/tmp/teuthology/logs/bst/',
'fvt_inktank' : '/tmp/teuthology/logs/fvt_inktank/',
'fvt_storm' : '/tmp/teuthology/logs/fvt_storm/'}
