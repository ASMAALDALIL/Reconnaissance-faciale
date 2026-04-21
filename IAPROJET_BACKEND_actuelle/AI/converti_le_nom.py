import os
import unicodedata
import re

# Dossier contenant tes images
dataset_dir = r"C:\Users\ASMAA\OneDrive\Desktop\IA project\dataset\justin_bieber"

# Fonction pour nettoyer un nom de fichier
def clean_filename(filename):
    # Supprimer les accents
    nfkd_form = unicodedata.normalize('NFKD', filename)
    no_accents = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    # Remplacer les espaces et caractères spéciaux par _
    clean_name = re.sub(r'[^a-zA-Z0-9_.]', '_', no_accents)
    return clean_name

# Parcourir tous les sous-dossiers
for root, dirs, files in os.walk(dataset_dir):
    for file in files:
        old_path = os.path.join(root, file)
        new_file = clean_filename(file)
        new_path = os.path.join(root, new_file)
        os.rename(old_path, new_path)
        print(f"{file} -> {new_file}")
