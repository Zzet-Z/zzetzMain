.PHONY: install dev-backend dev-frontend test test-backend test-frontend build check

# ── 安装 ──────────────────────────────────────────────
install:
	cd backend && pip install -e .
	cd frontend && npm install

# ── 开发服务器 ────────────────────────────────────────
dev-backend:
	cd backend && python run.py

dev-frontend:
	cd frontend && npm run dev

# ── 测试 ──────────────────────────────────────────────
test-backend:
	cd backend && pytest -q

test-frontend:
	cd frontend && npm test

test: test-backend test-frontend

# ── 构建 ──────────────────────────────────────────────
build:
	cd frontend && npm run build

# ── 全量检查（CI 等价） ───────────────────────────────
check: test build
	@echo "✓ All checks passed"
