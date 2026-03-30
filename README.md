# WhatsApp Sync — Event Management Platform

A full-stack application that ingests messages from WhatsApp groups, leverages OpenAI-based LLMs for intelligent event extraction, and transforms unstructured conversations into structured, actionable events presented through a centralized dashboard for property managers.

---

## System Architecture

```
┌───────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│   WhatsApp        │     │   Manual Input     │     │  File Upload     │
│   (Green API)     │     │   (Chat UI)        │     │  (.txt exports)  │
└────────┬──────────┘     └────────┬───────────┘     └────────┬─────────┘
         │                         │                           │
         └─────────────────────────┼───────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │     FastAPI Backend          │
                    │     (Python 3.11+)           │
                    │                              │
                    │  ┌────────────────────────┐  │
                    │  │    Router Layer         │  │
                    │  │  /groups  /events       │  │
                    │  │  /chat   /upload        │  │
                    │  └───────────┬────────────┘  │
                    │              │                │
                    │  ┌───────────▼────────────┐  │
                    │  │    Service Layer        │  │
                    │  │                         │  │
                    │  │  GreenAPIService ───────│──│──► Green API (WhatsApp)
                    │  │  OpenAIService ────────│──│──► OpenAI (GPT-4o-mini)
                    │  │  EventService          │  │
                    │  │  MessageProcessor      │  │
                    │  │  FileUploadService      │  │
                    │  │  FileParserFactory      │  │
                    │  └───────────┬────────────┘  │
                    │              │                │
                    │  ┌───────────▼────────────┐  │
                    │  │  SQLAlchemy Async ORM   │  │
                    │  │  (asyncpg driver)       │  │
                    │  └───────────┬────────────┘  │
                    └──────────────┼────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │       PostgreSQL             │
                    │   whatsapp_realestate DB     │
                    │                              │
                    │  ┌─────────────────────┐     │
                    │  │  whatsapp_groups     │     │
                    │  │  whatsapp_messages   │     │
                    │  │  events              │     │
                    │  └─────────────────────┘     │
                    └─────────────────────────────┘
                                   ▲
                                   │ REST API (JSON)
                                   │ http://localhost:8000/api/v1
                                   │
                    ┌──────────────┴──────────────┐
                    │     React Frontend           │
                    │     (TypeScript + Vite)       │
                    │                              │
                    │  ┌────────────────────────┐  │
                    │  │  Axios + React Query    │  │
                    │  │  (API + caching layer)  │  │
                    │  └───────────┬────────────┘  │
                    │              │                │
                    │  ┌───────────▼────────────┐  │
                    │  │  Zustand Stores         │  │
                    │  │  (UI state mgmt)        │  │
                    │  └───────────┬────────────┘  │
                    │              │                │
                    │  ┌───────────▼────────────┐  │
                    │  │  React Components       │  │
                    │  │  + Radix UI + Tailwind  │  │
                    │  └────────────────────────┘  │
                    │                              │
                    │  http://localhost:5173        │
                    └──────────────────────────────┘
```

---

## Tech Stack Overview

### Backend

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Framework | FastAPI 0.111+ |
| Server | Uvicorn (ASGI) |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL (asyncpg) |
| Migrations | Alembic |
| Validation | Pydantic 2.7+ |
| HTTP Client | httpx (async) |

### Frontend

| Component | Technology |
|-----------|-----------|
| Language | TypeScript 5.4 |
| Framework | React 18.3 |
| Build | Vite 5.3 |
| Routing | React Router 6.24 |
| State | Zustand 4.5 |
| Data Fetching | TanStack React Query 5.45 |
| HTTP Client | Axios 1.7 |
| CSS | Tailwind CSS 3.4 |
| UI Primitives | Radix UI |
| Icons | Lucide React |

### External Services

| Service | Purpose | Model/Plan |
|---------|---------|------------|
| [Green API](https://green-api.com/) | WhatsApp Business integration | Instance-based |
| [OpenAI](https://openai.com/) | Message parsing & event extraction | GPT-4o-mini |

---

## Database Schema & Relationships

### Entity Relationship Diagram

```
┌─────────────────────────────┐
│       whatsapp_groups       │
├─────────────────────────────┤
│ PK  id          VARCHAR(36) │
│ UQ  group_id    VARCHAR(100)│◄─────────────────────────────────┐
│     name        VARCHAR(255)│                                  │
│     description TEXT         │                                  │
│     created_at  TIMESTAMPTZ │                                  │
│     updated_at  TIMESTAMPTZ │                                  │
└─────────────────────────────┘                                  │
         │                                                       │
         │ 1:N                                                   │ 1:N
         │                                                       │
         ▼                                                       │
┌─────────────────────────────────┐                              │
│       whatsapp_messages         │                              │
├─────────────────────────────────┤                              │
│ PK  id                  VARCHAR(36)  │                         │
│ UQ  whatsapp_message_id VARCHAR(100) │◄──────────┐            │
│ FK  group_id            VARCHAR(100) │───────────│────────────┘
│     sender_id           VARCHAR(100) │           │
│     sender_name         VARCHAR(255) │           │
│     message_type        ENUM         │           │
│     raw_content         TEXT         │           │
│     media_url           TEXT         │           │
│     media_mime_type     VARCHAR(100) │           │
│     source              ENUM         │           │
│     language            VARCHAR(10)  │           │
│     processed           BOOLEAN      │           │
│     processed_at        TIMESTAMPTZ  │           │
│     whatsapp_timestamp  INTEGER      │           │
│     created_at          TIMESTAMPTZ  │           │
└─────────────────────────────────┘    │           │
                                       │ 1:1       │
                                       │           │
                                       ▼           │
┌──────────────────────────────────┐               │
│            events                │               │
├──────────────────────────────────┤               │
│ PK  id                VARCHAR(36)    │           │
│ FK  whatsapp_message_id VARCHAR(100) │───────────┘
│ FK  group_id          VARCHAR(100)   │──── (to whatsapp_groups.group_id)
│     event_type        ENUM           │
│     priority          ENUM           │
│     status            ENUM           │
│     title             VARCHAR(500)   │
│     description       TEXT           │
│     tenant_id         VARCHAR(100)   │
│     tenant_name       VARCHAR(255)   │
│     property_id       VARCHAR(100)   │
│     community_id      VARCHAR(100)   │
│     address           TEXT           │
│     ai_confidence     FLOAT          │
│     raw_ai_response   JSONB          │
│     source            ENUM           │
│     created_at        TIMESTAMPTZ    │
│     updated_at        TIMESTAMPTZ    │
└──────────────────────────────────┘
```

### Table Relationships

| Relationship | Type | FK Column | References | On Delete |
|-------------|------|-----------|------------|-----------|
| Group → Messages | 1:N | `whatsapp_messages.group_id` | `whatsapp_groups.group_id` | — |
| Group → Events | 1:N | `events.group_id` | `whatsapp_groups.group_id` | — |
| Message → Event | 1:1 | `events.whatsapp_message_id` | `whatsapp_messages.whatsapp_message_id` | CASCADE |

### Enum Types

**MessageType:** `text`, `image`, `audio`, `video`, `document`, `location`

**MessageSource / EventSource:** `whatsapp_group`, `manual_chat`, `file_upload`

**EventType:** `maintenance_request`, `lease_inquiry`, `payment_issue`, `move_in`, `move_out`, `noise_complaint`, `safety_concern`, `amenity_request`, `general_inquiry`, `other`

**Priority:** `low`, `medium`, `high`, `urgent`

**EventStatus:** `open`, `in_progress`, `resolved`, `closed`

### Key Indexes

| Table | Index | Column(s) | Type |
|-------|-------|-----------|------|
| whatsapp_groups | unique | `group_id` | Unique |
| whatsapp_messages | unique | `whatsapp_message_id` | Unique |
| whatsapp_messages | idx | `group_id` | B-tree |
| whatsapp_messages | idx | `processed` | B-tree |
| events | unique | `whatsapp_message_id` | Unique |
| events | idx | `group_id` | B-tree |
| events | idx | `status` | B-tree |
| events | idx | `event_type` | B-tree |
| events | idx | `priority` | B-tree |
| events | idx | `created_at` | B-tree |

---

## Data Flow

### 1. WhatsApp Group Sync

```
User selects group → Frontend calls POST /groups/{id}/messages/process
  → Backend fetches messages from Green API (getChatHistory)
  → Each message saved as WhatsappMessage
  → Deduplication by whatsapp_message_id
  → OpenAI parses each message (5 concurrent, semaphore-limited)
  → Event record created per message
  → Response: { events_created, events_skipped, events[] }
```

### 2. Manual Chat Input

```
User types message → Frontend calls POST /chat/message
  → Backend creates WhatsappMessage (source: manual_chat, id: manual_<uuid>)
  → OpenAI parses message
  → Event created
  → Response: { event, formatted_message }
```

### 3. File Upload

```
User uploads .txt → Frontend calls POST /upload/file (multipart)
  → FileParserFactory selects WhatsAppTextFileParser
  → Parser extracts messages (handles 3 format variants)
  → Each message processed through OpenAI (5 concurrent)
  → Events created (no deduplication for file uploads)
  → Response: { total_messages_found, events_created, events_failed, parse_errors }
```

---

## Project Structure

```
whatsapp-sync/
├── README.md                 # This file — full architecture overview
├── Makefile                  # Root orchestration (delegates to backend/frontend)
├── backend/                  # Python FastAPI server
│   ├── README.md             # Backend-specific documentation
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── config.py         # Environment-based settings
│   │   ├── database.py       # Async SQLAlchemy setup
│   │   ├── models/           # ORM models (Group, Message, Event)
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── routers/          # API endpoints
│   │   ├── services/         # Business logic + external API clients
│   │   └── utils/            # Logging
│   ├── alembic/              # Database migrations
│   ├── requirements.txt
│   └── Makefile
└── frontend/                 # React TypeScript client
    ├── README.md             # Frontend-specific documentation
    ├── src/
    │   ├── api/              # Axios API layer
    │   ├── store/            # Zustand state management
    │   ├── hooks/            # React Query hooks
    │   ├── types/            # TypeScript interfaces
    │   ├── components/       # UI components
    │   └── pages/            # Page components
    ├── package.json
    └── Makefile
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Green API account (instance ID + token)
- OpenAI API key

### Full Setup

```bash
# 1. Clone and set up both projects
make setup

# 2. Configure backend environment
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials:
#   DATABASE_URL, GREEN_API_INSTANCE_ID, GREEN_API_TOKEN, OPENAI_API_KEY

# 3. Run database migrations
make migrate

# 4. Start backend (terminal 1)
make dev-backend    # → http://localhost:8000

# 5. Start frontend (terminal 2)
make dev-frontend   # → http://localhost:5173
```

### Make Targets

| Command | Description |
|---------|-------------|
| `make setup` | Set up both backend and frontend |
| `make dev-backend` | Start backend dev server (port 8000) |
| `make dev-frontend` | Start frontend dev server (port 5173) |
| `make migrate` | Apply database migrations |
| `make build` | Build frontend for production |
| `make clean` | Remove build artifacts |

---

## API Reference

**Base URL:** `http://localhost:8000/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/groups` | List WhatsApp groups |
| GET | `/groups/{id}` | Get group details |
| POST | `/groups/{id}/messages/process` | Sync & process group messages |
| GET | `/events` | List events (filterable) |
| GET | `/events/{id}` | Get single event |
| PATCH | `/events/{id}/status` | Update event status |
| POST | `/chat/message` | Parse manual message |
| POST | `/upload/file` | Upload chat export |
| GET | `/upload/supported-types` | List supported file types |

---

## Key Design Decisions

- **Async everywhere:** asyncpg + async SQLAlchemy + async httpx for non-blocking I/O
- **Semaphore-limited concurrency:** Max 5 concurrent OpenAI calls to avoid rate limits
- **Per-task DB sessions:** Each async processing task gets its own session to avoid asyncpg conflicts
- **Factory pattern for file parsers:** Extensible without modifying existing code
- **Two-tier frontend state:** React Query for server cache, Zustand for UI state
- **Virtual scrolling:** Large event lists rendered efficiently
- **No authentication:** Designed for internal/local use — auth should be added for production
