from __future__ import unicode_literals
import re, socket
iprule = '([0-9]{1,3}\.){3}[0-9]{1,3}'
rule = re.compile(iprule)

def get_host(ipList):
    if isinstance(ipList, str):
        group = rule.match(ipList)
        if group:
            return group.group(0)
        else:
            return None
    for ip in ipList:
        ipresp = get_host(ip)
        if ipresp:
            return ipresp
    return None


def get_server_host():
    ipname = socket.gethostname()
    ipList = socket.gethostbyname_ex(ipname)
    print ipList
    return get_host(ipList)



