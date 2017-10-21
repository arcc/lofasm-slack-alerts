# small python library to hide the details with communicating with Slack servers

import os
from slackclient import SlackClient
from datetime import datetime


def get_config_params(f=None):
    '''
    read this station's slack config file and parse parameters
    '''

    if f is None:
        f = os.path.join(os.environ['HOME'], '.lofasm/slackconfig')
    
    cfg_contents = ''
    cfg_dict = {}
    with open(f, 'r') as cfg:
        cfg_contents = cfg.readlines()
    
    for line in cfg_contents:
        line = line.split()
        cfg_dict[line[0]] = line[1]
    
    return cfg_dict

def sendmsg(msg, fmt="%Y/%m/%d %H:%M:%S"):
    '''
    send message to slack channel.

    prepend with station id
    '''

    cfg = get_config_params()
    sc = SlackClient(cfg['token'])
    now = datetime.now().utcnow().strftime(fmt)

    msg = "*LCC {}* @ {} UTC: ".format(cfg['station_id'], now) + msg

    sc.api_call(
    "chat.postMessage",
    channel="#lofasm-station-feed",
    text=msg,
    )