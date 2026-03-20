# PropSync Backend — API Server

Python FastAPI backend that ingests WhatsApp messages (via Green API or file uploads), processes them through OpenAI for intelligent event extraction, and stores structured property management events in PostgreSQL.

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.11+ |
| Framework | FastAPI | 0.111.0+ |
| ASGI Server | Uvicorn | 0.29.0+ |
| Database | PostgreSQL | — |
| ORM | SQLAlchemy (async) | 2.0.0+ |
| DB Driver | asyncpg | 0.29.0+ |
| Migrations | Alembic | 1.13.0+ |
| Validation | Pydantic | 2.7.0+ |
| HTTP Client | httpx | 0.27.0+ |
| AI | OpenAI SDK | 1.30.0+ |

---

## Third-Party Services & APIs

### 1. Green API (WhatsApp Integration)

- **Purpose:** Connects to WhatsApp Business via [Green API](https://green-api.com/)
- **Base URL:** `https://api.green-api.com`
- **Endpoints used:**
  - `getChats` — Fetch all WhatsApp groups
  - `getChatHistory` — Fetch message history from a group
  - `sendMessage` — Send a message to a group
- **Auth:** Instance ID + API Token (configured in `.env`)
- **Connection:** Async HTTP with connection pooling (20 max, 10 keepalive), 30s timeout

### 2. OpenAI API (Message Intelligence)

- **Purpose:** Parses raw WhatsApp messages into structured property management events
- **Model:** `gpt-4o-mini` (configurable via `OPENAI_MODEL`)
- **Features:**
  - JSON response format for structured output
  - Temperature: 0.1 (deterministic extraction)
  - US Real Estate terminology in system prompt
  - Extracts: event type, priority, title, description, tenant info, property info, confidence score
  - Graceful fallback with low-confidence (0.1) generic event on failure

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FastAPI App                        │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌───────┐  ┌──────────┐   │
│  │  Groups   │  │ Messages │  │ Events│  │  Upload  │   │
│  │  Router   │  │  Router  │  │ Router│  │  Router  │   │
│  └────┬─────┘  └────┬─────┘  └───┬───┘  └────┬─────┘   │
│       │              │            │            │         │
│  ┌────▼──────────────▼────────────▼────────────▼─────┐  │
│  │                  Services Layer                    │  │
│  │                                                    │  │
│  │  ┌────────────┐ ┌────────────┐ ┌───────────────┐  │  │
│  │  │ GreenAPI   │ │  OpenAI    │ │    Event      │  │  │
│  │  │ Service    │ │  Service   │ │   Service     │  │  │
│  │  └────────────┘ └────────────┘ └───────────────┘  │  │
│  │  ┌────────────────┐ ┌──────────────────────────┐  │  │
│  │  │ FileUpload     │ │  MessageProcessor        │  │  │
│  │  │ Service        │ │  (batch + concurrency)    │  │  │
│  │  └────────────────┘ └──────────────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │ File Parsers (Factory Pattern)               │ │  │
│  │  │  ├── WhatsAppTextFileParser (.txt exports)   │ │  │
│  │  │  └── ... (extensible via registry)           │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐  │
│  │           SQLAlchemy Async ORM + asyncpg          │  │
│  └───────────────────────┬───────────────────────────┘  │
└──────────────────────────┼──────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ PostgreSQL  │
                    └─────────────┘
```

### Directory Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app, lifespan, CORS, router registration
│   ├── config.py                  # Pydantic Settings (env-based configuration)
│   ├── database.py                # Async SQLAlchemy engine & session factory
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── group.py               # WhatsappGroup
│   │   ├── message.py             # WhatsappMessage
│   │   └── event.py               # Event
│   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── group.py
│   │   ├── message.py
│   │   └── event.py
│   ├── routers/                   # API endpoint definitions
│   │   ├── groups.py              # /api/v1/groups
│   │   ├── messages.py            # /api/v1/groups/{id}/messages
│   │   ├── events.py              # /api/v1/events
│   │   ├── chat.py                # /api/v1/chat
│   │   └── upload.py              # /api/v1/upload
│   ├── services/                  # Business logic layer
│   │   ├── greenapi.py            # Green API WhatsApp client
│   │   ├── openai_service.py      # OpenAI message parsing
│   │   ├── event_service.py       # Event CRUD + processing pipeline
│   │   ├── message_processor.py   # Batch message processing
│   │   ├── file_upload_service.py # File upload orchestration
│   │   └── file_parsers/          # Extensible file parser system
│   │       ├── base.py            # Abstract parser interface (IFileParser)
│   │       ├── factory.py         # Parser registry/factory
│   │       └── text_parser.py     # WhatsApp .txt export parser
│   └── utils/
│       └── logger.py              # Logging configuration
├── alembic/                       # Database migrations
│   ├── env.py                     # Migration runner (async)
│   └── versions/
│       ├── 001_initial_schema.py  # Base tables + enums
│       └── 002_file_upload_support.py  # File upload nullable fields
├── requirements.txt
├── alembic.ini
├── Makefile
├── .env.example
└── .env
```

---

## API Endpoints

**Base path:** `/api/v1`

### Groups

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/groups` | List all WhatsApp groups (60s cache) |
| `GET` | `/groups/{group_id}` | Get single group details |
| `POST` | `/groups/{group_id}/messages/process` | Fetch & process messages from WhatsApp group |

### Events

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/events` | List events (filterable by group, type, priority, status) |
| `GET` | `/events/{event_id}` | Get single event |
| `PATCH` | `/events/{event_id}/status` | Update event status |

### Chat

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/chat/message` | Parse a manually entered message into an event |

### Upload

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/upload/file` | Upload WhatsApp chat export file (multipart) |
| `GET` | `/upload/supported-types` | List supported file MIME types |

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |

---

## Data Processing Pipeline

```
1. Message Ingestion (Green API / Manual / File Upload)
         │
2. Save raw WhatsappMessage to DB
         │
3. Deduplication check (by whatsapp_message_id)
         │
4. OpenAI parsing → structured event data
         │
5. Create Event record (linked to message)
         │
6. Mark WhatsappMessage as processed
```

**Concurrency:** Semaphore-limited to 5 concurrent OpenAI calls. Each async task uses its own DB session to avoid asyncpg conflicts.

**Deduplication:**
- Green API messages: deduplicated by `whatsapp_message_id`
- Manual chat: uses synthetic `manual_<uuid>` IDs
- File uploads: no deduplication (all messages processed)

---

## File Parser System

Extensible factory pattern for processing different file formats.

**Currently supported:**
- WhatsApp text exports (`.txt`) — 3 format variants:
  - Android 24-hour: `16/01/26, 19:46 - Sender: message`
  - Android 12-hour: `12/31/23, 10:30 AM - Sender: message`
  - iOS: `[31/12/23, 10:30:45 AM] Sender: message`

**Max file size:** 10 MB

To add a new parser: implement `IFileParser` and register it in `FileParserFactory`.

---

## Configuration

All configuration is via environment variables (loaded from `.env`).

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL async connection string |
| `GREEN_API_INSTANCE_ID` | Yes | — | Green API instance ID |
| `GREEN_API_TOKEN` | Yes | — | Green API authentication token |
| `OPENAI_API_KEY` | Yes | — | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | OpenAI model to use |
| `GREEN_API_BASE_URL` | No | `https://api.green-api.com` | Green API base URL |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `CORS_ORIGINS` | No | `["http://localhost:5173"]` | Allowed CORS origins (JSON array) |

---

## Setup & Development

### Prerequisites
- Python 3.11+
- PostgreSQL running locally
- Green API account with instance ID & token
- OpenAI API key

### Quick Start

```bash
# Create virtual environment & install dependencies
make setup

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run database migrations
make migrate

# Start development server (hot-reload on port 8000)
make dev
```

### Available Make Targets

| Command | Description |
|---------|-------------|
| `make setup` | Full first-time setup |
| `make install` | Install Python dependencies |
| `make migrate` | Apply pending Alembic migrations |
| `make makemigrations MSG="desc"` | Generate new migration |
| `make db-reset` | Drop all tables and re-migrate |
| `make dev` | Start dev server with hot-reload |
| `make run` | Start production server |
| `make clean` | Remove build artifacts |

---

## Database Connection

- **Engine:** Async SQLAlchemy with asyncpg driver
- **Pool:** 10 base connections, 20 max overflow, pre-ping enabled
- **Sessions:** AsyncSession with expire_on_commit=False

---

## Authentication

> **Note:** No authentication is currently implemented. All endpoints are publicly accessible. CORS restricts requests to configured origins only. Authentication should be added before production deployment.
