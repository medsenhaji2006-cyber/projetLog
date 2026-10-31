import os
import re

PATTERN = re.compile(r'(\w{3})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2}).+?:\s(.+)')
IP_PATTERN = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3})\b')

IP = r'(\d{1,3}(?:\.\d{1,3}){3})'

FAILED_PATTERN = re.compile(
    r'(?:message repeated (\d+) times: \[ )?'
    r'Failed \w+ for (invalid user )?(\S*) from ' + IP + r' port \d+'
)
ACCEPTED_PATTERN = re.compile(r'Accepted \w+ for (\S+) from ' + IP + r' port \d+')
INVALID_USER_PATTERN = re.compile(r'Invalid user (\S*) from ' + IP + r' port \d+')
DISCONNECT_PATTERN = re.compile(
    r'(?:Connection closed by|Connection reset by|Disconnected from)'
    r'(?: (?:authenticating|invalid) user (\S*))?'
    r' ' + IP + r' port \d+(?: \[preauth\])?'
)
SESSION_OPENED_PATTERN = re.compile(
    r'pam_unix\(sshd:session\): session opened for user ([^\s(]+)'
)


def classify(message):
    """Retourne (event_type, user, ip, count)."""
    try:
        m = FAILED_PATTERN.match(message)
        if m:
            repeated, invalid, user, ip = m.groups()
            event_type = 'failed_invalid_user' if invalid else 'failed_password'
            return event_type, user or None, ip, int(repeated) if repeated else 1

        m = ACCEPTED_PATTERN.match(message)
        if m:
            return 'accepted', m.group(1), m.group(2), 1

        m = INVALID_USER_PATTERN.match(message)
        if m:
            return 'invalid_user', m.group(1) or None, m.group(2), 1

        m = DISCONNECT_PATTERN.match(message)
        if m:
            return 'disconnect', m.group(1) or None, m.group(2), 1

        m = SESSION_OPENED_PATTERN.match(message)
        if m:
            return 'session_opened', m.group(1), None, 1

        return 'other', None, None, 1
    except Exception as e:
        os.makedirs("logs", exist_ok=True)
        with open("logs/process.log", "a", encoding="utf-8") as f:
            f.write(f"Erreur classify: {str(e)} | Message: {message}\n")
        return 'other', None, None, 1


def extract_from_row(row):
    try:
        match = PATTERN.search(row)
        if not match:
            return None

        message = match.group(4)
        event_type, user, ip, count = classify(message)

        if ip is None:
            ip_match = IP_PATTERN.search(message)
            ip = ip_match.group(1) if ip_match else None

        return {
            'month': match.group(1),
            'day': int(match.group(2)),
            'time': match.group(3),
            'message': message,
            'ip': ip,
            'user': user,
            'event_type': event_type,
            'count': count,
        }
    except Exception as e:
        os.makedirs("logs", exist_ok=True)
        with open("logs/process.log", "a", encoding="utf-8") as f:
            f.write(f"Erreur extract_from_row: {str(e)} | Row: {row}\n")
        return None
