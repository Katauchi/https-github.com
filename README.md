# School Search API – Technical Challenge

API desarrollada con FastAPI para realizar búsquedas rápidas sobre más de 100,000 registros de escuelas.

## Objetivo
Unificar múltiples archivos CSV y permitir búsquedas eficientes mediante una API REST.

## Tecnologías
- Python
- FastAPI
- Uvicorn

## Endpoints
- `/health` → estado del servicio
- `/searchquery=` → búsqueda de escuelas
- `/schools/{id}` → detalle de escuela

## Ejecutar localmente
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
