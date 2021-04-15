import json
import socket
import psutil
import requests


def get_group_ips():
    # wF50nURHTrEWclhl4WMJP4zPnqw1dVa8
    headers = {
        'Authorization': 'bearer wF50nURHTrEWclhl4WMJP4zPnqw1dVa8',
        'Content-Type': 'application/json'
    }
    # a0cbf4b62a17e0f2
    url = "https://my.zerotier.com/api/network/a0cbf4b62a17e0f2/member"
    result = requests.get(url=url, headers=headers)
    online_list = []
    offline_list = []
    for str in json.loads(result.text):
        if str["online"] == True:
            online_list.append(str["config"]["ipAssignments"][0])
        else:
            offline_list.append(str["config"]["ipAssignments"][0])
    return online_list, offline_list


def get_local_ips():
    netcard_info = []
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            netcard_info.append(item.address)
    return netcard_info


def get_local_ip():
    online, offline = get_group_ips()
    all_p2p_ips = online + offline
    local_ips = get_local_ips()
    real_ip = ""
    for ip in local_ips:
        if ip in all_p2p_ips:
            real_ip = ip
            # print(real_ip)
    return real_ip


def get_host_name():
    return socket.gethostname()


