"""Da lanciare UNA volta sul tuo computer: ti fa accedere con Google e stampa il refresh token per YT_REFRESH_TOKEN.

    python youtube_auth.py --client-id XXX --client-secret YYY

Usa solo la libreria standard. Accedi con l'account Google che gestisce il canale
(se il canale è un brand account, sceglilo quando Google te lo chiede).
Il token stampato va messo nelle variabili d'ambiente dell'ambiente cloud, mai in chat.
"""

import argparse
import http.server
import json
import socket
import urllib.parse
import urllib.request
import webbrowser

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/youtube.upload"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--client-secret", required=True)
    args = ap.parse_args()

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    redirect = f"http://127.0.0.1:{port}"
    url = AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": args.client_id, "redirect_uri": redirect, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent",
    })

    code = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code["value"] = q.get("code", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Fatto, puoi chiudere questa pagina e tornare al terminale.".encode())

        def log_message(self, *a):
            pass

    print("Si apre il browser per l'accesso. Se non si apre, copia questo link:\n" + url + "\n")
    webbrowser.open(url)
    with http.server.HTTPServer(("127.0.0.1", port), Handler) as srv:
        while "value" not in code:
            srv.handle_request()
    if not code["value"]:
        raise SystemExit("Accesso annullato o negato.")

    data = urllib.parse.urlencode({
        "code": code["value"], "client_id": args.client_id, "client_secret": args.client_secret,
        "redirect_uri": redirect, "grant_type": "authorization_code",
    }).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=data)) as r:
        tok = json.load(r)
    if "refresh_token" not in tok:
        raise SystemExit(f"Nessun refresh token nella risposta: {tok}")
    print("Refresh token (mettilo in YT_REFRESH_TOKEN nelle impostazioni dell'ambiente, NON in chat):\n")
    print(tok["refresh_token"])


if __name__ == "__main__":
    main()
