#!/usr/bin/python
# -*- encoding: utf-8 -*-
from antispamscript.ImapClient import ImapClient
import sched
import time
import yaml

with open("config_ass.yml", 'r') as ymlconfigfile:
    cfg = yaml.load(ymlconfigfile, Loader=yaml.BaseLoader)
    imap_param = cfg['imap']
    imap_host = imap_param['host']
    imap_userid = imap_param['userid']
    imap_password = imap_param['password']


def do_something(sc):
    try:
        print("Doing stuff...")
        with open("filter_ass.yml", 'r') as ymlfilterfile:
            cfgf = yaml.load(ymlfilterfile, Loader=yaml.BaseLoader)
            misc_param = cfgf['misc']
            interval = int(misc_param['interval'])
            filter_param = cfgf['filter']
        imap = ImapClient(recipient=imap_userid, password=imap_password, server=imap_host)
        imap.login()
        imap.select_folder('INBOX')
        messages = imap.get_messages()
        print("Messages in mailbox: ", len(messages))
        # Do something with the messages
        for msg in messages:
            # msg is a dict of {'num': num, 'msgid': msg_id, 'to': msg_to, 'from': msg_from,
            #                   'subject': msg_subject, 'body': body}
            for item in filter_param:
                # handle a mail
                delete_this_message = True
                for attribute in item:
                    if msg[attribute] is not None:
                        if item[attribute] not in msg[attribute]:
                            delete_this_message = False

                if delete_this_message:
                    print('Deleted :', msg['to'], '|', msg['from'], '|', msg['subject'], )
                    imap.delete_message(msg['num'])
        imap.logout()
        # when done, yo
        # do your stuff
        app.enter(interval, 1, do_something, (sc,))
    except Exception as err:
        print('Get Messages Failed!')
        print(err)


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
