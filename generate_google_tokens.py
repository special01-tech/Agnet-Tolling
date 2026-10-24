#!/usr/bin/env python3
"""
🔐 Générateur de jeton de rafraîchissement Google OAuth2 (Calendar & Drive)
Ouvre le navigateur pour autoriser l'accès et extrait GOOGLE_REFRESH_TOKEN
"""

import os
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]

def main():
    print("=" * 65, flush=True)
    print("🔑 GÉNÉRATION DU JETON GOOGLE OAUTH2 (CALENDAR, DRIVE & GMAIL API)", flush=True)
    print("=" * 65, flush=True)

    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    # Si credentials.json existe, on l'utilise, sinon on construit la config à partir du .env
    if os.path.exists("credentials.json"):
        print("📄 Lecture de credentials.json...", flush=True)
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    elif client_id and client_secret:
        print("⚙️ Configuration OAuth 2.0 (compatible Web et Desktop)...", flush=True)
        # Structure supportant les clients de type Web et Desktop
        client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [
                    "http://localhost:8080/",
                    "http://localhost:8080",
                    "http://127.0.0.1:8080/",
                    "http://localhost"
                ]
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        flow.redirect_uri = "http://localhost:8080/"
    else:
        print("❌ Erreur : Ni credentials.json ni les variables GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET ne sont disponibles.", flush=True)
        sys.exit(1)

    print("\n🌐 Un onglet de votre navigateur va s'ouvrir pour vous connecter.", flush=True)
    print("👉 Connectez-vous avec votre compte Google et acceptez les autorisations (Calendar & Drive).", flush=True)
    print("⏳ En attente de l'autorisation dans le navigateur...\n", flush=True)

    # Lance le serveur local sur le port fixe 8080 pour correspondre exactement à l'URI de redirection
    creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")

    refresh_token = creds.refresh_token
    if not refresh_token:
        print("⚠️ Attention : Aucun refresh_token retourné (le compte a peut-être déjà autorisé l'application).")
    else:
        print("\n" + "🎉" * 25)
        print("✅ AUTHENTIFICATION RÉUSSIE !")
        print("=" * 65)
        print("Voici votre GOOGLE_REFRESH_TOKEN :")
        print(refresh_token)
        print("=" * 65)

        # Enregistrement automatique dans .env
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                content = f.read()
            if "GOOGLE_REFRESH_TOKEN=" in content:
                lines = content.splitlines()
                new_lines = [
                    f"GOOGLE_REFRESH_TOKEN={refresh_token}" if l.startswith("GOOGLE_REFRESH_TOKEN=") else l 
                    for l in lines
                ]
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines) + "\n")
            else:
                with open(env_path, "a", encoding="utf-8") as f:
                    f.write(f"\nGOOGLE_REFRESH_TOKEN={refresh_token}\n")
            print("💾 Le jeton a également été sauvegardé automatiquement dans votre fichier .env !")

if __name__ == "__main__":
    main()
