# Stack Research

**Domain:** Hotel Reservation Application (Full-Stack Web)
**Researched:** 2026-03-20
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12+ | Backend runtime | Stable, well-supported; 3.13 has breaking changes with some libs. 3.12 is the safe production choice. |
| FastAPI | 0.135.x | API framework | Async-first, automatic OpenAPI docs, Pydantic-native validation. Best modern Python API framework for portfolio visibility. |
| React | 19.2.x | Frontend UI | Industry standard. v19 brings improved server components and Activity API. Massive ecosystem. |
| PostgreSQL | 16+ | Database | Production-grade relational DB. Perfect for reservation data with date ranges, constraints, and transactional integrity. |
| Node.js | 20 LTS / 22 LTS | Frontend toolchain | Required for Vite, npm ecosystem. Use LTS for stability. |

### Backend Libraries

| Library | Version | Purpose | Why This One |
|---------|---------|---------|--------------|
| SQLAlchemy | 2.0.48 | ORM / query builder | Industry standard Python ORM. v2.0 has modern async support, type-safe query API. Use with asyncpg driver for async PostgreSQL. |
| Alembic | 1.18.x | Database migrations | The only serious migration tool for SQLAlchemy. Auto-generates migrations from model diffs. |
| asyncpg | latest | PostgreSQL async driver | 5x faster than psycopg3 in benchmarks. Purpose-built for asyncio. Use as SQLAlchemy's async backend. |
| Pydantic | 2.12.x | Data validation / schemas | Ships with FastAPI. v2 is dramatically faster than v1. Drives request/response validation and settings management. |
| pydantic-settings | 2.x | Configuration management | Environment variable loading, .env file support. Clean separation of config from code. |
| pwdlib[argon2] | latest | Password hashing | Modern replacement for passlib (which is dead and breaks on Python 3.13). Argon2 is the recommended algorithm per OWASP. FastAPI docs now recommend this over passlib/bcrypt. |
| PyJWT | 2.x | JWT token handling | Lightweight, well-maintained. FastAPI docs use it directly. Avoid python-jose (unmaintained). |
| httpx | latest | HTTP client | Ships with FastAPI. Used for async HTTP requests and as the test client (AsyncClient). |
| fastapi-mail | latest | Email sending | Async email with Jinja2 templates. Perfect for booking confirmations. For mock emails, configure with a local SMTP or just log. |
| uvicorn | latest | ASGI server | Standard production server for FastAPI. Use with --workers for multi-process deployment. |

### Frontend Libraries

| Library | Version | Purpose | Why This One |
|---------|---------|---------|--------------|
| Vite | 8.x | Build tool / dev server | Rust-based bundler (Rolldown) in v8: 10-30x faster builds. Native React support. The standard for new React projects in 2026. |
| React Router | 7.13.x | Client-side routing | Standard React routing. v7 merged with Remix but works fine as a pure SPA router. Use declarative routes. |
| TanStack Query | 5.x (@tanstack/react-query) | Server state management | Handles caching, background refetching, optimistic updates. Eliminates manual loading/error state management for API calls. Essential for reservation data freshness. |
| Zustand | 5.x | Client state management | 1KB, hook-based, zero boilerplate. For UI state like modals, filters, booking wizard step. Do NOT use for server data (that is TanStack Query's job). |
| React Hook Form | 7.71.x | Form handling | Uncontrolled components = minimal re-renders. Critical for the multi-step booking form and admin forms. |
| Zod | 4.x | Schema validation | TypeScript-first validation. Shares validation logic between forms (via @hookform/resolvers) and API response parsing. Single source of truth for data shapes. |
| @hookform/resolvers | latest | Form + Zod bridge | Connects Zod schemas to React Hook Form. Automatic type inference. |
| Tailwind CSS | 4.x | Styling | Utility-first CSS. v4 is 5x faster builds, zero-config setup. Pairs with shadcn/ui. Industry standard for new React projects. |
| shadcn/ui | latest | UI components | Copy-paste components built on Radix UI + Tailwind. Full code ownership, accessible by default (ARIA, keyboard nav). Not a dependency -- source code lives in your project. |
| date-fns | 4.x | Date manipulation | Tree-shakeable, functional API. Better for TypeScript projects than Day.js. Reservation apps are date-heavy -- need reliable date math for availability, ranges, formatting. |
| Axios | 1.x | HTTP client | Cleaner API than fetch for request/response interceptors (auth token injection, error handling). Pairs well with TanStack Query. |

### Development & Testing Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| pytest 8.3.x | Backend testing | Standard Python testing framework. Use with pytest-asyncio for async test support. |
| pytest-asyncio | Async test support | Required for testing async FastAPI endpoints and database operations. |
| httpx (AsyncClient) | API integration tests | FastAPI's recommended approach for testing async endpoints. Replaces TestClient for async. |
| Vitest 4.x | Frontend testing | Vite-native test runner. 2-5x faster than Jest. Use with React Testing Library. |
| @testing-library/react | Component testing | Tests components like users interact with them. Standard for React testing. |
| Playwright | E2E testing | Cross-browser E2E tests. More reliable than Cypress, better async handling. |
| Ruff | Python linting + formatting | Replaces flake8, black, isort in one tool. 10-100x faster (Rust-based). The standard Python linter in 2026. |
| ESLint 9.x + Prettier | Frontend linting + formatting | ESLint for logic errors, Prettier for formatting. Use flat config (eslint.config.js). |
| Docker + Docker Compose | Containerization | PostgreSQL in dev, consistent environments, deployment packaging. |
| pre-commit | Git hooks | Run Ruff, ESLint, type checks before commit. Catches issues early. |

### Infrastructure

| Technology | Purpose | Why Recommended |
|------------|---------|-----------------|
| Docker Compose | Local development | Run PostgreSQL, optionally Redis and MailHog, with one command. Reproducible dev environment. |
| Alembic | Schema management | Version-controlled database migrations. Auto-generate from SQLAlchemy model changes. |
| GitHub Actions | CI/CD | Free for public repos. Run tests, lint, build, deploy on every push. Portfolio-friendly visibility. |
| Railway or Render | Deployment | Free/cheap tiers for portfolio projects. PostgreSQL included. Simpler than AWS for a single-property hotel app. |

## Installation

```bash
# Backend setup
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

pip install fastapi[standard] uvicorn[standard]
pip install sqlalchemy[asyncio] asyncpg alembic
pip install pydantic-settings
pip install "pwdlib[argon2]" PyJWT
pip install fastapi-mail
pip install httpx

# Dev dependencies
pip install pytest pytest-asyncio pytest-cov
pip install ruff pre-commit

# Frontend setup
npm create vite@latest frontend -- --template react-ts
cd frontend

npm install react-router react-router-dom
npm install @tanstack/react-query
npm install zustand
npm install react-hook-form @hookform/resolvers zod
npm install axios
npm install date-fns
npm install tailwindcss @tailwindcss/vite

# shadcn/ui (run after Tailwind is configured)
npx shadcn@latest init

# Dev dependencies
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
npm install -D eslint prettier
npm install -D @playwright/test
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| asyncpg | psycopg3 | If you prefer a single driver for sync+async, or need advanced PostgreSQL features like COPY. psycopg3 is simpler but ~5x slower async. |
| Zustand | Redux Toolkit | If the app grows to enterprise scale with complex state interactions needing time-travel debugging. Overkill for this project. |
| TanStack Query | SWR | If you want a simpler API with fewer features. TanStack Query's devtools and mutation support are better for reservation workflows. |
| date-fns | Day.js | If bundle size is critical (2KB vs ~18KB). Day.js has a Moment-like chaining API. date-fns is better for tree-shaking and TypeScript. |
| Tailwind + shadcn/ui | Material UI (MUI) | If you need a pre-built design system with minimal customization. MUI is heavier and harder to customize deeply. shadcn/ui gives full control. |
| Vitest | Jest | If your project does not use Vite. Vitest is Vite-native and 2-5x faster. No reason to use Jest with Vite in 2026. |
| Ruff | flake8 + black + isort | Never. Ruff replaces all three, is 100x faster, and is the community standard. |
| Railway/Render | AWS/GCP | If you need fine-grained infrastructure control or multi-region deployment. Overkill for a portfolio single-property hotel app. |
| pwdlib + Argon2 | passlib + bcrypt | Never for new projects. passlib is unmaintained and breaks on Python 3.13+. FastAPI docs have migrated away from it. |
| PyJWT | python-jose | Never. python-jose is unmaintained. PyJWT is actively maintained and simpler. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| passlib | Unmaintained, breaks on Python 3.13+. No longer recommended by FastAPI docs. | pwdlib[argon2] |
| python-jose | Unmaintained. Security risk for JWT handling. | PyJWT |
| Django / Django REST Framework | Monolithic, opinionated. Doesn't showcase modern async Python patterns that FastAPI demonstrates. Over-engineered for an API-first SPA. | FastAPI |
| SQLAlchemy 1.x patterns | Legacy API. v2.0 has a completely new query syntax. Old tutorials will lead you astray. | SQLAlchemy 2.0 style (select() statements, not query()) |
| Create React App (CRA) | Officially deprecated. No longer maintained. Slow builds. | Vite |
| Jest (with Vite projects) | Requires complex configuration to work with Vite. Slower. | Vitest |
| Moment.js | Deprecated by its own maintainers. Massive bundle size (300KB+). | date-fns |
| Redux (vanilla) | Excessive boilerplate. Even Redux Toolkit is overkill for this project's client state needs. | Zustand for client state, TanStack Query for server state |
| CSS Modules / Styled Components | More complex setup, harder to maintain consistency. Tailwind is the industry direction. | Tailwind CSS + shadcn/ui |
| Tortoise ORM | Smaller ecosystem, less documentation, fewer migration tools than SQLAlchemy. | SQLAlchemy 2.0 with async |

## Stack Patterns by Variant

**For the booking flow (guest-facing):**
- Use TanStack Query for availability checks (automatic cache invalidation ensures fresh data)
- Use Zustand for booking wizard state (step tracking, selected room, guest details in progress)
- Use React Hook Form + Zod for the multi-step form (guest details, payment info)
- Use date-fns for date range selection and display formatting

**For the staff dashboard:**
- Use TanStack Query with polling for live booking updates
- Use shadcn/ui data tables for booking lists, guest history, reports
- Use Zustand for dashboard UI state (filters, selected date range, active tab)

**For authentication:**
- Use FastAPI's built-in OAuth2PasswordBearer dependency
- Use PyJWT for token creation/verification
- Use pwdlib with Argon2 for password hashing
- Store JWT in httpOnly cookies (not localStorage) for security
- Implement refresh token rotation for session management

**For the mock payment flow:**
- Build a Stripe-like API interface (same request/response shapes)
- Use a local "payment service" module that always succeeds with realistic delays
- This pattern lets you swap in real Stripe later by replacing one module

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| FastAPI 0.135.x | Pydantic 2.12.x | FastAPI requires Pydantic v2. Do NOT use Pydantic v1. |
| SQLAlchemy 2.0.48 | asyncpg (latest) | Use `create_async_engine` with `postgresql+asyncpg://` connection string. |
| SQLAlchemy 2.0.48 | Alembic 1.18.x | Alembic auto-detects SQLAlchemy version. Use `--async` flag for async migration env. |
| Vite 8.x | Vitest 4.x | Vitest 4 requires Vite 8. They share config. |
| React 19.2.x | React Router 7.13.x | Full compatibility. Use `react-router` package (not separate `react-router-dom` in v7). |
| React Hook Form 7.71.x | Zod 4.x + @hookform/resolvers | Ensure @hookform/resolvers supports Zod 4. Check resolvers changelog if issues arise. |
| Tailwind CSS 4.x | shadcn/ui | shadcn/ui v2 supports Tailwind v4. Run `npx shadcn@latest init` after Tailwind setup. |
| Python 3.12 | All backend packages | Safest choice. Python 3.13 may have edge-case issues with some C extensions. |

## Sources

- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/) -- FastAPI 0.135.x version confirmed
- [FastAPI JWT Tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) -- PyJWT + pwdlib recommended over passlib
- [SQLAlchemy Download](https://www.sqlalchemy.org/download.html) -- SQLAlchemy 2.0.48 confirmed
- [Alembic Documentation](https://alembic.sqlalchemy.org/) -- Alembic 1.18.4 confirmed
- [React Versions](https://react.dev/versions) -- React 19.2.x confirmed
- [Vite 8.0 Announcement](https://vite.dev/blog/announcing-vite8) -- Vite 8 with Rolldown bundler
- [React Router Changelog](https://reactrouter.com/changelog) -- v7.13.x confirmed
- [TanStack Query](https://tanstack.com/query/latest) -- v5.91.x for React
- [Zustand npm](https://www.npmjs.com/package/zustand) -- v5.0.12 confirmed
- [React Hook Form npm](https://www.npmjs.com/package/react-hook-form) -- v7.71.2 confirmed
- [Zod npm](https://www.npmjs.com/package/zod) -- v4.3.6 confirmed
- [Tailwind CSS v4](https://tailwindcss.com/blog/tailwindcss-v4) -- v4.0 confirmed
- [shadcn/ui](https://ui.shadcn.com/) -- component library on Radix + Tailwind
- [Vitest](https://vitest.dev/) -- v4.1.0 confirmed
- [pwdlib PyPI](https://pypi.org/project/pwdlib/) -- modern passlib replacement
- [pytest PyPI](https://pypi.org/project/pytest/) -- v8.3.4 confirmed
- [Psycopg 3 vs Asyncpg](https://fernandoarteaga.dev/blog/psycopg-vs-asyncpg/) -- asyncpg 5x faster benchmark

---
*Stack research for: Hotel Reservation Application (HotelBook)*
*Researched: 2026-03-20*
