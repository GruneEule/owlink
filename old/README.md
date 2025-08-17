# OwLink - URL Shortener

OwLink ist ein selbstgebauter URL-Shortener unter owlink.grueneeule.de, komplett in Python (ohne Flask) mit NGINX-Hosting und CGI.

---

## Features

- Kürzt URLs zu `owlink.grueneeule.de/ol/<kurzname>`
- Prüft, ob Kurzname schon existiert
- Speichert Logs unter `/logs/shortener.log`
- Automatisches NGINX Reload bei neuen Links
- Keine externe Bibliothek erforderlich

---

## Ordnerstruktur

```
grueneeule-urlshortener/
├─ logs/
│  └─ shortener.log
├─ src/
│  ├─ assets/
│  │  └─ css/
│  │     └─ main.css
│  └─ index.html
├─ redirects.conf
└─ shortener.py
````

---

## Installation

1. Repo klonen:

```bash
git clone https://github.com/GruneEule/owlink.git /var/www/web/owlink
cd /var/www/web/owlink
````

2. Berechtigungen setzen:

```bash
chmod +x shortener.py
chown www-data:www-data shortener.py redirects.conf logs/shortener.log
```

3. NGINX sicherstellen, dass `fcgiwrap` installiert ist:

```bash
sudo apt install fcgiwrap
```

4. NGINX konfigurieren (aus `nginx.conf`):

* Root auf `/var/www/web/owlink/src`
* CGI-Pfad `/shortener.py` über `fcgiwrap`
* Weiterleitungen über `/redirects.conf`

5. OwLink ist jetzt unter `https://owlink.grueneeule.de` erreichbar.

---

## Nutzung

* Öffne das Web-Interface (`index.html`)
* Gib lange URL ein und wähle einen Kurzname
* Klick auf „Kürzen“
* Kurzname wird geprüft und in `redirects.conf` eingetragen
* NGINX wird automatisch neu geladen
* Zugriff auf gekürzte URL: `https://owlink.grueneeule.de/ol/<kurzname>`

---

## Hinweise

* `shortener.py` läuft als CGI-Skript, alle Logs gehen nach `/logs/shortener.log`
* Nur alphanumerische Kurz-Namen, `-` und `_` erlaubt
* Bei NGINX Reload Fehler: Stelle sicher, dass `sudo` ohne Passwort für den Reload erlaubt ist:

```bash
sudo visudo
# Dann hinzufügen:
www-data ALL=(ALL) NOPASSWD: /usr/sbin/nginx -s reload
```