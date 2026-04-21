# -*- coding: utf-8 -*-
# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from database import engine, Base
from routes import admin
from routes import presence
from routes import departement
from routes import employee
from routes import camera

Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,      
    allow_methods=["*"],        
    allow_headers=["*"],         
)


app.include_router(admin.router)
app.include_router(presence.router)
app.include_router(departement.router)
app.include_router(employee.router)
app.include_router(camera.router)

# Route de test (optionnelle)
@app.get("/")
def home():
    return {"message": "Backend OK"}