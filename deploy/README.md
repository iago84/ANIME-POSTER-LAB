# Despliegue — ANIME POSTER LAB

Despliegue **0-Docker** en un Linode: `venv` + `uvicorn` + `systemd` + `nginx`.

| Parámetro | Valor |
|---|---|
| Servicio systemd | `animeposter.service` |
| Raíz en el servidor | `/opt/animeposter` |
| Puerto local (uvicorn) | **8012** |
| Punto de entrada ASGI | `web.backend.main:app` |
| Sonda de salud | `GET /health/` |

## Ficheros

- `linode/SETUP_ALL.sh` — aprovisionamiento idempotente (10 pasos).
- `linode/animeposter.service` — unit systemd (referencia; lo escribe el SETUP).
- `linode/animeposter.nginx.conf` — vhost nginx (referencia; lo escribe el SETUP).
- `linode/.env.production.example` — plantilla de `/etc/animeposter.env`.

## Puesta en marcha

```powershell
# 1) Subir el código (o usar REPO_URL en SETUP_ALL.sh)
scp -r . root@<IP>:/opt/animeposter/app

# 2) Subir y ejecutar el aprovisionamiento
scp deploy/linode/SETUP_ALL.sh root@<IP>:/root/SETUP_ALL.sh
ssh root@<IP> "bash /root/SETUP_ALL.sh"
```

Tras el deploy, **edita** `/etc/animeposter.env` y pon el origen real del frontend
en `CORS_ALLOWED_ORIGINS` (vacío = solo localhost), luego:

```bash
sudo systemctl restart animeposter.service
```

## Verificación

```bash
curl -fsS http://127.0.0.1:8012/health/ | python3 -m json.tool
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8012/health/   # 200
```

El puerto **8012** debe ser idéntico en `SETUP_ALL.sh`, `animeposter.service` y
`animeposter.nginx.conf` (y libre en el servidor).
