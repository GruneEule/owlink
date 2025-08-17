#!/usr/bin/env python3
import os
from urllib.parse import parse_qs
import qrcode
import io
import base64

CONF_FILE = "/var/www/web/owlink/redirects.conf"
LOG_FILE = "/var/www/web/owlink/shortener.log"
QR_CODE_DIR = "/var/www/web/owlink/qrcodes"  # Stellen Sie sicher, dass dieses Verzeichnis existiert

def application(environ, start_response):
    try:
        if environ["PATH_INFO"] == "/api/shorten" and environ["REQUEST_METHOD"] == "POST":
            # Existierender Shortener Code bleibt unverändert
            try:
                request_body_size = int(environ.get("CONTENT_LENGTH", 0))
            except ValueError:
                request_body_size = 0

            request_body = environ["wsgi.input"].read(request_body_size).decode("utf-8")
            params = parse_qs(request_body)

            short_name = params.get("short_name", [""])[0].strip()
            original_url = params.get("original_url", [""])[0].strip()

            # Validierung
            if not short_name or not original_url:
                return _response(start_response, 400, "Fehler: Alle Felder ausfüllen!")

            if not all(c.isalnum() or c in "-_" for c in short_name):
                return _response(start_response, 400, "Fehler: Kurzname darf nur Buchstaben, Zahlen, - oder _ enthalten!")

            # Prüfen, ob schon vorhanden
            if os.path.exists(CONF_FILE):
                with open(CONF_FILE, "r") as f:
                    if f"/{short_name}" in f.read():
                        return _response(start_response, 400, f"Fehler: {short_name} existiert bereits!")

            # Eintrag hinzufügen
            with open(CONF_FILE, "a") as f:
                f.write(f"\nlocation = /{short_name} {{\n    return 302 {original_url};\n}}\n")

            # Log schreiben
            with open(LOG_FILE, "a") as f:
                f.write(f"{short_name} -> {original_url}\n")

            # Nginx reload
            os.system("sudo nginx -s reload")

            return _response(start_response, 200, f"Link erstellt: /{short_name}")

        elif environ["PATH_INFO"] == "/api/qrcode" and environ["REQUEST_METHOD"] == "POST":
            try:
                request_body_size = int(environ.get("CONTENT_LENGTH", 0))
            except ValueError:
                request_body_size = 0

            request_body = environ["wsgi.input"].read(request_body_size).decode("utf-8")
            params = parse_qs(request_body)
            url = params.get("url", [""])[0].strip()

            if not url:
                return _response(start_response, 400, "Fehler: URL darf nicht leer sein!")

            # QR Code generieren
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # QR Code in Bytes speichern
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            qr_code_data = buffer.getvalue()

            # Base64 für direkte Einbindung in HTML
            qr_code_base64 = base64.b64encode(qr_code_data).decode('utf-8')

            # QR Code speichern (optional)
            if not os.path.exists(QR_CODE_DIR):
                os.makedirs(QR_CODE_DIR)

            filename = f"qr_{hash(url)}.png"
            filepath = os.path.join(QR_CODE_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(qr_code_data)

            headers = [
                ("Content-Type", "application/json"),
                ("Content-Disposition", f"attachment; filename={filename}")
            ]
            start_response("200 OK", headers)

            return [qr_code_data]

        else:
            return _response(start_response, 404, "Not Found")

    except Exception as e:
        return _response(start_response, 500, f"Fehler: {e}")


def _response(start_response, status_code, message):
    status = f"{status_code} {'OK' if status_code == 200 else 'ERROR'}"
    headers = [("Content-Type", "text/plain; charset=utf-8")]
    start_response(status, headers)
    return [message.encode("utf-8")]