# Anti-Spam Mail Cleaner — Installation Guide

Tested on Raspberry Pi OS (Bookworm / Bullseye), Python 3.9+.

---

## 1. Prerequisites

```bash
# Make sure Python 3 is installed
python3 --version
```

### Install PyYAML

On **Raspberry Pi OS Bookworm (and newer Debian-based systems)** pip is blocked from
modifying the system Python (PEP 668 — "externally managed environment").
Use `apt` instead, which is the recommended approach:

```bash
sudo apt install python3-yaml
```

> **Alternative — virtual environment** (keeps dependencies isolated):
> ```bash
> cd /home/pi/anti-spam-script
> python3 -m venv venv
> source venv/bin/activate
> pip install pyyaml
> ```
> If you use a venv, update `ExecStart` in `antispam.service` to point to the
> venv's interpreter:
> ```ini
> ExecStart=/home/pi/anti-spam-script/venv/bin/python3 /home/pi/anti-spam-script/script.py
> ```

---

## 2. Copy the files to the Raspberry Pi

From your PC, copy the project folder to the Pi (adjust the IP address):

```bash
scp -r anti-spam-script pi@192.168.1.xx:/home/pi/anti-spam-script
```

Or clone it directly on the Pi if you have it in a git repository:

```bash
git clone https://github.com/WKielen/anti-spam-script.git /home/pi/anti-spam-script
```

---

## 3. Configure mailboxes — `config_ass.yml`

Edit the file on the Pi:

```bash
nano /home/pi/anti-spam-script/config_ass.yml
```

Add one `emailparam` block per mailbox:

```yaml
imap:
  - emailparam:
      userid   : you@example.com
      password : your-password
      host     : imap.yourprovider.com
      port     : 993
  - emailparam:
      userid   : other@example.com
      password : other-password
      host     : imap.otherprovider.com
      port     : 993

# Optional: override the log directory (default: logs/ next to script.py)
# log:
#   dir: /var/log/antispam
```

> **Tip — protect the file** because it contains passwords:
> ```bash
> chmod 600 /home/pi/anti-spam-script/config_ass.yml
> ```

---

## 4. Configure filter rules — `filter_ass.yml`

```bash
nano /home/pi/anti-spam-script/filter_ass.yml
```

```yaml
misc:
  interval: 300   # seconds between mailbox checks (300 = every 5 minutes)

filter:
  # Each rule is a set of fields that must ALL match (AND logic).
  # Rules are tested in order; the first match deletes the message.
  # Supported fields: from, to, subject, body

  - from: noreply@unwanted-sender.com          # match on sender alone

  - to     : info@example.com                  # match on recipient AND body
    body   : "bitcoin"

  - subject: "You have won"                    # match on subject alone
```

**Matching rules:**
- Each field is a **substring match** (case-sensitive).
- All fields in a single rule must match for the message to be deleted.
- Different rules use **OR** logic — any matching rule deletes the message.

---

## 5. Test manually before installing as a service

```bash
cd /home/pi/anti-spam-script
python3 script.py
```

You should see output like:

```
2026-05-31 14:00:01  INFO  main  Anti-spam service starting — accounts: 2  interval: 300s  log: …
2026-05-31 14:00:02  INFO  you@example.com  Worker started (interval=300s)
2026-05-31 14:00:04  INFO  you@example.com  you@example.com  inbox:  42  deleted:   3
```

Check the log file:

```bash
cat /home/pi/anti-spam-script/logs/antispam.log
```

Press **Ctrl+C** to stop once you are satisfied it works.

---

## 6. Install as a systemd service

### 6a. Edit the service file

Open `antispam.service` and verify the paths match your setup:

```bash
nano /home/pi/anti-spam-script/antispam.service
```

The two lines to check:

```ini
WorkingDirectory=/home/pi/anti-spam-script
ExecStart=/usr/bin/python3 /home/pi/anti-spam-script/script.py
```

If your username is not `pi`, also update:

```ini
User=pi
Group=pi
```

### 6b. Install and enable

```bash
# Copy the service file to systemd
sudo cp /home/pi/anti-spam-script/antispam.service /etc/systemd/system/antispam.service

# Tell systemd about the new file
sudo systemctl daemon-reload

# Start the service now
sudo systemctl start antispam

# Enable it so it starts automatically after every reboot
sudo systemctl enable antispam
```

---

## 7. Managing the service

| Action | Command |
|---|---|
| Check status | `sudo systemctl status antispam` |
| Start | `sudo systemctl start antispam` |
| Stop | `sudo systemctl stop antispam` |
| Restart | `sudo systemctl restart antispam` |
| Disable autostart | `sudo systemctl disable antispam` |
| Live log (systemd journal) | `journalctl -u antispam -f` |
| Last 50 journal lines | `journalctl -u antispam -n 50` |

---

## 8. Log files

Logs are written to `logs/antispam.log` inside the script directory (or the `log.dir` you set in `config_ass.yml`).

Each deleted message is logged with full details:

```
2026-05-31 14:23:01  INFO  DELETED
  from   : spam@example.com
  to     : info@example.com
  date   : Sat, 31 May 2026 14:20:00 +0200
  subject: Win a prize!
  body   : Click here to claim your reward…
```

Logs rotate automatically at 5 MB and 5 backup files are kept.

---

## 9. Updating filter rules

You can edit `filter_ass.yml` at any time — no restart needed.  
The running service re-reads the filter file at the start of each check interval.

---

## 10. Troubleshooting

**Service fails to start**
```bash
journalctl -u antispam -n 30
```
Look for `ImportError` (missing `pyyaml`) or `FileNotFoundError` (wrong paths in the service file).

**Login failed**
- Double-check the password in `config_ass.yml`.
- Some providers (Gmail, Outlook) require an **app password** rather than your regular account password. Check your provider's IMAP settings.
- Make sure IMAP is enabled in your mail provider's settings.

**Messages not being deleted**
- Check that the filter field name (`from`, `to`, `subject`, `body`) is spelled correctly.
- Matching is **case-sensitive** and **substring-based**. `"bitcoin"` will not match `"Bitcoin"` — add a separate rule for each variant.
- Run the script manually and watch the output to see what the actual field values look like.

**Port 993 refused**
- Verify the IMAP host and port with your provider.
- Some providers use port 143 with STARTTLS instead of 993 with SSL; set `use_ssl: false` and `port: 143` if needed (requires a code change to `ImapClient` — contact your provider first).
