from pathlib import Path

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(tags=["pages"])


@router.get("/")
def home() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=302)


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"title": "Sign in"},
    )


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"title": "Create account"},
    )


@router.get("/app")
def app_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={"title": "Todos"},
    )


@router.get("/profile")
def profile_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"title": "Profile"},
    )
