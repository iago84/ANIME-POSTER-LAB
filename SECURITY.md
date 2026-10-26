# Política de seguridad — ANIME POSTER LAB

## Superficie de ataque

El proyecto es una **utilidad de generación** con dos caras:

- `poster_lab.py`: motor local. **No usa red, no lee secretos, no ejecuta código
  de terceros.** Sus entradas son conceptos de texto; sus salidas, JSON.
- `web/backend/main.py`: API HTTP (FastAPI) que envuelve al motor.

## Medidas vigentes

| Área | Medida |
|---|---|
| CORS | `allow_origins` **solo** desde `CORS_ALLOWED_ORIGINS` (lista explícita). Nunca `"*"` con `allow_credentials=True`. Ver `ARTEFACTOS_TRAE/E3`. |
| Métodos/cabeceras | Restringidos a `GET, POST, OPTIONS` y `Content-Type`. |
| Sonda | `GET /health/` sin autenticación; **no expone** secretos, hosts ni rutas: solo `status`, `version`, `timestamp` y checks booleanos. |
| Secretos | Ninguno en el repositorio. `.env` está en `.gitignore`; solo se versiona `.env.example`. |
| Validación de entrada | Esquemas Pydantic (`GenerateRequest`); técnica inválida → error explícito. |
| Dependencias | Fijadas por rango mínimo en `requirements.txt`; `ruff` + `pre-commit` en el ciclo. |

## Riesgos conocidos y su estado

- **No hay autenticación.** La API es de uso local/interno. **No exponerla en
  Internet sin añadir autenticación y limitación de tasa** (p. ej. API key o
  proxy inverso con `auth_request`).
- **Sin persistencia:** no guarda datos de usuario, por lo que no hay superficie
  de fuga de datos almacenados.

## Reporte de vulnerabilidades

Escribe a **heart.at.flames@gmail.com** con pasos de reproducción. No abras un
*issue* público para vulnerabilidades explotables.
