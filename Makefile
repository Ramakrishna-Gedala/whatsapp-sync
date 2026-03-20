# ============================================================
#  PropSync — Root Makefile (Windows Command Prompt)
# ============================================================
#  Delegates to backend\ and frontend\ Makefiles.
#  Prerequisites: Python 3.11+, Node.js 18+, make
#  Usage: make <target>
# ============================================================

.PHONY: help setup setup-backend setup-frontend \
        install install-backend install-frontend \
        dev-backend dev-frontend \
        migrate makemigrations db-reset \
        build clean-backend clean-frontend clean

# ── Default target ──────────────────────────────────────────
help:
	@echo.
	@echo  PropSync — Root commands (delegates to backend\ and frontend\)
	@echo  ─────────────────────────────────────────────────────────────────
	@echo.
	@echo  SETUP
	@echo    make setup              First-time setup for both projects
	@echo    make setup-backend      First-time setup for backend only
	@echo    make setup-frontend     First-time setup for frontend only
	@echo.
	@echo  INSTALL
	@echo    make install            Install deps for both projects
	@echo    make install-backend    Install Python deps only
	@echo    make install-frontend   Install Node deps only
	@echo.
	@echo  DATABASE  (backend)
	@echo    make migrate            Apply all pending DB migrations
	@echo    make makemigrations     Generate migration  MSG="your_message"
	@echo    make db-reset           Drop + re-apply all migrations
	@echo.
	@echo  DEV SERVERS
	@echo    make dev-backend        uvicorn  →  http://localhost:8000
	@echo    make dev-frontend       vite     →  http://localhost:5173
	@echo    (open two terminals and run both simultaneously)
	@echo.
	@echo  BUILD  (frontend)
	@echo    make build              Production build into frontend\dist\
	@echo.
	@echo  CLEAN
	@echo    make clean              Remove .venv, node_modules, dist, caches
	@echo    make clean-backend      Backend only
	@echo    make clean-frontend     Frontend only
	@echo  ─────────────────────────────────────────────────────────────────
	@echo.

# ── Setup ───────────────────────────────────────────────────
setup: setup-backend setup-frontend
	@echo.
	@echo  ========================================================
	@echo   All done! Edit credentials in:
	@echo     backend\.env
	@echo     frontend\.env
	@echo   Then run the DB migration:
	@echo     make migrate
	@echo   And start the dev servers (two terminals):
	@echo     make dev-backend
	@echo     make dev-frontend
	@echo  ========================================================
	@echo.

setup-backend:
	@echo  [..] Setting up backend ...
	@cd backend && $(MAKE) setup

setup-frontend:
	@echo  [..] Setting up frontend ...
	@cd frontend && $(MAKE) setup

# ── Install ─────────────────────────────────────────────────
install: install-backend install-frontend

install-backend:
	@cd backend && $(MAKE) install

install-frontend:
	@cd frontend && $(MAKE) install

# ── Database ─────────────────────────────────────────────────
migrate:
	@cd backend && $(MAKE) migrate

makemigrations:
	@cd backend && $(MAKE) makemigrations MSG="$(MSG)"

db-reset:
	@cd backend && $(MAKE) db-reset

# ── Dev servers ──────────────────────────────────────────────
dev-backend:
	@cd backend && $(MAKE) dev

dev-frontend:
	@cd frontend && $(MAKE) dev

# ── Build ────────────────────────────────────────────────────
build:
	@cd frontend && $(MAKE) build

# ── Clean ────────────────────────────────────────────────────
clean: clean-backend clean-frontend

clean-backend:
	@cd backend && $(MAKE) clean

clean-frontend:
	@cd frontend && $(MAKE) clean
