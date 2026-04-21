# 🎭 Système de Gestion des Présences par Reconnaissance Faciale

Application web complète intégrant l'IA (reconnaissance faciale) avec un backend FastAPI et un frontend React pour la gestion automatisée des présences en entreprise.

## 📋 Description

Ce système permet de détecter et identifier automatiquement les employés via une caméra en temps réel, enregistrant leurs présences/absences dans une base de données PostgreSQL. Un tableau de bord RH permet de consulter les statistiques, gérer les employés, les départements et les caméras.

## ✨ Fonctionnalités

- **Reconnaissance faciale en temps réel** — Identification automatique des employés via OpenCV + SVM
- **Tableau de bord RH** — Statistiques de présences, graphiques, indicateurs clés
- **Gestion des employés** — CRUD complet (ajout, modification, suppression)
- **Gestion des départements** — Organisation de la structure d'entreprise
- **Gestion des caméras** — Configuration des points de surveillance
- **Suivi des absences** — Historique et rapports détaillés
- **Authentification sécurisée** — JWT (JSON Web Tokens) + bcrypt
- **API REST complète** — Documentation Swagger auto-générée

## 🏗️ Architecture
### Frontend — React + Vite
| Page | Description |
|------|-------------|
| Login | Authentification admin |
| Dashboard | Vue d'ensemble & statistiques |
| Cameras | Gestion des caméras |
| Employes | CRUD des employés |
| Absences | Suivi des absences |
| DepartementForm | Gestion des départements |

### Backend — FastAPI
| Module | Description |
|--------|-------------|
| `routes/admin.py` | Gestion des admins |
| `routes/employee.py` | CRUD employés |
| `routes/camera.py` | Gestion caméras |
| `routes/departement.py` | Gestion départements |
| `routes/presence.py` | Enregistrement présences |
| `core/security.py` | JWT + bcrypt |
| `core/config.py` | Configuration |

### Module IA
| Fichier | Rôle |
|---------|------|
| `ai_recognition.py` | Reconnaissance faciale en temps réel |
| `entrainer_svm.py` | Entraînement du modèle SVM |
| `haarcascade_frontalface_default.xml` | Détection de visages (OpenCV) |
| `svm_model_160x160.pkl` | Modèle SVM entraîné |
| `visages_embeddings_comprimes.npz` | Embeddings compressés |

## 🤖 Pipeline IA
**Dataset d'entraînement :** 12 personnes (Angelina Jolie, Monica Bellucci, Billie Eilish, Cristiano Ronaldo, Donald Trump, Gigi Hadid, Achraf Hakimi, Johnny Depp, Justin Bieber, Lamine Yamal, Messi, Taylor Swift)

## 🛠️ Technologies

### Frontend
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)

### Backend
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat)

### IA
![OpenCV](https://img.shields.io/badge/OpenCV-27338e?style=flat&logo=OpenCV&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)

## 👥 Équipe

| Nom | GitHub |
|-----|--------|
| Asma Al Dalil | [@ASMAALDALIL](https://github.com/ASMAALDALIL) |
| Hanane Belhyane | [@hananebelhyane](https://github.com/hananebelhyane) |
| Meryem Al Moumi | [@MeryemAlMoumi](https://github.com/MeryemAlMoumi) |
