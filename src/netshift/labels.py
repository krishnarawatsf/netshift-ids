"""Map raw dataset labels to the six common classes.

Unknown labels raise an error. They are never silently dropped, so every
mapping decision is visible. Add new raw labels here and in tests/test_labels.py.
"""
import re

from netshift.config import CLASSES

DROP = "DROP"  # classes with no clean match, dropped on both networks

_RAW = {
    "benign": "Benign",
    # DoS
    "dos hulk": "DoS", "dos goldeneye": "DoS", "dos slowloris": "DoS", "dos slowhttptest": "DoS",
    "dos attacks-hulk": "DoS", "dos attacks-goldeneye": "DoS",
    "dos attacks-slowloris": "DoS", "dos attacks-slowhttptest": "DoS",
    "dos attacks-synflooding": "DoS",
    # DDoS
    "ddos": "DDoS", "ddos attacks-loic-http": "DDoS",
    "ddos attack-loic-http": "DDoS", "ddos attacks-loic-udp": "DDoS",
    "ddos attack-loic-udp": "DDoS", "ddos-loic-udp": "DDoS",
    "ddos attacks-hoic": "DDoS", "ddos attack-hoic": "DDoS", "ddos-hoic": "DDoS",
    # Brute-force (SSH and FTP logins)
    "ftp-patator": "Brute-force", "ssh-patator": "Brute-force",
    "ftp-bruteforce": "Brute-force", "ssh-bruteforce": "Brute-force",
    # Web attack (includes web brute force, a decision to confirm with the guide)
    "web attack - brute force": "Web attack", "web attack - xss": "Web attack",
    "web attack - sql injection": "Web attack",
    "brute force -web": "Web attack", "brute force -xss": "Web attack", "sql injection": "Web attack",
    # Bot
    "bot": "Bot",
    # Dropped consistently on both networks
    "heartbleed": DROP, "portscan": DROP, "infiltration": DROP, "infilteration": DROP,
}


def normalize(label) -> str:
    """Fix dash variants and encoding damage, collapse spaces, lowercase."""
    s = str(label).replace("\ufffd", "-").replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def map_label(raw) -> str:
    key = normalize(raw)
    if key not in _RAW:
        raise KeyError(f"Unmapped label: {raw!r} (normalized {key!r}). Add it to labels.py.")
    mapped = _RAW[key]
    assert mapped == DROP or mapped in CLASSES, f"Bad mapping target {mapped!r}"
    return mapped


def map_series(s):
    """Map a whole pandas Series. Each unique label is checked once."""
    table = {u: map_label(u) for u in s.dropna().unique()}
    return s.map(table)
