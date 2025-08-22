from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import os, json, asyncio, uuid

# Reuse session-based demo auth from web.router

def get_user(request: Request):
    return request.session.get('user')

router = APIRouter(prefix="/ui/admin", tags=["admin-ui"])

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
templates = Jinja2Templates(directory=TEMPLATES_DIR)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
REGISTRY_FILE = DATA_DIR / "feed_registry.json"

# Utilities for registry persistence

def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_registry() -> Dict[str, Any]:
    _ensure_data_dir()
    if not REGISTRY_FILE.exists():
        return {"feeds": []}
    try:
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {"feeds": []}


def _save_registry(data: Dict[str, Any]):
    _ensure_data_dir()
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def _bootstrap_registry_if_needed():
    data = _load_registry()
    if data.get("feeds"):
        return
    # Bootstrap from AdverseMediaService defaults when available
    try:
        from services.data_sources.adverse_media import AdverseMediaService
        svc = AdverseMediaService()
        feeds = []
        for key, meta in svc.sources.items():
            feeds.append({
                "id": key,
                "name": meta.get("name", key.title()),
                "type": meta.get("type", "rss"),
                "url": meta.get("url", ""),
                "enabled": bool(meta.get("enabled", True)),
                "tags": [],
                "created_at": datetime.now().isoformat()
            })
        _save_registry({"feeds": feeds})
    except Exception:
        # Fallback to empty registry
        _save_registry({"feeds": []})


@router.get("/", response_class=HTMLResponse)
async def admin_home(request: Request, user=Depends(get_user)):
    if not user:
        return RedirectResponse(url="/ui/login", status_code=302)
    _bootstrap_registry_if_needed()
    # Lightweight system metrics (placeholder)
    from services.scraping.job_manager import ScrapingJobManager
    jm = ScrapingJobManager(data_dir=str(DATA_DIR))
    stats = jm.get_job_statistics()
    reg = _load_registry()
    return templates.TemplateResponse(
        "admin/overview.html",
        {
            "request": request,
            "title": "Admin Control Panel",
            "job_stats": stats,
            "feeds_count": len(reg.get("feeds", [])),
            "now": datetime.now().isoformat(),
        },
    )


@router.get("/feeds", response_class=HTMLResponse)
async def feeds_page(request: Request, user=Depends(get_user)):
    if not user:
        return RedirectResponse(url="/ui/login", status_code=302)
    _bootstrap_registry_if_needed()
    reg = _load_registry()
    return templates.TemplateResponse(
        "admin/feeds.html",
        {"request": request, "title": "Manage Feeds", "registry": reg},
    )


@router.post("/feeds/add")
async def add_feed(
    request: Request,
    name: str = Form(...),
    url: str = Form(...),
    type: str = Form("rss"),
    enabled: bool = Form(True),
    tags: str = Form(""),
    user=Depends(get_user),
):
    if not user:
        return RedirectResponse(url="/ui/login", status_code=302)
    reg = _load_registry()
    feed_id = uuid.uuid4().hex[:8]
    reg.setdefault("feeds", []).append({
        "id": feed_id,
        "name": name,
        "type": type,
        "url": url,
        "enabled": bool(enabled),
        "tags": [t.strip() for t in tags.split(',') if t.strip()],
        "created_at": datetime.now().isoformat(),
    })
    _save_registry(reg)
    return RedirectResponse(url="/ui/admin/feeds", status_code=303)


@router.post("/feeds/{feed_id}/toggle")
async def toggle_feed(feed_id: str, request: Request, user=Depends(get_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    reg = _load_registry()
    for f in reg.get("feeds", []):
        if f.get("id") == feed_id:
            f["enabled"] = not bool(f.get("enabled"))
            _save_registry(reg)
            return RedirectResponse(url="/ui/admin/feeds", status_code=303)
    raise HTTPException(status_code=404, detail="Feed not found")


@router.post("/feeds/{feed_id}/delete")
async def delete_feed(feed_id: str, request: Request, user=Depends(get_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    reg = _load_registry()
    before = len(reg.get("feeds", []))
    reg["feeds"] = [f for f in reg.get("feeds", []) if f.get("id") != feed_id]
    _save_registry(reg)
    if len(reg["feeds"]) == before:
        raise HTTPException(status_code=404, detail="Feed not found")
    return RedirectResponse(url="/ui/admin/feeds", status_code=303)


@router.get("/scrapers", response_class=HTMLResponse)
async def scrapers_page(request: Request, user=Depends(get_user)):
    if not user:
        return RedirectResponse(url="/ui/login", status_code=302)
    from services.scraping.job_manager import ScrapingJobManager, JobStatus, JobPriority, ScrapingType
    jm = ScrapingJobManager(data_dir=str(DATA_DIR))
    jobs = jm.list_jobs()
    return templates.TemplateResponse(
        "admin/scrapers.html",
        {
            "request": request,
            "title": "Scrapers",
            "jobs": jobs,
            "JobStatus": JobStatus,
            "JobPriority": JobPriority,
            "ScrapingType": ScrapingType,
        },
    )


@router.post("/scrapers/create")
async def scrapers_create(
    request: Request,
    name: str = Form(...),
    job_type: str = Form("custom"),
    target_urls: str = Form(""),
    priority: int = Form(2),
    user=Depends(get_user),
):
    if not user:
        return RedirectResponse(url="/ui/login", status_code=302)
    from services.scraping.job_manager import ScrapingJobManager, JobPriority, ScrapingType
    jm = ScrapingJobManager(data_dir=str(DATA_DIR))
    urls = [u.strip() for u in target_urls.splitlines() if u.strip()]
    try:
        job_id = jm.create_job(
            name=name,
            job_type=ScrapingType(job_type) if job_type in [t.value for t in ScrapingType] else ScrapingType.CUSTOM,
            target_urls=urls,
            priority=JobPriority(priority) if priority in [p.value for p in JobPriority] else JobPriority.MEDIUM,
            config={"delay": 1.0},
        )
    except Exception:
        job_id = jm.create_job(
            name=name,
            job_type=ScrapingType.CUSTOM,
            target_urls=urls,
        )
    return RedirectResponse(url="/ui/admin/scrapers", status_code=303)


@router.post("/scrapers/{job_id}/start")
async def scrapers_start(job_id: str, request: Request, user=Depends(get_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    from services.scraping.job_manager import ScrapingJobManager
    jm = ScrapingJobManager(data_dir=str(DATA_DIR))
    # Fire and forget
    async def _run():
        async with jm:
            try:
                await jm.execute_job(job_id)
            except Exception:
                pass
    asyncio.create_task(_run())
    return RedirectResponse(url="/ui/admin/scrapers", status_code=303)


@router.post("/scrapers/{job_id}/cancel")
async def scrapers_cancel(job_id: str, request: Request, user=Depends(get_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    from services.scraping.job_manager import ScrapingJobManager
    jm = ScrapingJobManager(data_dir=str(DATA_DIR))
    jm.cancel_job(job_id)
    return RedirectResponse(url="/ui/admin/scrapers", status_code=303)


@router.get("/metrics")
async def admin_metrics(user=Depends(get_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    from services.scraping.job_manager import ScrapingJobManager
    jm = ScrapingJobManager(data_dir=str(DATA_DIR))
    stats = jm.get_job_statistics()
    reg = _load_registry()
    return JSONResponse({
        "time": datetime.now().isoformat(),
        "jobs": stats,
        "feeds": {
            "total": len(reg.get("feeds", [])),
            "active": len([f for f in reg.get("feeds", []) if f.get("enabled")]),
        },
    })


def _sqlite_inspect(db_path: Path, max_rows: int = 5) -> Dict[str, Any]:
    info: Dict[str, Any] = {"path": str(db_path), "exists": db_path.exists(), "tables": []}
    if not db_path.exists():
        return info
    import sqlite3
    try:
        con = sqlite3.connect(str(db_path))
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                count = cur.fetchone()[0]
            except Exception:
                count = None
            sample = []
            try:
                cur.execute(f"SELECT * FROM {t} LIMIT {max_rows}")
                cols = [d[0] for d in cur.description] if cur.description else []
                for row in cur.fetchall():
                    sample.append({c: v for c, v in zip(cols, row)})
            except Exception:
                pass
            info["tables"].append({"name": t, "count": count, "sample": sample})
    except Exception as e:
        info["error"] = str(e)
    finally:
        try:
            con.close()
        except Exception:
            pass
    return info


@router.get("/data", response_class=HTMLResponse)
async def data_quality(request: Request, user=Depends(get_user)):
    if not user:
        return RedirectResponse(url="/ui/login", status_code=302)
    base = Path(__file__).resolve().parents[1]
    dbs = {
        "Compliance Analysis": base / "compliance_analysis.db",
        "Sanctions": base / "sanctions.db",
        "Admin Sources": base / "database" / "data_sources.db",
    }
    reports = {name: _sqlite_inspect(path) for name, path in dbs.items()}
    return templates.TemplateResponse(
        "admin/data.html",
        {"request": request, "title": "Data Quality", "reports": reports},
    )


@router.get("/troubleshoot", response_class=HTMLResponse)
async def troubleshoot(request: Request, user=Depends(get_user)):
    if not user:
        return RedirectResponse(url="/ui/login", status_code=302)
    from services.scraping.job_manager import ScrapingJobManager
    jm = ScrapingJobManager(data_dir=str(DATA_DIR))
    execs = jm.get_execution_history()[:20]
    errors: List[Dict[str, Any]] = []
    for ex in execs:
        if getattr(ex, "errors", None):
            errors.append({
                "execution_id": ex.execution_id,
                "job_id": ex.job_id,
                "started_at": ex.started_at,
                "completed_at": ex.completed_at,
                "errors": ex.errors,
            })
    return templates.TemplateResponse(
        "admin/troubleshoot.html",
        {"request": request, "title": "Troubleshoot", "executions": execs, "errors": errors},
    )


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, user=Depends(get_user)):
    if not user:
        return RedirectResponse(url="/ui/login", status_code=302)
    # Selected environment/config values (read-only demo)
    keys = [
        "ALLOWED_ORIGINS", "DATABASE_URL", "REDIS_URL", "ENV", "SECRET_KEY",
    ]
    env = {k: os.getenv(k, "") for k in keys}
    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request, "title": "Settings", "env": env},
    )
