#!/usr/bin/env python3
"""
Script para descargar la fuente Hack Nerd Font desde GitHub
"""
import os
import requests
import zipfile
import tempfile
from pathlib import Path

def download_hack_nerd_font():
    """Descarga la fuente Hack Nerd Font desde GitHub"""
    url = "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/Hack.zip"
    
    # Crear directorio fonts si no existe
    fonts_dir = Path("fonts")
    fonts_dir.mkdir(exist_ok=True)
    
    print("Descargando Hack Nerd Font...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Descargar a archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_path = temp_file.name
        
        print("Extrayendo archivos de fuente...")
        
        # Extraer solo los archivos .ttf
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith('.ttf'):
                    file_info.filename = os.path.basename(file_info.filename)
                    zip_ref.extract(file_info, fonts_dir)
                    print(f"Extraído: {file_info.filename}")
        
        # Limpiar archivo temporal
        os.unlink(temp_path)
        
        print(f"Fuentes descargadas exitosamente en: {fonts_dir.absolute()}")
        return True
        
    except Exception as e:
        print(f"Error descargando fuente: {e}")
        return False

if __name__ == "__main__":
    download_hack_nerd_font()