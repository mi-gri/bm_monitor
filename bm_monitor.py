#################################################################################

# Brandmeister Monitor
# Develped by: Michael Clemens, DK1MI
# Refactored by: Jeff Lehman, N8ACL
# Modified by: Michael Grigutsch, DO3BOX
# Current Version: 1.2
# Original Script: https://codeberg.org/mclemens/pyBMNotify
# Refactored Script: https://github.com/n8acl/bm_monitor

# Questions? Comments? Suggestions? Contact me one of the following ways:
# E-mail: n8acl@qsl.net
# Twitter: @n8acl
# Discord: Ravendos#7364
# Mastodon: @n8acl@mastodon.radio
# Website: https://www.qsl.net/n8acl

###################   DO NOT CHANGE BELOW   #########################

#############################
##### Import Libraries and configs
import config as cfg
import json
import datetime as dt
import time
import socketio
import http.client, urllib

# libary only needed if Discord is configured in config.py
if cfg.discord:
    from discord_webhook import DiscordWebhook

# libraries only needed if Telegram is configured in config.py
# if cfg.telegram:
#     import telebot 
#     from telethon.sync import TelegramClient 
#     from telethon.tl.types import InputPeerUser, InputPeerChannel 
#     from telethon import TelegramClient, sync, events 

# libraries only needed if dapnet or telegram is configured in config.py
if cfg.dapnet or cfg.telegram:
    import requests
    from requests.auth import HTTPBasicAuth

#############################
##### Define Variables

sio = socketio.Client()

last_TG_activity = {}
last_OM_activity = {}

#############################
##### Define Functions

# Send push notification via Pushover. Disabled if not configured in config.py
def push_pushover(msg):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
        "token": cfg.pushover_token,
        "user": cfg.pushover_user,
        "message": msg,
        }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

def push_telegram(msg):
    telegram_url = "https://api.telegram.org/bot" + cfg.telegram_api_hash + "/sendmessage"

    response = requests.post(
        telegram_url, json = msg, # data=json.dumps(msg),
        headers={'Content-Type': 'application/json'}
    )


# send pager notification via DAPNET. Disabled if not configured in config.py
def push_dapnet(msg):
    dapnet_json = json.dumps({"text": msg, "callSignNames": cfg.dapnet_callsigns, "transmitterGroupNames": [cfg.dapnet_txgroup], "emergency": True})
    response = requests.post(cfg.dapnet_url, data=dapnet_json, auth=HTTPBasicAuth(cfg.dapnet_user,cfg.dapnet_pass)) 

# Send notification to Discord Channel via webhook
def push_discord(wh_url, msg):
    webhook = DiscordWebhook(url=wh_url, content=msg)
    response = webhook.execute()  

def construct_message(c):
    tg = c["DestinationID"]
    out = ""
    duration = c["Stop"] - c["Start"]
    # convert unix time stamp to human readable format
    time = dt.datetime.utcfromtimestamp(c["Start"]).strftime("%Y/%m/%d %H:%M")
    # construct text message from various transmission properties
    out += c["SourceCall"] + ' (' + c["SourceName"] + ') was active on '
    out += str(tg) + ' (' + c["DestinationName"] + ') at '
    out += time + ' (' + str(duration) + ' seconds)'
    # finally return the text message
    print (out)
    return out

def construct_long_message(c):
    tg = c["DestinationID"]
    out = ""
    duration = c["Stop"] - c["Start"]
    # convert unix time stamp to human readable format
    time = dt.datetime.utcfromtimestamp(c["Start"]).strftime("%Y/%m/%d %H:%M")
    # convert SourceID zu str
    source_id = str(c["SourceID"])
    # convert TalkerAlias zu str
    talker_alias = str(c.get("TalkerAlias", ""))
    # convert ContextID zu str
    relais  = str(c["ContextID"])
    # construct text message from various transmission properties
    out += 'Call: ' + c["SourceCall"] + ' (' + source_id + ', ' + c["SourceName"] + ', TA:' + talker_alias + '):\n'
    out += 'TG: ' + str(tg) + ' (' + c["DestinationName"] + ') at ' + time + ' (' + str(duration) + ' seconds)\n'
    out += 'RelaisID:' + str(relais) + ' (' + c["LinkCall"] + ')\n---\n'
    # finally return the text message
    if cfg.verbose:
        print (out)
    return out


#############################
##### Define SocketIO Callback Functions

@sio.event
def connect():
    print('connection established')

@sio.on("mqtt")
def on_mqtt(data):
    call = json.loads(data['payload'])
    tg = call["DestinationID"]
    rpt = call["LinkCall"]
    callsign = call["SourceCall"]
    start_time = call["Start"]
    stop_time = call["Stop"]
    notify = False
    now = int(time.time())

    if cfg.verbose and callsign in cfg.noisy_calls:
        print("ignored noisy ham " + callsign)
    
    else:
        # check if callsign is monitored, the transmission has already been finished
        # and the person was inactive for n seconds
        if rpt in cfg.repeater or callsign in cfg.callsigns:
            if callsign not in last_OM_activity:
                last_OM_activity[callsign] = 9999999
            inactivity = now - last_OM_activity[callsign]
            if callsign not in last_OM_activity or inactivity >= cfg.min_silence:
                # If the activity has happened in a monitored TG, remember the transmission start time stamp
                if tg in cfg.talkgroups and stop_time > 0:
                    last_TG_activity[tg] = now
                # remember the transmission time stamp of this particular DMR user
                last_OM_activity[callsign] = now
                notify = True
        # Continue if the talkgroup is monitored, the transmission has been
        # finished and there was no activity during the last n seconds in this talkgroup
        elif tg in cfg.talkgroups and stop_time > 0:# and callsign not in cfg.noisy_calls:
            if tg not in last_TG_activity:
                last_TG_activity[tg] = 9999999
            inactivity = now - last_TG_activity[tg]
            # calculate duration of key down
            duration = stop_time - start_time
            # only proceed if the key down has been long enough
            if duration >= cfg.min_duration:
                if tg not in last_TG_activity or inactivity >= cfg.min_silence:
                    notify = True
                elif cfg.verbose:
                    print("ignored activity in TG " + str(tg) + " from " + callsign + ": last action " + str(inactivity) + " seconds ago.")
                last_TG_activity[tg] = now


        if notify:
            if cfg.pushover:
                push_pushover(construct_message(call))
            if cfg.telegram:
                push_telegram({'text': construct_long_message(call), 'chat_id': cfg.telegram_api_id, "disable_notification": True})
            if cfg.dapnet:
                push_dapnet(construct_message(call))
            if cfg.discord:
                push_discord(cfg.discord_wh_url, construct_long_message(call))

@sio.event
def disconnect():
    print('disconnected from server')

#############################
##### Main Program

sio.connect(url='https://api.brandmeister.network', socketio_path="/lh/socket.io", transports="websocket")
sio.wait()
