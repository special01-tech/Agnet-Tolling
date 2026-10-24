#!/usr/bin/env python3
"""
📝 Notion Tool pour PydanticAI
Rechercher, lire, créer une page et ajouter du contenu via l'API officielle Notion
"""

import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class NotionTool:
    """Outil d'interaction avec Notion via l'API REST officielle"""

    def __init__(self):
        self.api_key = (os.getenv("NOTION_API_KEY") or "").strip()
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    def _check_key(self) -> Optional[str]:
        if not self.api_key or self.api_key.startswith("secret_votre_"):
            return "❌ NOTION_API_KEY non configurée dans .env. Veuillez ajouter une clé d'intégration Notion valide."
        return None

    def search(self, query: str = "", page_size: int = 5) -> str:
        """Recherche des pages et bases de données Notion"""
        err = self._check_key()
        if err:
            return err

        try:
            url = f"{self.base_url}/search"
            payload = {
                "query": query,
                "page_size": page_size,
                "sort": {"direction": "descending", "timestamp": "last_edited_time"}
            }
            resp = requests.post(url, headers=self.headers, json=payload, timeout=15)
            if resp.status_code != 200:
                return f"❌ Erreur Notion ({resp.status_code}) : {resp.text}"

            results = resp.json().get("results", [])
            if not results:
                return f"🔍 Aucune page trouvée pour la recherche '{query}'."

            output = f"📚 **Pages Notion trouvées ({len(results)}) :**\n\n"
            for r in results:
                title = "Sans titre"
                props = r.get("properties", {})
                for p in props.values():
                    if p.get("type") == "title" and p.get("title"):
                        title = "".join([t.get("plain_text", "") for t in p["title"]])
                        break
                page_id = r.get("id")
                url_link = r.get("url", "")
                output += f"• **{title}**\n  ID : `{page_id}`\n  URL : {url_link}\n\n"

            return output.strip()
        except Exception as e:
            return f"❌ Erreur recherche Notion : {str(e)}"

    def read_page(self, page_id: str) -> str:
        """Lit les blocs de texte d'une page Notion"""
        err = self._check_key()
        if err:
            return err

        clean_id = page_id.replace("-", "").strip()
        try:
            url = f"{self.base_url}/blocks/{clean_id}/children"
            resp = requests.get(url, headers=self.headers, timeout=15)
            if resp.status_code != 200:
                return f"❌ Erreur lecture page Notion ({resp.status_code}) : {resp.text}"

            blocks = resp.json().get("results", [])
            if not blocks:
                return "📄 La page Notion est vide ou aucun bloc textuel n'a été trouvé."

            lines = []
            for b in blocks:
                b_type = b.get("type")
                content_obj = b.get(b_type, {})
                rich_texts = content_obj.get("rich_text", [])
                text = "".join([t.get("plain_text", "") for t in rich_texts])
                if text:
                    if b_type.startswith("heading"):
                        lines.append(f"\n### {text}")
                    elif b_type == "bulleted_list_item":
                        lines.append(f"• {text}")
                    elif b_type == "numbered_list_item":
                        lines.append(f"1. {text}")
                    elif b_type == "to_do":
                        checked = "x" if content_obj.get("checked") else " "
                        lines.append(f"- [{checked}] {text}")
                    else:
                        lines.append(text)

            return f"📄 **Contenu de la page Notion (`{clean_id}`) :**\n\n" + "\n".join(lines)
        except Exception as e:
            return f"❌ Erreur lecture Notion : {str(e)}"

    def create_page(self, title: str, content: str = "", parent_page_id: Optional[str] = None) -> str:
        """Crée une nouvelle page Notion"""
        err = self._check_key()
        if err:
            return err

        try:
            url = f"{self.base_url}/pages"
            # Si aucun parent_page_id n'est fourni, on cherche la première page accessible pour s'y rattacher
            if not parent_page_id:
                search_resp = requests.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json={"page_size": 1, "filter": {"value": "page", "property": "object"}},
                    timeout=10
                )
                if search_resp.status_code == 200 and search_resp.json().get("results"):
                    parent_page_id = search_resp.json()["results"][0]["id"]
                else:
                    return "❌ Erreur : Impossible de créer une page sans page parente accessible. Renseignez un `parent_page_id` ou partagez une page avec l'intégration."

            clean_parent = parent_page_id.replace("-", "").strip()
            payload = {
                "parent": {"page_id": clean_parent},
                "properties": {
                    "title": {
                        "title": [{"type": "text", "text": {"content": title}}]
                    }
                },
                "children": []
            }
            if content:
                # Découper par paragraphes
                paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
                for p in paragraphs:
                    payload["children"].append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": p}}]
                        }
                    })

            resp = requests.post(url, headers=self.headers, json=payload, timeout=15)
            if resp.status_code != 200:
                return f"❌ Erreur création page Notion ({resp.status_code}) : {resp.text}"

            created = resp.json()
            new_id = created.get("id")
            new_url = created.get("url")
            return f"✅ Page Notion créée avec succès !\n• Titre : **{title}**\n• ID : `{new_id}`\n• URL : {new_url}"
        except Exception as e:
            return f"❌ Erreur création Notion : {str(e)}"

    def append_content(self, page_id: str, content: str) -> str:
        """Ajoute des blocs de texte à la fin d'une page Notion existante"""
        err = self._check_key()
        if err:
            return err

        clean_id = page_id.replace("-", "").strip()
        try:
            url = f"{self.base_url}/blocks/{clean_id}/children"
            paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
            children = []
            for p in paragraphs:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": p}}]
                    }
                })

            resp = requests.patch(url, headers=self.headers, json={"children": children}, timeout=15)
            if resp.status_code != 200:
                return f"❌ Erreur ajout contenu Notion ({resp.status_code}) : {resp.text}"

            return f"✅ Contenu ajouté avec succès à la page Notion `{clean_id}` !"
        except Exception as e:
            return f"❌ Erreur ajout contenu Notion : {str(e)}"

# Fonctions d'outils exportées
def search_notion_tool(query: str = "") -> str:
    """Recherche des pages dans Notion par mot-clé"""
    return NotionTool().search(query)

def read_notion_page_tool(page_id: str) -> str:
    """Lit le texte d'une page Notion à partir de son ID"""
    return NotionTool().read_page(page_id)

def create_notion_page_tool(title: str, content: str = "", parent_page_id: str = "") -> str:
    """Crée une nouvelle page Notion avec titre et contenu optionnel"""
    return NotionTool().create_page(title, content, parent_page_id or None)

def append_to_notion_page_tool(page_id: str, content: str) -> str:
    """Ajoute du texte à une page Notion existante"""
    return NotionTool().append_content(page_id, content)

if __name__ == "__main__":
    print(search_notion_tool("test"))
