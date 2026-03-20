# ============================================================
#  PropSync — Backend Makefile (Windows Command Prompt)
# ============================================================
#  Prerequisites: Python 3.11+, pip
#  Usage: make <target>
# ============================================================

VENV        = .venv
PYTHON      = $(VENV)\Scripts\python.exe
PIP         = $(VENV)\Scripts\pip.exe
UVICORN     = $(VENV)\Scripts\uvicorn.exe
ALEMBIC     = $(VENV)\Scripts\alembic.exe

APP         = app.main:app
HOST        = 127.0.0.1
PORT        = 8000

.PHONY: help setup install env migrate makemigrations \
        db-reset db-downgrade dev run clean lint

# ── Default target ──────────────────────────────────────────
help:
	@echo.
	@echo  PropSync Backend — available commands:
	@echo  ─────────────────────────────────────────────────────
	@echo  make setup           Full first-time setup (venv + deps + .env)
	@echo  make install         Install / refresh Python dependencies
	@echo  make env             Copy .env.example to .env (skip if exists)
	@echo  make migrate         Apply all pending DB migrations
	@echo  make makemigrations  Auto-generate a new migration (MSG=your_message)
	@echo  make db-reset        Downgrade to base then re-apply all migrations
	@echo  make db-downgrade    Downgrade one migration step
	@echo  make dev             Start dev server with hot-reload
	@echo  make run             Start production server (no reload)
	@echo  make clean           Remove .venv, __pycache__, .pyc files
	@echo  ─────────────────────────────────────────────────────
	@echo.

# ── Full first-time setup ───────────────────────────────────
setup: env _venv install
	@echo.
	@echo  [OK] Setup complete.
	@echo  Next: edit .env with your credentials, then run:
	@echo        make migrate
	@echo        make dev
	@echo.

# ── Create .env from example (skip if .env already exists) ──
env:
	@if not exist .env ( \
		copy .env.example .env > nul && \
		echo  [OK] .env created — fill in your credentials before running. \
	) else ( \
		echo  [SKIP] .env already exists. \
	)

# ── Create virtual environment ──────────────────────────────
_venv:
	@if not exist $(VENV) ( \
		echo  [..] Creating virtual environment... && \
		python -m venv $(VENV) && \
		echo  [OK] Virtual environment created at $(VENV) \
	) else ( \
		echo  [SKIP] Virtual environment already exists. \
	)

# ── Install / refresh dependencies ──────────────────────────
install: _venv
	@echo  [..] Upgrading pip ...
	@$(PYTHON) -m pip install --upgrade pip -q
	@echo  [..] Installing dependencies from requirements.txt ...
	@$(PYTHON) -m pip install -r requirements.txt
	@echo  [OK] Dependencies installed.

# ── Database migrations ─────────────────────────────────────
migrate: _check_env
	@echo  [..] Applying DB migrations ...
	@$(ALEMBIC) upgrade head
	@echo  [OK] Migrations applied.

# Usage: make makemigrations MSG="add_index_to_events"
makemigrations: _check_env
	@if "$(MSG)"=="" ( \
		echo  [ERROR] Provide a message: make makemigrations MSG="describe_change" \
	) else ( \
		$(ALEMBIC) revision --autogenerate -m "$(MSG)" && \
		echo  [OK] Migration file created. \
	)

db-downgrade: _check_env
	@echo  [..] Downgrading one step ...
	@$(ALEMBIC) downgrade -1
	@echo  [OK] Downgraded one step.

db-reset: _check_env
	@echo  [WARN] Resetting DB — this will drop and recreate all tables.
	@$(ALEMBIC) downgrade base
	@$(ALEMBIC) upgrade head
	@echo  [OK] DB reset complete.

# ── Dev server (hot-reload) ──────────────────────────────────
dev: _check_env
	@echo  [..] Starting dev server at http://$(HOST):$(PORT) ...
	@$(UVICORN) $(APP) --host $(HOST) --port $(PORT) --reload

# ── Production server ────────────────────────────────────────
run: _check_env
	@echo  [..] Starting server at http://$(HOST):$(PORT) ...
	@$(UVICORN) $(APP) --host $(HOST) --port $(PORT) --workers 2

# ── Clean build artefacts ────────────────────────────────────
clean:
	@echo  [..] Cleaning up ...
	@if exist $(VENV) ( rmdir /s /q $(VENV) && echo  [OK] Removed $(VENV) )
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@del /s /q *.pyc 2>nul
	@echo  [OK] Clean complete.

# ── Internal guard — ensure .env exists ─────────────────────
_check_env:
	@if not exist .env ( \
		echo  [ERROR] .env not found. Run: make env && exit 1 \
	)
