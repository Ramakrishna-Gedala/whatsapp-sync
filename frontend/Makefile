# ============================================================
#  PropSync — Frontend Makefile (Windows Command Prompt)
# ============================================================
#  Prerequisites: Node.js 18+, npm
#  Usage: make <target>
# ============================================================

NODE_MODULES = node_modules
NPM          = npm

.PHONY: help setup install env dev build preview clean lint

# ── Default target ──────────────────────────────────────────
help:
	@echo.
	@echo  PropSync Frontend — available commands:
	@echo  ─────────────────────────────────────────────────────
	@echo  make setup     Full first-time setup (deps + .env)
	@echo  make install   Install / refresh Node dependencies
	@echo  make env       Copy .env.example to .env (skip if exists)
	@echo  make dev       Start Vite dev server  (http://localhost:5173)
	@echo  make build     Production build into dist/
	@echo  make preview   Serve the production build locally
	@echo  make clean     Remove node_modules and dist/
	@echo  ─────────────────────────────────────────────────────
	@echo.

# ── Full first-time setup ───────────────────────────────────
setup: env install
	@echo.
	@echo  [OK] Frontend setup complete.
	@echo  Run: make dev
	@echo.

# ── Copy .env (skip if already exists) ──────────────────────
env:
	@if not exist .env ( \
		copy .env.example .env > nul && \
		echo  [OK] .env created. \
	) else ( \
		echo  [SKIP] .env already exists. \
	)

# ── Install Node dependencies ────────────────────────────────
install:
	@echo  [..] Installing Node dependencies ...
	@$(NPM) install
	@echo  [OK] Dependencies installed.

# ── Dev server ───────────────────────────────────────────────
dev: _check_env _check_modules
	@echo  [..] Starting Vite dev server at http://localhost:5173 ...
	@$(NPM) run dev

# ── Production build ─────────────────────────────────────────
build: _check_env _check_modules
	@echo  [..] Building for production ...
	@$(NPM) run build
	@echo  [OK] Build output in dist\

# ── Serve production build locally ──────────────────────────
preview: _check_env
	@if not exist dist ( \
		echo  [ERROR] No dist\ folder found. Run: make build && exit 1 \
	)
	@echo  [..] Serving production build ...
	@$(NPM) run preview

# ── Clean artefacts ──────────────────────────────────────────
clean:
	@echo  [..] Cleaning up ...
	@if exist $(NODE_MODULES) ( rmdir /s /q $(NODE_MODULES) && echo  [OK] Removed node_modules )
	@if exist dist             ( rmdir /s /q dist            && echo  [OK] Removed dist )
	@echo  [OK] Clean complete.

# ── Internal guards ──────────────────────────────────────────
_check_env:
	@if not exist .env ( \
		echo  [ERROR] .env not found. Run: make env && exit 1 \
	)

_check_modules:
	@if not exist $(NODE_MODULES) ( \
		echo  [ERROR] node_modules not found. Run: make install && exit 1 \
	)
