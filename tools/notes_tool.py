#!/usr/bin/env python3
"""
📝 Notes Tool pour PydanticAI
Gestion de notes avec stockage SQLite persistant
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class NotesTool:
    """Outil de gestion de notes avec stockage SQLite"""
    
    def __init__(self, db_path: str = "kwame_notes.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialise la base de données SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                category TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS note_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Catégories par défaut
        cursor.execute('''
            INSERT OR IGNORE INTO note_categories (name, description) VALUES 
            ('general', 'Notes generales'),
            ('work', 'Notes professionnelles'),
            ('personal', 'Notes personnelles'),
            ('ideas', 'Idees et inspiration'),
            ('todo', 'Taches a faire'),
            ('learning', 'Notes d apprentissage')
        ''')
        
        conn.commit()
        conn.close()
    
    def save_note(self, title: str, content: str, tags: str = "", category: str = "general") -> Dict:
        """Sauvegarde une nouvelle note"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notes (title, content, tags, category, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (title, content, tags, category))
        
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Note '{title}' sauvegardée avec succès",
            "note_id": note_id,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
    
    def list_notes(self, limit: int = 20, category: str = None) -> Dict:
        """Liste toutes les notes avec filtre optionnel par catégorie"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT id, title, content, tags, category, created_at, updated_at
                FROM notes
                WHERE category = ?
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (category, limit))
        else:
            cursor.execute('''
                SELECT id, title, content, tags, category, created_at, updated_at
                FROM notes
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (limit,))
        
        notes = []
        for row in cursor.fetchall():
            notes.append({
                "id": row[0],
                "title": row[1],
                "content": row[2][:200] + "..." if len(row[2]) > 200 else row[2],
                "tags": row[3],
                "category": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            })
        
        conn.close()
        
        return {
            "success": True,
            "notes": notes,
            "total": len(notes),
            "category_filter": category
        }
    
    def search_notes(self, keyword: str, category: str = None) -> Dict:
        """Recherche des notes par mot-clé avec filtre optionnel par catégorie"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT id, title, content, tags, category, created_at, updated_at
                FROM notes
                WHERE (title LIKE ? OR content LIKE ? OR tags LIKE ?)
                AND category = ?
                ORDER BY updated_at DESC
            ''', (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", category))
        else:
            cursor.execute('''
                SELECT id, title, content, tags, category, created_at, updated_at
                FROM notes
                WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                ORDER BY updated_at DESC
            ''', (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        
        notes = []
        for row in cursor.fetchall():
            notes.append({
                "id": row[0],
                "title": row[1],
                "content": row[2][:200] + "..." if len(row[2]) > 200 else row[2],
                "tags": row[3],
                "category": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            })
        
        conn.close()
        
        return {
            "success": True,
            "keyword": keyword,
            "notes": notes,
            "total": len(notes),
            "category_filter": category
        }
    
    def get_note(self, note_id: int) -> Dict:
        """Récupère une note spécifique"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, tags, category, created_at, updated_at
            FROM notes
            WHERE id = ?
        ''', (note_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "success": True,
                "note": {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "tags": row[3],
                    "category": row[4],
                    "created_at": row[5],
                    "updated_at": row[6]
                }
            }
        else:
            return {
                "success": False,
                "message": f"Note avec ID {note_id} non trouvée"
            }
    
    def update_note(self, note_id: int, title: str = None, content: str = None, tags: str = None, category: str = None) -> Dict:
        """Met à jour une note existante"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Vérifier si la note existe
        cursor.execute('SELECT id FROM notes WHERE id = ?', (note_id,))
        if not cursor.fetchone():
            conn.close()
            return {
                "success": False,
                "message": f"Note avec ID {note_id} non trouvée"
            }
        
        # Construire la requête de mise à jour
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        if tags is not None:
            updates.append("tags = ?")
            params.append(tags)
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(note_id)
        
        cursor.execute(f'''
            UPDATE notes 
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Note ID {note_id} mise à jour avec succès",
            "timestamp": datetime.now().isoformat()
        }
    
    def delete_note(self, note_id: int) -> Dict:
        """Supprime une note"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        deleted_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_rows > 0:
            return {
                "success": True,
                "message": f"Note ID {note_id} supprimée avec succès"
            }
        else:
            return {
                "success": False,
                "message": f"Note avec ID {note_id} non trouvée"
            }
    
    def list_categories(self) -> Dict:
        """Liste toutes les catégories disponibles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, description, created_at
            FROM note_categories
            ORDER BY name
        ''')
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                "name": row[0],
                "description": row[1],
                "created_at": row[2]
            })
        
        conn.close()
        
        return {
            "success": True,
            "categories": categories,
            "total": len(categories)
        }
    
    def get_stats(self) -> Dict:
        """Obtient des statistiques sur les notes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Nombre total de notes
        cursor.execute('SELECT COUNT(*) FROM notes')
        total_notes = cursor.fetchone()[0]
        
        # Notes par catégorie
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM notes
            GROUP BY category
            ORDER BY count DESC
        ''')
        notes_by_category = dict(cursor.fetchall())
        
        # Notes créées aujourd'hui
        cursor.execute('''
            SELECT COUNT(*) FROM notes 
            WHERE DATE(created_at) = DATE('now')
        ''')
        today_notes = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "total_notes": total_notes,
            "notes_by_category": notes_by_category,
            "today_notes": today_notes,
            "database_path": self.db_path
        }

# Fonctions pour PydanticAI
def save_note(title: str, content: str, tags: str = "", category: str = "general") -> str:
    """
    Sauvegarde une nouvelle note dans la base de données.
    
    Args:
        title: Titre de la note
        content: Contenu de la note
        tags: Tags séparés par des virgules (optionnel)
        category: Catégorie de la note (défaut: general)
        
    Returns:
        Message de confirmation avec l'ID de la note créée
    """
    tool = NotesTool()
    result = tool.save_note(title, content, tags, category)
    
    if result["success"]:
        return f"✅ {result['message']} (ID: {result['note_id']})\n📂 Catégorie: {result['category']}\n🕐 Créée le: {result['timestamp']}"
    else:
        return f"❌ Erreur: {result.get('message', 'Erreur inconnue')}"

def list_notes(limit: int = 20, category: str = None) -> str:
    """
    Liste toutes les notes avec filtre optionnel par catégorie.
    
    Args:
        limit: Nombre maximum de notes à afficher (défaut: 20)
        category: Filtrer par catégorie spécifique (optionnel)
        
    Returns:
        Liste formatée des notes avec ID, titre, catégorie et date
    """
    tool = NotesTool()
    result = tool.list_notes(limit, category)
    
    if result["success"]:
        if result["notes"]:
            output = f"📝 **Notes trouvées ({result['total']} résultats)"
            if result["category_filter"]:
                output += f" dans la catégorie '{result['category_filter']}'"
            output += ":\n\n"
            
            for note in result["notes"]:
                output += f"**ID {note['id']}: {note['title']}**\n"
                output += f"📂 Catégorie: {note['category']}\n"
                output += f"🏷️ Tags: {note['tags'] or 'Aucun'}\n"
                output += f"📄 Contenu: {note['content']}\n"
                output += f"🕐 Mis à jour: {note['updated_at']}\n\n"
            
            return output
        else:
            if result["category_filter"]:
                return f"📝 Aucune note trouvée dans la catégorie '{result['category_filter']}'."
            else:
                return "📝 Aucune note trouvée. Utilisez save_note() pour créer votre première note."
    else:
        return f"❌ Erreur: {result.get('message', 'Erreur inconnue')}"

def search_notes(keyword: str, category: str = None) -> str:
    """
    Recherche des notes par mot-clé avec filtre optionnel par catégorie.
    
    Args:
        keyword: Mot-clé à rechercher
        category: Limiter la recherche à une catégorie (optionnel)
        
    Returns:
        Liste des notes contenant le mot-clé
    """
    tool = NotesTool()
    result = tool.search_notes(keyword, category)
    
    if result["success"]:
        if result["notes"]:
            output = f"🔍 **Résultats pour '{keyword}' ({result['total']} notes)"
            if result["category_filter"]:
                output += f" dans la catégorie '{result['category_filter']}'"
            output += ":\n\n"
            
            for note in result["notes"]:
                output += f"**ID {note['id']}: {note['title']}**\n"
                output += f"📂 Catégorie: {note['category']}\n"
                output += f"🏷️ Tags: {note['tags'] or 'Aucun'}\n"
                output += f"📄 Contenu: {note['content']}\n"
                output += f"🕐 Mis à jour: {note['updated_at']}\n\n"
            
            return output
        else:
            if result["category_filter"]:
                return f"🔍 Aucune note trouvée pour '{keyword}' dans la catégorie '{result['category_filter']}'."
            else:
                return f"🔍 Aucune note trouvée pour '{keyword}'."
    else:
        return f"❌ Erreur: {result.get('message', 'Erreur inconnue')}"

def get_note(note_id: int) -> str:
    """
    Récupère une note spécifique par son ID.
    
    Args:
        note_id: ID numérique de la note
        
    Returns:
        Contenu complet de la note
    """
    tool = NotesTool()
    result = tool.get_note(note_id)
    
    if result["success"]:
        note = result["note"]
        output = f"📄 **Note ID {note['id']}: {note['title']}**\n\n"
        output += f"📂 Catégorie: {note['category']}\n"
        output += f"🏷️ Tags: {note['tags'] or 'Aucun'}\n"
        output += f"📅 Créée le: {note['created_at']}\n"
        output += f"🕐 Mis à jour: {note['updated_at']}\n\n"
        output += f"📝 **Contenu:**\n{note['content']}"
        
        return output
    else:
        return f"❌ {result.get('message', 'Erreur inconnue')}"

def update_note(note_id: int, title: str = None, content: str = None, tags: str = None, category: str = None) -> str:
    """
    Met à jour une note existante.
    
    Args:
        note_id: ID de la note à mettre à jour
        title: Nouveau titre (optionnel)
        content: Nouveau contenu (optionnel)
        tags: Nouveaux tags (optionnel)
        category: Nouvelle catégorie (optionnel)
        
    Returns:
        Message de confirmation de la mise à jour
    """
    tool = NotesTool()
    result = tool.update_note(note_id, title, content, tags, category)
    
    if result["success"]:
        return f"✅ {result['message']} (Mis à jour le: {result['timestamp']})"
    else:
        return f"❌ {result.get('message', 'Erreur inconnue')}"

def delete_note(note_id: int) -> str:
    """
    Supprime une note par son ID.
    
    Args:
        note_id: ID de la note à supprimer
        
    Returns:
        Message de confirmation de la suppression
    """
    tool = NotesTool()
    result = tool.delete_note(note_id)
    
    if result["success"]:
        return f"✅ {result['message']}"
    else:
        return f"❌ {result.get('message', 'Erreur inconnue')}"

def list_categories() -> str:
    """
    Liste toutes les catégories de notes disponibles.
    
    Returns:
        Liste des catégories avec descriptions
    """
    tool = NotesTool()
    result = tool.list_categories()
    
    if result["success"]:
        output = f"📂 **Catégories disponibles ({result['total']}):**\n\n"
        
        for cat in result["categories"]:
            output += f"📁 **{cat['name']}**\n"
            output += f"   📝 {cat['description']}\n"
            output += f"   🕐 Créée le: {cat['created_at']}\n\n"
        
        return output
    else:
        return f"❌ Erreur: {result.get('message', 'Erreur inconnue')}"

def get_notes_stats() -> str:
    """
    Affiche des statistiques sur les notes.
    
    Returns:
        Statistiques détaillées sur les notes
    """
    tool = NotesTool()
    result = tool.get_stats()
    
    if result["success"]:
        output = f"📊 **Statistiques des notes:**\n\n"
        output += f"📝 **Total des notes:** {result['total_notes']}\n"
        output += f"📅 **Notes aujourd'hui:** {result['today_notes']}\n"
        output += f"💾 **Base de données:** {result['database_path']}\n\n"
        
        output += "📂 **Notes par catégorie:**\n"
        for category, count in result["notes_by_category"].items():
            output += f"   📁 {category}: {count} notes\n"
        
        return output
    else:
        return f"❌ Erreur: {result.get('message', 'Erreur inconnue')}"

if __name__ == "__main__":
    # Test de l'outil
    print("📝 Test Notes Tool")
    print("=" * 40)
    
    # Test sauvegarde
    print("Test sauvegarde note:")
    print(save_note("Test Note", "Ceci est une note de test", "test,demo", "general"))
    
    # Test liste
    print("\nTest liste notes:")
    print(list_notes())
    
    # Test recherche
    print("\nTest recherche notes:")
    print(search_notes("test"))
    
    # Test catégories
    print("\nTest catégories:")
    print(list_categories())
    
    print("\n✅ Tests terminés!")
