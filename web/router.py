from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime, timedelta
import os, json, random
import asyncio

router = APIRouter(prefix="/ui", tags=["web-ui"])

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Simple auth using session; in production integrate real auth

def get_user(request: Request):
    return request.session.get('user')

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "title": "Home", "year": datetime.now().year})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get('user'):
        return RedirectResponse(url="/ui/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login", "year": datetime.now().year})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...), remember: bool = Form(False)):
    # Demo auth: accept any non-empty credentials
    if email and password:
        request.session['user'] = {"email": email, "remember": remember}
        return RedirectResponse(url="/ui/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials", "title": "Login"})

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/ui", status_code=302)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user=Depends(get_user)):
    if not user:
        return RedirectResponse(url="/ui/login", status_code=302)
    return templates.TemplateResponse("dashboard.html", {"request": request, "title": "Dashboard", "year": datetime.now().year})

# Simple WebSocket for live metrics
_clients = set()
_started = False
_start_time = datetime.now()

@router.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            uptime = datetime.now() - _start_time
            payload = {
                "screenings_per_min": random.randint(200, 500),
                "alerts_per_min": random.randint(2, 20),
                "avg_latency_ms": random.randint(80, 250),
                "success_rate": round(random.uniform(97.0, 99.9), 2),
                "error_rate": round(random.uniform(0.1, 3.0), 2),
                "uptime": str(uptime).split('.')[0],
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
