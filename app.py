from fastapi import FastAPI
from pydantic import BaseModel
from google_play_scraper import app
import sqlite3

app = FastAPI()

# Підключення до бази даних
def get_db_connection():
    conn = sqlite3.connect('apps.db')
    conn.row_factory = sqlite3.Row
    return conn

# Створення таблиці, якщо її немає
def create_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS apps (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        package_name TEXT,
                        url TEXT,
                        description TEXT,
                        rating REAL,
                        updated_at TEXT
                    )''')
    conn.commit()
    conn.close()

create_table()

# Моделі для API
class AppInfo(BaseModel):
    name: str
    package_name: str
    url: str
    description: str
    rating: float
    updated_at: str

@app.get("/apps/{package_name}")
def get_app(package_name: str):
    conn = get_db_connection()
    app_info = conn.execute('SELECT * FROM apps WHERE package_name = ?', (package_name,)).fetchone()
    conn.close()
    if app_info:
        return {"name": app_info["name"], "package_name": app_info["package_name"], "url": app_info["url"], 
                "description": app_info["description"], "rating": app_info["rating"], "updated_at": app_info["updated_at"]}
    else:
        return {"error": "App not found"}

@app.post("/apps/")
def add_or_update_app(app_data: AppInfo):
    conn = get_db_connection()
    app_info = app.get(app_data.package_name)
    conn.execute('INSERT OR REPLACE INTO apps (name, package_name, url, description, rating, updated_at) VALUES (?, ?, ?, ?, ?, ?)',
                 (app_info['title'], app_data.package_name, app_info['url'], app_info['description'], app_info['score'], app_data.updated_at))
    conn.commit()
    conn.close()
    return {"message": "App data added/updated successfully"}
