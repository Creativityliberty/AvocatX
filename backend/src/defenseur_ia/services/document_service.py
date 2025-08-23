"""
Service de gestion des documents pour DEFENSEUR-IA
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import UploadFile
import os
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service de gestion des documents et fichiers uploadés
    """
    
    def __init__(self, upload_dir: str = "./uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
    async def save_uploaded_file(self, file: UploadFile, case_id: str) -> Dict[str, Any]:
        """
        Sauvegarde un fichier uploadé et retourne ses métadonnées
        """
        try:
            # Créer le dossier pour ce case
            case_dir = self.upload_dir / case_id
            case_dir.mkdir(exist_ok=True)
            
            # Lire le contenu du fichier
            content = await file.read()
            
            # Calculer le hash
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Sauvegarder le fichier
            file_path = case_dir / file.filename
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Retourner les métadonnées
            return {
                "filename": file.filename,
                "size": len(content),
                "hash": file_hash,
                "path": str(file_path),
                "content_type": file.content_type
            }
            
        except Exception as e:
            logger.error(f"Error saving file {file.filename}: {e}")
            raise
    
    async def list_case_files(self, case_id: str) -> List[Dict[str, Any]]:
        """
        Liste tous les fichiers d'un dossier
        """
        case_dir = self.upload_dir / case_id
        if not case_dir.exists():
            return []
        
        files = []
        for file_path in case_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "path": str(file_path)
                })
        
        return files
    
    async def delete_file(self, case_id: str, filename: str) -> bool:
        """
        Supprime un fichier d'un dossier
        """
        try:
            file_path = self.upload_dir / case_id / filename
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return False
