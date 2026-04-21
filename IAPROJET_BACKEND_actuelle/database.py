# -*- coding: utf-8 -*-

from sqlalchemy import create_engine #il sert a faire cnx ave cdatabase  cest comme un pont entre sqlalchemy et la bas
from  sqlalchemy.orm import sessionmaker,declarative_base
#session maker  cree des sessions sessions sont eux qui execute les requetes et  gere les transactions
#declarative_base permet a sqlalchemy de savori quel modele exesten et comment mapper vers les tables
from core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"options": "-c client_encoding=utf8"} 
)# echo true poiur dire que la requete s affiche dans console utilie pour debugger
SessionLocal=sessionmaker(bind=engine, autoflush=False, autocommit=False)
#bind=engine pour dire que session va utiliser cette pont
Base=declarative_base()
def get_db():
    db = SessionLocal()#creer une session chaque requete est une nouivelle session
    try:
        yield db #la requete
    finally:
        db.close()#ferme la session apres la requete et libere la cnx
