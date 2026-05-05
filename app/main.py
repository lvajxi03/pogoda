from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader

from .db import SessionLocal, engine, Base
from .models import City
from .weather import get_weather, describe_weather, weather_icon
from .auth import *

import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "secret"))

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Environment(loader=FileSystemLoader("app/templates"))

from datetime import datetime

def as_weekday(value: str) -> str:
    days = {
        0: "Poniedziałek",
        1: "Wtorek",
        2: "Środa",
        3: "Czwartek",
        4: "Piątek",
        5: "Sobota",
        6: "Niedziela",
    }

    date = datetime.strptime(value, "%Y-%m-%d")
    return days[date.weekday()]

templates.filters["as_weekday"] = as_weekday
templates.filters["weather_icon"] = weather_icon

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- FRONT ----------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    template = templates.get_template("index.html")
    return template.render(request=request)

@app.get("/partials/weather", response_class=HTMLResponse)
async def weather_partial(request: Request, db: Session = Depends(get_db)):
    cities = db.query(City).filter_by(enabled=True).order_by(City.sort_order).all()

    data = []
    for c in cities:
        w = await get_weather(c)

        code = w["current"].get("weather_code")
        description, icon = describe_weather(code)

        data.append({
            "city": c,
            "weather": w,
            "description": description,
            "icon": icon,
        })

    template = templates.get_template("partials/weather_cards.html")
    return template.render(cities=data)

# ---------- AUTH ----------

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.get_template("login.html").render()

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and verify(password):
        login_user(request, username)
        return RedirectResponse("/admin/cities", status_code=303)
    return RedirectResponse("/login", status_code=303)

@app.get("/logout")
def logout(request: Request):
    logout_user(request)
    return RedirectResponse("/", status_code=303)

# ---------- ADMIN ----------

@app.get("/admin/cities", response_class=HTMLResponse)
def admin_cities(request: Request, db: Session = Depends(get_db)):
    if not is_logged(request):
        return RedirectResponse("/login", status_code=303)

    cities = db.query(City).all()
    return templates.get_template("admin_cities.html").render(cities=cities)

@app.post("/admin/cities")
def add_city(
    request: Request,
    name: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    db: Session = Depends(get_db),
):
    if not is_logged(request):
        return RedirectResponse("/login", status_code=303)

    city = City(name=name, latitude=lat, longitude=lon)
    db.add(city)
    db.commit()

    return RedirectResponse("/admin/cities", status_code=303)

