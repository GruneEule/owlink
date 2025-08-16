# OwLink - GrüneEule URL Shortener

OwLink ist ein einfacher URL-Shortener, der unter `owlink.grueneeule.de` läuft. Jeder kann eine URL kürzen und einen eigenen Kurzlink wählen. Das System nutzt **Python (CGI)** und **NGINX**, kein Flask oder andere Frameworks.

---

## **Installation / Setup**

1. **Repo klonen**

```bash
git clone https://github.com/GruneEule/owlink.git grueneeule-urlshortener
cd grueneeule-urlshortener
```

2. **Leere Konfigurations- und Log-Dateien anlegen**

```bash
touch redirects.conf
touch logs/shortener.log
```

3. **Python-Skript ausführbar machen**

```bash
chmod +x shortener.py
```

4. **NGINX konfigurieren**

* Erstelle eine NGINX-Serverblock-Datei z. B. `/etc/nginx/sites-available/owlink.grueneeule.de.conf`:

```nginx
server {
    listen 80;
    server_name owlink.grueneeule.de;

    root /path/to/grueneeule-urlshortener/src;
    index index.html;

    location /shortener.py {
        fastcgi_pass unix:/var/run/fcgiwrap.socket;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME /path/to/grueneeule-urlshortener/shortener.py;
    }

    include /path/to/grueneeule-urlshortener/redirects.conf;
}
```

> Ersetze `/path/to/grueneeule-urlshortener/` durch den Pfad, wo du das Repo geklont hast.

5. **NGINX aktivieren**

```bash
sudo ln -s /etc/nginx/sites-available/owlink.grueneeule.de.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

6. **FCGIWrap installieren** (falls noch nicht vorhanden, notwendig für Python CGI):

```bash
sudo apt install fcgiwrap
sudo systemctl enable --now fcgiwrap
```

---

## **Benutzung**

1. Besuche `http://owlink.grueneeule.de`.
2. Gib die lange URL und den gewünschten Kurzlink ein.
3. Wenn der Kurzlink noch nicht existiert, wird er automatisch in `redirects.conf` eingetragen und NGINX reloadet.
4. Der Kurzlink ist sofort unter `owlink.grueneeule.de/ol/<kurzname>` erreichbar.

---

## **Ordnerstruktur**

```
grueneeule-urlshortener/
├── logs/
│   └── shortener.log
├── src/
│   ├── assets/
│   │   └── css/
│   │       └── main.css
│   └── index.html
├── redirects.conf
└── shortener.py
```