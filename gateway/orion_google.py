#!/usr/bin/env python3
"""Puerta privada ORION con Google OIDC. NO inicia sesiones de Claude o ChatGPT.

Se despliega en un backend HTTPS separado. Nunca publicar este servidor sin
configurar credenciales OAuth, allowlist y sesión. GitHub Pages sigue público.
"""
import os
import sys
from pathlib import Path

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from centro_control import assemble  # noqa: E402

def env_config():
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    session_secret = os.environ.get("ORION_SESSION_SECRET", "")
    allowed = {item.strip().casefold() for item in
               os.environ.get("ORION_ALLOWED_GOOGLE_EMAILS", "").split(",") if item.strip()}
    base_url = os.environ.get("ORION_BASE_URL", "").rstrip("/")
    if not (client_id and client_secret and len(session_secret) >= 32
            and allowed and base_url.startswith("https://")):
        raise RuntimeError("OAuth incompleto. Se requieren secretos, correos admitidos y URL HTTPS.")
    if base_url.endswith("/"):
        raise RuntimeError("URL base inválida")
    return client_id, client_secret, session_secret, allowed, base_url

def allowed_google_profile(info, allowed):
    """No basta con coincidir en correo; Google debe verificarlo."""
    if not isinstance(info, dict) or not info.get("sub"):
        return False
    verified = info.get("email_verified")
    return verified in (True, "true") and str(info.get("email", "")).casefold() in allowed

def create_app():
    client_id, client_secret, session_secret, allowed, base_url = env_config()
    app = FastAPI(title="ORION privado — Google solamente", docs_url=None,
                  redoc_url=None, openapi_url=None)
    app.add_middleware(SessionMiddleware, secret_key=session_secret,
                       https_only=True, same_site="lax", max_age=60 * 60 * 4)
    oauth = OAuth()
    oauth.register(name="google", client_id=client_id, client_secret=client_secret,
                   server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                   client_kwargs={"scope": "openid email profile"})

    def identity(request):
        obj = request.session.get("identity")
        if not isinstance(obj, dict) or obj.get("email", "").casefold() not in allowed:
            return None
        return obj

    @app.get("/auth/login")
    async def login(request: Request):
        # State y nonce quedan gestionados por Authlib + sesión firmada.
        return await oauth.google.authorize_redirect(request, base_url + "/auth/callback")

    @app.get("/auth/callback")
    async def callback(request: Request):
        try:
            token = await oauth.google.authorize_access_token(request)
            # Authlib valida firma, issuer, audience, nonce y expiración del ID token
            # cuando usa server_metadata_url y devuelve la userinfo validada.
            info = token.get("userinfo")
        except (OAuthError, ValueError, KeyError):
            request.session.clear()
            raise HTTPException(status_code=401, detail="Google no pudo autenticar la sesión")
        if not allowed_google_profile(info, allowed):
            request.session.clear()
            raise HTTPException(status_code=403, detail="Cuenta Google no autorizada")
        request.session.clear()
        request.session["identity"] = {"email": info["email"], "sub": info["sub"]}
        return RedirectResponse("/", status_code=303)

    @app.post("/auth/logout")
    async def logout(request: Request):
        request.session.clear()
        return RedirectResponse("/auth/login", status_code=303)

    @app.get("/api/session")
    async def session(request: Request):
        person = identity(request)
        if not person:
            raise HTTPException(status_code=401, detail="No autorizado")
        return {"authenticated": True, "email": person["email"],
                "notice": "Google verifica identidad ORION, no abre Claude ni ChatGPT"}

    def require(request):
        if not identity(request):
            return RedirectResponse("/auth/login", status_code=303)
        return None

    @app.get("/")
    @app.get("/orion/")
    async def dashboard(request: Request):
        deny = require(request)
        return deny if deny else FileResponse(ROOT / "dashboard/index.html",
                                               media_type="text/html",
                                               headers={"Cache-Control": "no-store"})

    @app.get("/data.json")
    @app.get("/orion/data.json")
    async def snapshot(request: Request):
        if not identity(request):
            raise HTTPException(status_code=401, detail="No autorizado")
        data = assemble()
        data["governance"]["links"].pop("office", None)
        return JSONResponse(data, headers={"Cache-Control": "no-store"})

    @app.get("/cuentas")
    async def cuentas(request: Request):
        deny = require(request)
        if deny:
            return deny
        # No se reciben contraseñas, cookies ni tokens de servicios ajenos.
        page = """<!doctype html><html lang="es"><meta name="viewport" content="width=device-width,initial-scale=1">
        <title>ORION · Cuentas</title>
        <style>body{font:16px system-ui;background:#0b1322;color:#edf3fc;padding:2rem;max-width:580px;margin:auto}
        a{display:block;background:#1d3657;padding:1rem;border-radius:12px;color:white;margin:12px 0;text-decoration:none}
        p{color:#a9bfdc}button{padding:12px;border-radius:9px}</style>
        <h1>ORION · Accesos oficiales</h1>
        <p>Ingresaste a ORION con Google. ChatGPT y Claude gestionan sus propias sesiones.
        Usá «Continuar con Google» en cada sitio si corresponde a tu cuenta.</p>
        <a href="https://chatgpt.com/" rel="noopener noreferrer">Abrir ChatGPT</a>
        <a href="https://claude.ai/" rel="noopener noreferrer">Abrir Claude</a>
        <a href="/">Volver a ORION</a>
        <form method="post" action="/auth/logout"><button>Cerrar sesión de ORION</button></form>
        </html>"""
        return HTMLResponse(page, headers={"Cache-Control": "no-store"})

    @app.get("/visor/")
    async def visor(request: Request):
        deny = require(request)
        return deny if deny else FileResponse(ROOT / "docs/visor/index.html",
                                              media_type="text/html",
                                              headers={"Cache-Control": "no-store"})

    return app

# Solo importable cuando la configuración de producción está presente.
app = create_app()
