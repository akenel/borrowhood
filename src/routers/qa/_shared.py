"""Shared router instances, templates, and helpers for qa/ package."""

import logging
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from src.i18n import detect_language, get_translator, SUPPORTED_LANGUAGES

logger = logging.getLogger("bh.qa_router")

router = APIRouter(prefix="/api/v1/testing", tags=["QA Testing"])
html_router = APIRouter(tags=["QA Testing - Web UI"])
templates = Jinja2Templates(directory="src/templates")


def _ctx(request: Request, token: Optional[dict] = None, **kwargs) -> dict:
    """Build template context with i18n (reuse pages.py pattern)."""
    query_lang = request.query_params.get("lang")
    cookie_lang = request.cookies.get("bh_lang")
    accept_lang = request.headers.get("accept-language")
    lang = detect_language(query_lang, cookie_lang, accept_lang)
    t = get_translator(lang)
    set_lang_cookie = query_lang and query_lang != cookie_lang
    ctx = {
        "request": request,
        "user": token,
        "t": t,
        "lang": lang,
        "supported_languages": SUPPORTED_LANGUAGES,
        "_set_lang_cookie": set_lang_cookie,
    }
    ctx.update(kwargs)
    return ctx


def _render(template_name: str, ctx: dict, status_code: int = 200):
    set_cookie = ctx.pop("_set_lang_cookie", False)
    lang = ctx.get("lang", "en")
    response = templates.TemplateResponse(template_name, ctx, status_code=status_code)
    if set_cookie:
        response.set_cookie("bh_lang", lang, max_age=365 * 24 * 3600, samesite="lax")
    return response
