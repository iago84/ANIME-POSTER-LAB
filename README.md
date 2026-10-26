# ANIME POSTER LAB

Generador de **pósters y prompts de vídeo estilo anime/experimental**.
Recibe un concepto ("cyberpunk samurai", "ink wash", "vaporwave") y devuelve un
JSON operativo con: técnica de diseño, paleta estricta de 3 colores, tipografía
y los *prompts* listos para imagen y vídeo (estilo TikTok autocut).

Es a la vez:

- una **librería/CLI** (`poster_lab.py`) que no requiere red ni dependencias de pago, y
- una pequeña **API HTTP** (FastAPI, `web/backend/main.py`) que expone el motor.

## ¿Para quién?

Para el propio estudio (NAIRA STUDIO LTD) y para terceros que quieran integrar el
motor de generación de pósters mediante HTTP o línea de comandos.

## Cómo se ejecuta

Requisitos: Python 3.11+ (probado en 3.13). Instala dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 1. CLI (sin servidor)

```powershell
.\.venv\Scripts\python.exe poster_lab.py "cyberpunk samurai"
```

Imprime el JSON completo y un resumen (`técnica`, título, paleta, prompts).

### 2. API HTTP (FastAPI)

```powershell
.\start_8012.ps1
```

Arranca `uvicorn` en `http://127.0.0.1:8012`. Endpoints:

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Identificación del servicio (mensaje + versión, traducido por `?lang=`) |
| GET | `/health/` | Sonda de salud (liveness) |
| GET | `/techniques` | Catálogo de las 11 técnicas disponibles |
| GET | `/i18n/languages` | Idiomas soportados |
| POST | `/generate` | Genera el JSON del póster (`{concept, technique?, seed?}`) |
| POST | `/generate/video-prompt` | Devuelve solo el prompt de vídeo |

Ejemplo:

```powershell
curl "http://127.0.0.1:8012/techniques"
curl -X POST "http://127.0.0.1:8012/generate" -H "Content-Type: application/json" `
  -d '{"concept": "cyberpunk samurai", "seed": 42}'
```

Con `seed` igual se obtiene siempre el mismo resultado (reproducible).

## Qué depende

- **Runtime:** `fastapi`, `uvicorn`, `pydantic` (ver `requirements.txt`).
- **Desarrollo/tests:** `pytest`, `httpx`.
- El motor (`poster_lab.py`) usa **solo la librería estándar** (`json`, `random`,
  `dataclasses`, `enum`); no llama a ninguna API externa ni gasta red.

## Estructura

```
poster_lab.py            # motor: técnicas, paletas, prompts (CLI)
web/backend/main.py      # API FastAPI
web/backend/requirements.txt
i18n_support/            # carga de traducciones (.po)
locale/<lang>/LC_MESSAGES/messages.po
tests/                   # suites pytest
legal/                   # privacidad y términos
deploy/linode/           # despliegue 0-Docker (venv + uvicorn + systemd + nginx)
start_8012.ps1           # arranque local
prompt.txt               # prompt maestro del sistema (spec creativa)
```

## Documentación creativa

El comportamiento del motor (metodologías `BLEND_IN_BLACK` / `BLEND_ON_WHITE` /
`MASK_CUT`, estructura del JSON, directrices de la IA) se describe en
[`prompt.txt`](prompt.txt).

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Despliegue

Ver [`deploy/README.md`](deploy/README.md). Puerto por defecto: **8012**.

---

© NAIRA STUDIO LTD — Licencia de uso personal no exclusiva; ver [`legal/terms.md`](legal/terms.md).
