#!/usr/bin/env python3
"""
📁 Google Drive Tool pour PydanticAI
Rechercher et lire des documents Google Docs et fichiers texte (en lecture seule)
"""

import os
import io
from typing import Optional
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive.readonly"
]

def get_drive_service():
    """Obtient le service Google Drive v3 avec authentification OAuth2"""
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if refresh_token and client_id and client_secret:
        try:
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=SCOPES
            )
            creds.refresh(Request())
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"⚠️ Erreur initialisation Drive via refresh_token: {e}")

    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"⚠️ Erreur token.json Drive: {e}")

    return None

def search_drive(query: str, max_results: int = 5) -> str:
    """Recherche des fichiers dans Google Drive par mot-clé dans le titre ou le contenu"""
    service = get_drive_service()
    if service is None:
        return "❌ Service Google Drive non connecté. GOOGLE_REFRESH_TOKEN non configuré."

    try:
        q = f"name contains '{query}' and trashed = false"
        results = service.files().list(
            q=q,
            pageSize=max_results,
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()

        files = results.get("files", [])
        if not files:
            return f"📁 Aucun fichier trouvé dans Drive pour '{query}'."

        output = f"📁 **Fichiers Google Drive trouvés ({len(files)}) :**\n\n"
        for f in files:
            output += f"• **{f['name']}**\n  ID : `{f['id']}`\n  Type : {f['mimeType']}\n  Modifié : {f.get('modifiedTime', 'N/A')}\n\n"

        return output.strip()
    except Exception as e:
        return f"❌ Erreur recherche Google Drive : {str(e)}"

def read_drive_file(file_id: str) -> str:
    """Lit le contenu d'un Google Doc ou fichier texte à partir de son ID"""
    service = get_drive_service()
    if service is None:
        return "❌ Service Google Drive non connecté. GOOGLE_REFRESH_TOKEN non configuré."

    try:
        # Récupérer les métadonnées pour connaître le mimeType
        meta = service.files().get(fileId=file_id, fields="id, name, mimeType").execute()
        mime_type = meta.get("mimeType", "")
        file_name = meta.get("name", file_id)

        # Cas 1 : Document Google Docs -> Export en texte brut
        if mime_type == "application/vnd.google-apps.document":
            request = service.files().export_media(fileId=file_id, mimeType="text/plain")
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            content = fh.getvalue().decode("utf-8", errors="replace")
            return f"📄 **Contenu du Google Doc « {file_name} » :**\n\n{content}"

        # Cas 2 : Fichier texte / markdown brut
        elif "text/" in mime_type or mime_type in ["application/json", "application/javascript"]:
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            content = fh.getvalue().decode("utf-8", errors="replace")
            return f"📄 **Contenu du fichier « {file_name} » :**\n\n{content}"

        else:
            return f"⚠️ Le fichier « {file_name} » est de type `{mime_type}`, non lisible directement en texte brut."
    except Exception as e:
        return f"❌ Erreur lecture fichier Drive : {str(e)}"

# Fonctions outils exportées
def search_drive_tool(query: str, max_results: int = 5) -> str:
    """Recherche des fichiers et documents dans Google Drive"""
    return search_drive(query, max_results)

def read_drive_file_tool(file_id: str) -> str:
    """Lit le contenu textuel d'un Google Doc ou fichier texte Drive"""
    return read_drive_file(file_id)

if __name__ == "__main__":
    print(search_drive("test"))
