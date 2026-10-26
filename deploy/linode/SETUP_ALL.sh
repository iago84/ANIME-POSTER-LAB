#!/usr/bin/env bash
#
# =============================================================================
#  SETUP_ALL.sh — Aprovisionamiento 0-Docker de ANIME POSTER LAB
#  (venv + uvicorn + systemd + nginx). Adaptado de
#  ARTEFACTOS_TRAE/C2_SETUP_ALL_TEMPLATE.sh a un backend FastAPI/ASGI.
# =============================================================================
#
#  Qué hace (10 pasos idempotentes):
#    1) Comprobación sudo/root
#    2) apt update + paquetes (python3-venv, nginx, git, build-essential)
#    3) Crear carpetas APP_ROOT/{app,venv,logs}
#    4) Crear /etc/<SVC>.env desde deploy/linode/.env.production.example
#    5) Código (opcional git clone) + python3 -m venv + pip install -r requirements.txt
#    6) Instalar unit systemd /etc/systemd/system/<SVC>.service
#    7) systemctl daemon-reload / enable / restart
#    8) Vhost nginx + symlink + nginx -t + reload (con rollback si falla)
#    9) Smoke test: curl http://127.0.0.1:<APP_PORT>/health/
#   10) RESUMEN
#
#  RE-EJECUTABLE: no sobrescribe /etc/<SVC>.env existente; backups de nginx con
#  timestamp; apt/venv/systemctl/symlink son idempotentes.
#
#  ---------- SUBIDA Y EJECUCIÓN (desde Windows/PowerShell) ----------
#    scp deploy/linode/SETUP_ALL.sh root@<IP>:/root/SETUP_ALL.sh
#    ssh root@<IP> "bash /root/SETUP_ALL.sh"
# =============================================================================

set -euo pipefail

# ===========================================================================
# PARÁMETROS
# ===========================================================================
SVC="animeposter"
APP_ROOT="/opt/animeposter"
APP_PORT="8012"
APP_USER="www-data"
REPO_URL=""                       # Opcional: git clone si APP_ROOT/app está vacío
DOMAIN=""                         # Dominio real (vacío "" si aún no hay DNS)
UVICORN_WORKERS="3"

# ---- Rutas derivadas (no editar) ------------------------------------------
APP_DIR="${APP_ROOT}/app"
VENV_DIR="${APP_ROOT}/venv"
LOG_DIR="${APP_ROOT}/logs"
ENV_FILE="/etc/${SVC}.env"
ENV_EXAMPLE="${APP_DIR}/deploy/linode/.env.production.example"
UNIT_FILE="/etc/systemd/system/${SVC}.service"
NGINX_AVAILABLE="/etc/nginx/sites-available/${SVC}"
NGINX_ENABLED="/etc/nginx/sites-enabled/${SVC}"
TS="$(date +%Y%m%d%H%M%S)"

ok()    { printf '\e[32m[ OK ]\e[0m  %s\n' "$*"; }
info()  { printf '\e[34m[INFO]\e[0m  %s\n' "$*"; }
warn()  { printf '\e[33m[WARN]\e[0m  %s\n' "$*" >&2; }
fail()  { printf '\e[31m[FAIL]\e[0m %s\n' "$*" >&2; exit 1; }
stage() { printf '\n\e[1;36m==== %s ====\e[0m\n' "$*"; }

# ===========================================================================
# Paso 1) Privilegios
# ===========================================================================
stage "Paso 1) Comprobación de privilegios"
if [[ "${EUID}" -ne 0 ]]; then
  fail "Ejecuta como root o con sudo: sudo bash $0"
fi
if ! [[ "${APP_PORT}" =~ ^[0-9]{2,5}$ ]]; then
  fail "APP_PORT inválido: '${APP_PORT}'. Debe ser numérico (8000..8014)."
fi
ok "Ejecutando como root."

export DEBIAN_FRONTEND=noninteractive

# ===========================================================================
# Paso 2) Paquetes base
# ===========================================================================
stage "Paso 2) Paquetes base (apt)"
apt-get update -y
apt-get install -y --no-install-recommends \
  python3 python3-venv python3-dev \
  nginx git build-essential curl ca-certificates
ok "Paquetes base instalados/actualizados."

# ===========================================================================
# Paso 3) Estructura de carpetas
# ===========================================================================
stage "Paso 3) Carpetas de la aplicación"
mkdir -p "${APP_DIR}" "${VENV_DIR}" "${LOG_DIR}"
chown -R "${APP_USER}:${APP_USER}" "${LOG_DIR}"
chown -R root:root "${APP_DIR}" "${VENV_DIR}"
ok "Carpetas creadas: app/ venv/ logs/"

# ===========================================================================
# Paso 4) /etc/<SVC>.env (no sobrescribe)
# ===========================================================================
stage "Paso 4) Fichero de entorno ${ENV_FILE}"
if [[ -f "${ENV_FILE}" ]]; then
  info "${ENV_FILE} ya existe -> NO se sobrescribe (idempotencia)."
else
  if [[ -f "${ENV_EXAMPLE}" ]]; then
    install -m 0600 "${ENV_EXAMPLE}" "${ENV_FILE}"
    warn "Creado ${ENV_FILE} desde el ejemplo. EDITA CORS_ALLOWED_ORIGINS con el"
    warn "origen real del frontend antes de ir a producción:  nano ${ENV_FILE}"
  else
    fail "Falta ${ENV_EXAMPLE}. Sube deploy/linode/ del proyecto o crea ${ENV_FILE} a mano."
  fi
fi

# ===========================================================================
# Paso 5) Código, venv y dependencias
# ===========================================================================
stage "Paso 5) Código, venv y dependencias"
if [[ ! -f "${APP_DIR}/requirements.txt" ]]; then
  if [[ -n "${REPO_URL}" ]]; then
    info "Clonando ${REPO_URL} en ${APP_DIR} ..."
    git clone "${REPO_URL}" "${APP_DIR}"
  else
    fail "No hay ${APP_DIR}/requirements.txt y REPO_URL está vacío. Sube el código."
  fi
fi
if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  info "Creando venv en ${VENV_DIR} ..."
  python3 -m venv "${VENV_DIR}"
else
  info "venv existente -> se reutiliza."
fi
"${VENV_DIR}/bin/pip" install --upgrade pip wheel
"${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"
ok "venv listo y dependencias instaladas."

# ===========================================================================
# Paso 6) Unit systemd
# ===========================================================================
stage "Paso 6) Unit systemd ${UNIT_FILE}"
cat > "${UNIT_FILE}" <<UNIT
# Generado por SETUP_ALL.sh (${TS})
[Unit]
Description=Uvicorn daemon for ${SVC} (FastAPI, 0-Docker)
After=network.target

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
EnvironmentFile=${ENV_FILE}
ExecStart=${VENV_DIR}/bin/uvicorn web.backend.main:app \\
  --host 127.0.0.1 \\
  --port ${APP_PORT} \\
  --workers ${UVICORN_WORKERS} \\
  --proxy-headers \\
  --forwarded-allow-ips 127.0.0.1
Restart=always
RestartSec=5

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
ReadWritePaths=${APP_ROOT}
UNIT
chmod 0644 "${UNIT_FILE}"
ok "Unit escrito."

# ===========================================================================
# Paso 7) Servicio
# ===========================================================================
stage "Paso 7) Habilitar y (re)arrancar ${SVC}"
systemctl daemon-reload
systemctl enable "${SVC}.service"
systemctl restart "${SVC}.service"
if systemctl is-active --quiet "${SVC}.service"; then
  ok "${SVC}.service activo."
else
  journalctl -u "${SVC}.service" -n 40 --no-pager || true
  fail "${SVC}.service NO está activo. Revisa journalctl arriba."
fi

# ===========================================================================
# Paso 8) Vhost nginx
# ===========================================================================
stage "Paso 8) Vhost nginx ${NGINX_AVAILABLE}"
if [[ -f "${NGINX_AVAILABLE}" ]]; then
  cp "${NGINX_AVAILABLE}" "${NGINX_AVAILABLE}.bak-${TS}"
  info "Backup previo: ${NGINX_AVAILABLE}.bak-${TS}"
fi
cat > "${NGINX_AVAILABLE}" <<NGINX
# Generado por SETUP_ALL.sh (${TS})
upstream animeposter_app {
    server 127.0.0.1:${APP_PORT} fail_timeout=0;
}

server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN:-_};

    client_max_body_size 5m;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        allow all;
    }

    location / {
        proxy_pass http://animeposter_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
NGINX
ln -sfn "${NGINX_AVAILABLE}" "${NGINX_ENABLED}"

if ! nginx -t 2>/tmp/nginx-test-${TS}.log; then
  warn "nginx -t FALLÓ. Rollback del vhost:"
  if [[ -f "${NGINX_AVAILABLE}.bak-${TS}" ]]; then
    mv -f "${NGINX_AVAILABLE}.bak-${TS}" "${NGINX_AVAILABLE}"
    warn "Restaurado vhost anterior desde backup."
  else
    rm -f "${NGINX_ENABLED}" "${NGINX_AVAILABLE}"
    warn "No había backup: se eliminó el vhost nuevo."
  fi
  nginx -t && systemctl reload nginx || true
  cat "/tmp/nginx-test-${TS}.log" >&2 || true
  fail "Configuración nginx inválida; proyecto NO desplegado."
fi
systemctl reload nginx
ok "nginx recargado con ${NGINX_ENABLED}."

# ===========================================================================
# Paso 9) Smoke test local
# ===========================================================================
stage "Paso 9) Smoke test http://127.0.0.1:${APP_PORT}/health/"
SMOKE_URL="http://127.0.0.1:${APP_PORT}/health/"
HTTP_CODE="$(curl -fsS -o /dev/null -w '%{http_code}' \
  --retry 5 --retry-delay 2 --retry-connrefused "${SMOKE_URL}" || true)"
if [[ "${HTTP_CODE}" == "200" ]]; then
  ok "Smoke OK: ${SMOKE_URL} -> HTTP ${HTTP_CODE}"
else
  warn "Smoke FALLÓ: ${SMOKE_URL} -> HTTP '${HTTP_CODE:-sin respuesta}'"
  warn "Comprueba que el proyecto expone GET /health/ y revisa:"
  warn "  journalctl -u ${SVC}.service -n 40 --no-pager"
  fail "Smoke test no devolvió 200. Deploy incompleto."
fi

# ===========================================================================
# Paso 10) RESUMEN
# ===========================================================================
stage "Paso 10) RESUMEN — ${SVC}"
cat <<SUMMARY
  Servicio systemd : ${SVC}.service  ($(systemctl is-active "${SVC}.service"))
  Unit             : ${UNIT_FILE}
  Env              : ${ENV_FILE}   (edita aquí CORS_ALLOWED_ORIGINS)
  uvicorn          : 127.0.0.1:${APP_PORT}
  nginx vhost      : ${NGINX_ENABLED}
  Código / venv    : ${APP_DIR}  /  ${VENV_DIR}
  Logs             : journalctl -u ${SVC}.service -f

  Siguientes pasos (una vez, cuando el DNS apunte al Linode):
    certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}
SUMMARY
ok "Aprovisionamiento de ${SVC} completado."
