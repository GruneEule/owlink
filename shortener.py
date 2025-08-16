#!/usr/bin/env python3
import cgi
import os
import subprocess

CONF_FILE = "/path/to/grueneeule-urlshortener/redirects.conf"
LOG_FILE = "/path/to/grueneeule-urlshortener/logs/shortener.log"

print("Content-Type: text/html\n")

form = cgi.FieldStorage()
short_name = form.getfirst("short_name", "").strip()
original_url = form.getfirst("original_url", "").strip()

# Validierung
if not short_name or not original_url:
    print("<p>Fehler: Alle Felder ausfüllen!</p>")
    exit()

if not short_name.isalnum() and not all(c in "-_" for c in short_name):
    print("<p>Fehler: Kurzname darf nur Buchstaben, Zahlen, - oder _ enthalten!</p>")
    exit()

# Prüfen, ob schon vorhanden
if os.path.exists(CONF_FILE):
    with open(CONF_FILE, "r") as f:
        if f"/ol/{short_name}" in f.read():
            print(f"<p>Fehler: {short_name} existiert bereits!</p>")
            exit()

# Eintrag hinzufügen
with open(CONF_FILE, "a") as f:
    f.write(f"\nlocation = /ol/{short_name} {{\n    return 302 {original_url};\n}}\n")

# Log schreiben
with open(LOG_FILE, "a") as f:
    f.write(f"{short_name} -> {original_url}\n")

# Nginx reload
result = subprocess.run(["sudo", "nginx", "-s", "reload"], capture_output=True, text=True)
if result.returncode != 0:
    print(f"<p>Fehler beim Nginx reload: {result.stderr}</p>")
else:
    print(f"<p>Link erstellt: <a href='/ol/{short_name}'>owlink.grueneeule.de/ol/{short_name}</a></p>")
