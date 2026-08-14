# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto

"Granero" — gestión de inventario, compras/ventas y contabilidad de partida doble para una tienda. Backend FastAPI en clean architecture, frontend React/Vite, todo orquestado con Docker Compose. El README (en español) documenta el uso; este archivo cubre cómo trabajar sobre el código.

## Comandos

### Levantar todo

```bash
docker compose up            # postgres + backend(:8000) + frontend(:5173) + adminer(:8080)
```

El `entrypoint.sh` del backend corre `alembic upgrade head` y luego `python -m scripts.seed` (idempotente) en cada arranque. `backend/app`, `backend/tests`, `frontend/src` están montados como volúmenes → hot reload (uvicorn `--reload`, Vite HMR). Login demo: `admin@granero.com` / `admin123`.

### Backend (desde `backend/`)

```bash
pip install -r requirements-dev.txt
ruff check .                 # lint
black --check .              # formato (line-length 100, py312)
pytest -q                    # toda la suite; NO requiere Postgres
pytest tests/unit/application/test_register_sale.py -q          # un archivo
pytest tests/unit/application/test_register_sale.py::test_x -q  # un test
alembic revision --autogenerate -m "descripcion" && alembic upgrade head
```

`pyproject.toml` fija `pythonpath = ["."]` y `testpaths = ["tests"]`, así que pytest debe ejecutarse desde `backend/`.

### Frontend (desde `frontend/`)

```bash
npm install
npm run lint
npm run build                # tsc -b && vite build (esto es el typecheck)
```

CI (`.github/workflows/ci.yml`) corre exactamente: ruff + black + pytest en backend, eslint + build en frontend. No hay servicio de base de datos en CI porque los tests no lo necesitan.

## Arquitectura del backend

Cuatro capas con dependencias apuntando hacia adentro (`backend/app/`):

- `domain/` — entidades (dataclasses), enums, excepciones, e **interfaces de repositorio** (puertos). Sin SQLAlchemy ni FastAPI.
- `application/` — casos de uso, `AbstractUnitOfWork`, `AccountingService`. Depende solo de `domain/`.
- `infrastructure/` — modelos ORM, repositorios SQLAlchemy, `SqlAlchemyUnitOfWork`, JWT/bcrypt, `Settings` (pydantic-settings).
- `presentation/` — routers FastAPI, schemas Pydantic, y `deps.py` con toda la inyección de dependencias.

### Unit of Work — el eje del diseño

Los casos de uso reciben un `AbstractUnitOfWork` (nunca una `Session`). El UoW agrupa los nueve repositorios (`uow.products`, `uow.sales`, `uow.journal_entries`, …) tras una sola transacción. Contrato importante en `application/unit_of_work.py`: **`__exit__` siempre hace rollback**; el caso de uso debe llamar `uow.commit()` explícitamente antes de salir del `with`. Olvidarlo significa que nada se persiste.

Esto es lo que permite testear toda la lógica de negocio con `InMemoryUnitOfWork` (`tests/unit/application/fakes/in_memory_uow.py`) — incluidos los tests de "integración" de API, que sobreescriben `get_uow` vía `app.dependency_overrides` (ver `tests/integration/conftest.py`).

### Operaciones atómicas inventario + contabilidad

`RegisterSaleUseCase` / `RegisterPurchaseUseCase` son el patrón de referencia: validan stock, crean el documento, escriben el movimiento de kardex, actualizan `current_stock` del producto y generan un asiento contable balanceado — todo en la misma transacción. Si tocas alguna de estas rutas, mantén las cuatro cosas juntas.

Los asientos los arma `AccountingService`, que recibe un dict `{código: account_id}` (resuelto por `resolve_account_ids(uow, codes)`) en vez de acceder al repositorio, para quedar libre de dependencias. Los códigos del plan de cuentas viven en un único lugar, `domain/accounting_codes.py`, compartido por el seed y el servicio — no los hardcodees. Todo asiento pasa por `assert_balanced()` antes de persistirse.

### Errores

Las excepciones de dominio heredan de `DomainError` y llevan el mensaje en español ya formateado. `main.py` las mapea a HTTP en un solo handler (`NotFoundError`→404, `DuplicateError`→409, `InvalidCredentialsError`→401, resto→400). No lances `HTTPException` desde los casos de uso; añade o reutiliza una excepción de dominio.

### Añadir un endpoint nuevo

Toca cinco archivos, en este orden: entidad + interfaz de repositorio en `domain/` → caso de uso en `application/use_cases/<modulo>/` → repositorio SQLAlchemy + modelo ORM en `infrastructure/` → schema Pydantic + router en `presentation/` → un provider `get_*_use_case` en `presentation/api/v1/deps.py`, e incluir el router en `main.py` con prefijo `/api/v1`. Si agregas un repositorio al UoW, hay que añadirlo también a `SqlAlchemyUnitOfWork` **y** a `InMemoryUnitOfWork` o los tests fallan. Los routers protegidos llevan `dependencies=[Depends(get_current_user)]` a nivel de `APIRouter`.

## Frontend

Estructura por feature: `src/features/<modulo>/{api,pages}`. Cada feature expone un objeto plano (`productsApi`, `salesApi`, …) que envuelve `apiClient` y devuelve `r.data`; los componentes consumen eso con React Query. Los tipos de respuesta viven centralizados en `src/types/api.ts`.

`lib/api-client.ts` es axios con dos interceptores: adjunta el JWT desde `authStorage` y, ante un 401, limpia el token y redirige a `/login`. `extractErrorMessage()` normaliza el `detail` de FastAPI (string o array de errores de validación) para mostrarlo en UI.

Rutas y providers en `src/app/App.tsx`; todo lo autenticado cuelga de `<ProtectedRoute><Layout/></ProtectedRoute>`. Alias `@/` → `src/`. UI propia minimalista en `components/ui/` (Button, Input, Modal, Table, KpiCard…) sobre Tailwind v4 — reutilízala en vez de escribir clases sueltas.

## Convenciones

- Texto visible al usuario (mensajes de error, descripciones de asientos, labels) en **español**; docstrings y comentarios de código en inglés.
- Dinero y cantidades con `Decimal` en el backend de punta a punta; nunca `float`.
- `JWT_EXPIRE_MINUTES: 0` es intencional en el compose — significa sesión que no expira, decisión de UX para la demo.
