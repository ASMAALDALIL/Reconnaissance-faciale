#Sans __init__.py, l’import suivant NE marche pas :
#from models.admin import Admin
#Pour Python, un dossier n’est pas automatiquement un module importable.
#python il import seulement package alors il peut pas importer un dossier directement c est pour ca fichier init import ce dossier comme package
from models.Admin import Admin
from models.Employe import Employee
from models.Camera import Camera
from models.Presence import Presence


'''ce qui en haut je le fait pour que dans fichier main je peut importer en utilisant 
from models import Admin, Employee, Camera, Presence, Alert, Uniform
'''