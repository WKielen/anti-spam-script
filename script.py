#!/usr/bin/python
# -*- encoding: utf-8 -*-
import sys

from antispamscript.ImapClient import ImapClient
import sched
import time
import yaml
from time import strftime

with open("config_ass.yml", 'r') as ymlconfigfile:
    cfg = yaml.load(ymlconfigfile, Loader=yaml.BaseLoader)
    imap_param = cfg['imap']


def do_something(itemuser, count_deleted):
    try:
        emailparam = itemuser['emailparam']
        imap_host = emailparam['host']
        imap_userid = emailparam['userid']
        imap_password = emailparam['password']
        imap_port = emailparam['port']

        with open("filter_ass.yml", 'r') as ymlfilterfile:
            cfgf = yaml.load(ymlfilterfile, Loader=yaml.BaseLoader)
            misc_param = cfgf['misc']
            interval = int(misc_param['interval'])
            filter_param = cfgf['filter']
        imap = ImapClient(recipient=imap_userid, password=imap_password, server=imap_host, portnumber=int(imap_port), use_ssl=True)
        imap.login()
        imap.select_folder('INBOX')
        messages = imap.get_messages()
        print(strftime("%H:%M", time.localtime()), "User: ", imap_userid, " Messages in mailbox: ", len(messages), '|', count_deleted, 'deleted')
        # Do something with the messages
        for msg in messages:
            # msg is a dict of {'num': num, 'msgid': msg_id, 'to': msg_to, 'from': msg_from,
            #                   'subject': msg_subject, 'body': body}
            # print (msg['subject'])
            for item in filter_param:
                # handle a mail
                delete_this_message = True
                for attribute in item:
                    if msg[attribute] is not None:
                        if item[attribute] not in msg[attribute]:
                            delete_this_message = False

                if delete_this_message:
                    count_deleted += 1
                    print('Deleted : ', count_deleted, '|', msg['to'], '|', msg['from'], '|', msg['subject'], )
                    imap.delete_message(msg['num'])
        imap.logout()

    except Exception as err:
        print('Get Messages Failed!')
        print(err)
    # when done, yo
    # do your stuff
    app.enter(interval, 1, do_something, (itemuser, count_deleted,))


app = sched.scheduler(time.time, time.sleep)
for itemuser in imap_param:
    do_something(itemuser, count_deleted=0)


def main():
    app.run()
# Net de applicatie gestart. Hieronder wordt de main thread levend gehouden.
    while True:
        time.sleep(30)


if __name__ == '__main__':
    main()
