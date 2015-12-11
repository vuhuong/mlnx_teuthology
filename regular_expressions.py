"""
This file will contain the regular expressions
"""
#get primary ip address for eth0 from unix host
GET_PRIMARY_IP_UNIX = "sudo ifconfig eth0 | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p'"
