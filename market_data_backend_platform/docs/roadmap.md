# Roadmap de Desarrollo — Market Data Backend Platform

## Objetivo del proyecto

Diseñar y desplegar una plataforma backend orientada a datos financieros que permita:

- Ingestar datos históricos de mercado (acciones, índices y criptomonedas).
- Normalizar y persistir series temporales de forma consistente.
- Exponer los datos mediante APIs REST (API-first).
- Visualizar datos y KPIs mediante Grafana.
- Ejecutarse de forma reproducible en entorno local usando Docker.

El proyecto está orientado a demostrar:

- **Backend engineering** con Python y FastAPI.
- **Clean code**: SOLID, DRY, PEP8/PEP257.
- **Test-Driven Development (TDD)** como metodología central.
- **DevOps**: Docker, CI/CD, infraestructura como código.

---

## Metodología: Test-Driven Development (TDD)

Cada fase de desarrollo sigue el ciclo:

1. **Red**: Escribir tests que fallen.
2. **Green**: Implementar el código mínimo para pasar los tests.
3. **Refactor**: Mejorar el código manteniendo los tests verdes.

Herramientas de testing:

- `pytest` + `pytest-cov` (cobertura).
- `pytest-asyncio` (tests asíncronos).
- `httpx` (tests de API).
- `testcontainers` (integración con Docker).

---

## Fase 0 — Diseño y arquitectura

**Objetivo:** Definir el sistema antes de implementar.

Tareas:

- Definición del dominio (instrumentos, series temporales).
- Selección del stack tecnológico.
- Diseño de flujos de datos (ETL).
- Diseño de estructura del repositorio.
- Documentación de principios (SOLID, DRY, PEP).

**Entregables:**

- `architecture.md`
- `CONTRIBUTING.md` (convenciones de código)
- Estructura base del proyecto

---

## Fase 1 — Setup del proyecto

**Objetivo:** Configurar el entorno de desarrollo profesional.

Tareas:

- Inicialización del repositorio (GitHub).
- Configuración de `pyproject.toml`:
  - Dependencias (producción y desarrollo).
  - Metadata del proyecto.
- Configuración de herramientas de calidad:
  - `ruff` (linting + formatting).
  - `mypy` (type checking).
  - `pytest` (testing).
- Configuración de `pre-commit` hooks.
- Creación del `Makefile` para automatización.
- Estructura inicial de directorios (`src/`, `tests/`).

**Entregables:**

- Proyecto Python configurado y listo para desarrollo.
- Pipeline de calidad funcional (lint, format, type-check).
- Tests ejecutables (aunque vacíos).

---

## Fase 2 — Backend base (FastAPI) e Infraestructura de Testing

**Objetivo:** Construir el núcleo del servicio con TDD.

Tareas:

- **Tests primero**: Escribir tests para `/health` endpoint.
- Inicialización de la aplicación FastAPI.
- Configuración tipada con `pydantic-settings`.
- Logging estructurado (`structlog` o `loguru`).
- Estructura modular (`api/`, `core/`, `services/`).
- Manejo de errores centralizado.

**Principios aplicados:**

- Single Responsibility (endpoints delgados).
- Dependency Injection (FastAPI `Depends`).
- Configuration as code.

**Entregables:**

- API mínima funcional con `/health`.
- Tests unitarios pasando.
- Cobertura de código establecida.

---

## Fase 3 — Modelado, Persistencia y Autenticación (JWT/Sesiones)

**Objetivo:** Definir el dominio de datos con TDD.

Tareas:

- **Tests primero**: Tests de modelos y repositorios.
- Modelos SQLAlchemy:
  - `Instrument`
  - `MarketPrice`
  - `User` (Gestión de usuarios administradores)
- Schemas Pydantic (separados de modelos).
- Implementación de Repository pattern.
- Sistema de Autenticación con JWT (Token y Login).
- Configuración de Alembic.
- Migraciones iniciales.

**Principios aplicados:**

- Dependency Inversion (Repository abstraction).
- Open/Closed (extensibilidad de repositorios).

**Entregables:**

- Esquema de base de datos versionado.
- Repositorios testeados.
- Migraciones reproducibles.

---

## Fase 4 — Ingestión de datos (ETL)

**Objetivo:** Poblar el sistema con datos reales.

Tareas:

- **Tests primero**: Tests de clientes API y transformadores.
- Implementación de clientes de API externas.
- Normalización de datos.
- Inserción idempotente.
- Logging estructurado de operaciones.

Activación de ingestión (elegir una):

- **Opción A: Automatizada** — APScheduler ejecuta ingestión cada X minutos.
  - Ideal para backends sin intervención manual.
  - Scheduler se inicia con FastAPI.
- **Opción B: Manual** — Endpoint `/ingest/run` dispara ingestión bajo demanda.
  - Ideal para control explícito desde UI o herramientas externas.

**Principios aplicados:**

- Interface Segregation (clientes especializados).
- DRY (transformadores reutilizables).

**Entregables:**

- ETL funcional y testeado.
- Datos históricos persistidos.

---

## Fase 5 — API REST de consulta

**Objetivo:** Exponer los datos como servicio.

Tareas:

- **Tests primero**: Tests de endpoints con datos mock.
- Endpoints:
  - Listado de instrumentos.
  - Consulta de precios por instrumento.
  - Consulta por rango temporal.
- Validación de parámetros.
- Paginación.
- Manejo de errores HTTP.

**Entregables:**

- API REST completa y testeada.
- Documentación OpenAPI generada.
- Contratos claros de datos.

---

## Fase 6 — Visualización con Grafana

**Objetivo:** Análisis y observabilidad.

Tareas:

- Configuración de datasource PostgreSQL.
- Dashboards:
  - Evolución temporal.
  - Comparativas.
  - KPIs básicos.
- Versionado de dashboards en JSON.

**Entregables:**

- Dashboards funcionales.
- Configuración exportable.

---

## Fase 7 — Dockerización y despliegue local

**Objetivo:** Entorno reproducible y portable.

Tareas:

- Dockerfile multi-stage del backend.
- Docker Compose con:
  - API FastAPI
  - PostgreSQL / TimescaleDB
  - Grafana
- Health checks de contenedores.
- Variables de entorno centralizadas.
- Scripts de arranque.

**Entregables:**

- `docker-compose.yml`
- Sistema levantable con un solo comando.
- Tests de integración con contenedores.

---

## Fase 8 — CI/CD y documentación final (GitHub Actions)

**Objetivo:** Proyecto publicable y defendible.

Tareas:

- GitHub Actions:
  - Lint + Type check (`black`, `isort`, `pylint`, `mypy`).
  - Tests unitarios + Coverage (`pytest --cov-fail-under=85`).
  - Build Docker image.
- README principal profesional.
- Documentación en `docs/`.
- Diagramas actualizados.
- Badges de calidad.

**Entregables:**

- Pipeline CI/CD funcional.
- Proyecto listo para GitHub.
- Repositorio profesional.

---

## Estado del proyecto

- [x] Fase 0 — Diseño y arquitectura
- [x] Fase 1 — Setup del proyecto
- [x] Fase 2 — Backend base (FastAPI) e Infraestructura de Testing
- [x] Fase 3 — Modelado, Persistencia y Autenticación (JWT/Sesiones)
- [x] Fase 4 — Ingestión de datos (ETL)
- [x] Fase 5 — API REST de consulta
- [x] Fase 6 — Visualización con Grafana
- [x] Fase 7 — Dockerización y despliegue local
- [x] Fase 8 — CI/CD y documentación final (GitHub Actions)
