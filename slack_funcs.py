# small python library to hide the details with communicating with Slack servers

import os
from slackclient import SlackClient
from datetime import datetime
import io


def get_config_params(f=None):
    '''
    read this station's slack config file and parse parameters
    '''

    if f is None:
        f = os.path.join('/home/controller/.lofasm/slackconfig')
    
    cfg_contents = ''
    cfg_dict = {}
    with open(f, 'r') as cfg:
        cfg_contents = [x for x in cfg.readlines() if not x.startswith('#')]
    
    for line in cfg_contents:
        line = line.split()
        cfg_dict[line[0]] = line[1]
    
    return cfg_dict

def sendmsg(msg, fmt="%Y/%m/%d %H:%M:%S"):
    '''
    send message to slack channel.

    prepend with station id & time stamp
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

def uploadImage(fpath, title='', fmt="%Y/%m/%d %H:%M:%S"):
    '''
    upload image to slack channel.
    '''
    cfg = get_config_params()
    sc = SlackClient(cfg['token'])
    station = cfg['station_id']
    now = datetime.now().utcnow().strftime(fmt)
    
    with open(fpath, 'rb') as f:
        content = io.BytesIO(f.read())
    
    result = sc.api_call(
        "files.upload",
        channels="#lofasm-station-feed",
        filename=fpath,
        title='LCC ' + station + ' @ ' + now +' UTC: ' + title,
        file=content
    )
    return result