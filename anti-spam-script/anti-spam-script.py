#!/usr/bin/python
# -*- encoding: utf-8 -*-
from ImapClient import ImapClient
import sched
import time
import yaml
import imaplib
import sys
import base64
import email


with open("..\\config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)
    imap_param = cfg['imap']
    imap_host = imap_param['host']
    imap_userid = imap_param['userid']
    imap_password = imap_param['password']
    misc_param = cfg['misc']
    interval = int(misc_param['interval'])



def do_something(sc):
    print ("Doing stuff...")
    imap = ImapClient(recipient=imap_userid, password=imap_password, server=imap_host)
    imap.login();
    imap.select_folder('INBOX')
    messages = imap.get_messages()
    # Do something with the messages
    print("Messages in my inbox:")
    for msg in messages:
        # msg is a dict of {'num': num, 'body': body}
        # print(msg['num'], msg['msgid'], msg['to'], msg['from'], msg['subject'])
        if msg['to'] is not None:
            if "Serge Hoek" in msg['from']:
                print('Delete', msg['to'], msg['subject'], msg['from'])
                imap.delete_message(msg['num'])
    imap.logout()
    # when done, yo
    # do your stuff
    app.enter(interval, 1, do_something, (sc,))

s = None
app = sched.scheduler(time.time, time.sleep)
do_something(s)

def main():
    app.run()
# Net de applicatie gestart. Hieronder wordt de main thread levend gehouden.
    while True:
        time.sleep(30)


if __name__ == '__main__':
    main()
