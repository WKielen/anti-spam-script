#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anti-spam mail cleaner.
Runs as a long-lived service; checks configured mailboxes at a fixed interval
and deletes messages that match the filter rules in filter_ass.yml.
"""

import logging
import logging.handlers
import os
import signal
import sys
import threading
import time
import yaml

from antispamscript.ImapClient import ImapClient

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Config loading ─────────────────────────────────────────────────────────────

def _load_yaml(filename):
    path = os.path.join(SCRIPT_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# ── Logging setup ──────────────────────────────────────────────────────────────

def setup_logging(log_dir):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'antispam.log')

    fmt = logging.Formatter(
        fmt='%(asctime)s  %(levelname)-8s  %(name)s  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8',
    )
    file_handler.setFormatter(fmt)

    # Force UTF-8 on stdout so emoji in subjects don't crash on latin-1 terminals
    stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1, closefd=False)
    console_handler = logging.StreamHandler(stream)
    console_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(file_handler)
    root.addHandler(console_handler)

    return log_file


# ── Filter matching ────────────────────────────────────────────────────────────

def matches_rule(msg, rule):
    """Return True only when every field in *rule* is found in the message."""
    for field, expected in rule.items():
        value = msg.get(field)
        if not value or expected not in value:
            return False
    return True


# ── Deletion logging ───────────────────────────────────────────────────────────

def log_deleted(log, msg):
    body_preview = (msg.get('body') or '').strip()[:1000]
    log.info(
        'DELETED\n'
        '  from   : %s\n'
        '  to     : %s\n'
        '  date   : %s\n'
        '  subject: %s\n'
        '  body   : %s',
        msg.get('from', ''),
        msg.get('to', ''),
        msg.get('date', ''),
        msg.get('subject', ''),
        body_preview,
    )


# ── Mailbox processing ─────────────────────────────────────────────────────────

def process_mailbox(account, filters, log):
    ep = account['emailparam']
    user = ep['userid']

    imap = ImapClient(
        recipient=user,
        password=ep['password'],
        server=ep['host'],
        portnumber=int(ep['port']),
        use_ssl=True,
    )
    imap.login()
    imap.select_folder('INBOX')
    messages = imap.get_messages()

    deleted = 0
    for msg in messages:
        for rule in filters:
            if matches_rule(msg, rule):
                deleted += 1
                log_deleted(log, msg)
                imap.mark_deleted(msg['num'])
                break  # one rule matched — skip remaining rules for this message

    log.info('%-35s  inbox: %3d  deleted: %3d', user, len(messages), deleted)
    imap.logout()  # CLOSE inside logout triggers the actual EXPUNGE
    return deleted


# ── Per-account worker thread ──────────────────────────────────────────────────

def mailbox_worker(account, filters, interval, stop_event, counter, counter_lock):
    user = account['emailparam']['userid']
    log = logging.getLogger(user)
    log.info('Worker started  (interval=%ds)', interval)

    while not stop_event.is_set():
        try:
            n = process_mailbox(account, filters, log)
            with counter_lock:
                counter[0] += n
        except Exception:
            log.exception('Mailbox check failed')

        # Sleep in short slices so SIGTERM wakes us up quickly
        stop_event.wait(timeout=interval)

    log.info('Worker stopped')


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    cfg     = _load_yaml('config_ass.yml')
    fil_cfg = _load_yaml('filter_ass.yml')

    interval = int((fil_cfg.get('misc') or {}).get('interval', 300))
    filters  = fil_cfg.get('filter') or []
    log_dir  = (cfg.get('log') or {}).get('dir', os.path.join(SCRIPT_DIR, 'logs'))

    log_file = setup_logging(log_dir)
    log = logging.getLogger('main')
    log.info('Anti-spam service starting — accounts: %d  interval: %ds  log: %s',
             len(cfg['imap']), interval, log_file)

    stop_event    = threading.Event()
    counter       = [0]
    counter_lock  = threading.Lock()

    def _shutdown(signum, _frame):
        log.info('Signal %d received — stopping', signum)
        stop_event.set()

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT,  _shutdown)

    threads = []
    for account in cfg['imap']:
        t = threading.Thread(
            target=mailbox_worker,
            args=(account, filters, interval, stop_event, counter, counter_lock),
            daemon=True,
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    log.info('Service stopped — total deleted this session: %d', counter[0])


if __name__ == '__main__':
    main()
