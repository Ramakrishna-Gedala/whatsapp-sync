# PropSync Frontend — React Client

React + TypeScript single-page application for managing property management events extracted from WhatsApp messages. Features a dashboard for viewing/filtering events, a chat interface for manual message parsing, and file upload for bulk WhatsApp export processing.

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | TypeScript | 5.4.5 |
| Framework | React | 18.3.1 |
| Build Tool | Vite | 5.3.3 |
| Routing | React Router DOM | 6.24.0 |
| State Management | Zustand | 4.5.2 |
| Data Fetching | TanStack React Query | 5.45.1 |
| HTTP Client | Axios | 1.7.2 |
| CSS Framework | Tailwind CSS | 3.4.4 |
| UI Primitives | Radix UI | various |
| Icons | Lucide React | 0.400.0 |
| Toasts | Sonner | 1.5.0 |
| Dates | date-fns | 3.6.0 |
| Virtualization | @tanstack/react-virtual | 3.8.1 |

---

## Third-Party Libraries

### UI Components (Radix UI)

Accessible, unstyled primitives used for complex interactive components:

| Package | Usage |
|---------|-------|
| `@radix-ui/react-select` | Group selector, filter dropdowns |
| `@radix-ui/react-dialog` | Modal dialogs |
| `@radix-ui/react-dropdown-menu` | Context menus |
| `@radix-ui/react-progress` | Upload progress, confidence bars |
| `@radix-ui/react-tooltip` | Hover tooltips |
| `@radix-ui/react-label` | Form labels |
| `@radix-ui/react-separator` | Visual dividers |
| `@radix-ui/react-slot` | Component composition |

### Styling Utilities

| Package | Purpose |
|---------|---------|
| `tailwind-merge` | Merge conflicting Tailwind classes |
| `clsx` | Conditional className construction |
| `class-variance-authority` | Component variant definitions |

---

## Architecture

### Directory Structure

```
frontend/src/
├── main.tsx                         # Entry point, React Query provider setup
├── App.tsx                          # Router definition & layout wrapper
├── index.css                        # Global styles, Tailwind directives, custom classes
├── api/                             # API communication layer
│   ├── axiosClient.ts               # Axios instance with interceptors
│   ├── chatApi.ts                   # POST /chat/message
│   ├── eventsApi.ts                 # GET/PATCH /events
│   ├── groupsApi.ts                 # GET /groups
│   ├── messagesApi.ts               # POST /groups/{id}/messages/process
│   └── uploadApi.ts                 # POST /upload/file
├── store/                           # Zustand global state
│   ├── useEventStore.ts             # Event list, filters, optimistic updates
│   └── useGroupStore.ts             # Selected group state
├── hooks/                           # Custom React hooks (React Query wrappers)
│   ├── useChat.ts                   # Chat message mutation
│   ├── useEvents.ts                 # Events query with filters
│   ├── useFileUpload.ts             # File upload mutation
│   ├── useGroupMessages.ts          # Message sync mutation
│   └── useGroups.ts                 # Groups query
├── types/                           # TypeScript interfaces
│   ├── event.ts                     # Event, EventType, Priority, EventStatus
│   ├── group.ts                     # WhatsAppGroup
│   ├── message.ts                   # ProcessMessagesResponse
│   └── upload.ts                    # FileUploadResponse
├── lib/
│   └── utils.ts                     # cn() — Tailwind className utility
├── components/
│   ├── layout/
│   │   ├── AppLayout.tsx            # Sidebar + main content + toast container
│   │   └── Sidebar.tsx              # Navigation links, dark mode toggle
│   ├── events/
│   │   ├── EventCard.tsx            # Event display with expand/collapse, status update
│   │   ├── EventFilters.tsx         # Type/priority/status filter dropdowns
│   │   └── EventList.tsx            # Virtualized event list (50+ items)
│   ├── groups/
│   │   └── GroupSelector.tsx        # WhatsApp group dropdown
│   └── chat/
│       ├── ChatInput.tsx            # Textarea with char count (2000 max), Ctrl+Enter submit
│       ├── ChatEventPreview.tsx     # Parsed event result with confidence bar
│       └── FileUploadSection.tsx    # Drag-drop upload with progress & results
└── pages/
    ├── EventsPage.tsx               # Events dashboard (groups + filters + list)
    └── ChatPage.tsx                 # Manual message parsing + file upload
```

### Component Hierarchy

```
App (BrowserRouter)
└── AppLayout
    ├── Sidebar (navigation + theme toggle)
    └── <Outlet>
        ├── EventsPage
        │   ├── GroupSelector
        │   ├── "Sync Messages" button
        │   ├── EventFilters
        │   └── EventList
        │       └── EventCard × N
        └── ChatPage
            ├── ChatInput
            ├── ChatEventPreview
            └── FileUploadSection
```

---

## State Management

### Two-Tier Approach

```
Backend API → React Query (server state cache) → Zustand (UI state) → Components
```

**React Query** handles server state:
- Automatic caching (30s stale time for events, 60s for groups)
- Single retry on failure
- Query key invalidation on mutations

**Zustand** handles UI state:
- `useEventStore` — event list, total count, filter state, optimistic status updates
- `useGroupStore` — currently selected group ID and name

### Data Flow Example (Sync Messages)

1. User selects a group → `useGroupStore.setSelectedGroup()`
2. User clicks "Sync" → `useGroupMessages` mutation fires
3. Backend processes messages → returns new events
4. Events prepended to `useEventStore.events` (optimistic)
5. `useEvents` query invalidated → re-fetches from server
6. Toast notification shown via Sonner

---

## Routing

| Path | Page | Description |
|------|------|-------------|
| `/` | — | Redirects to `/events` |
| `/events` | EventsPage | Main dashboard with event list and filters |
| `/chat` | ChatPage | Manual message parsing and file upload |

---

## API Integration

### Base URL

```
VITE_API_BASE_URL (default: http://localhost:8000/api/v1)
```

### Axios Client Features

- **Request interceptor:** Logs API calls in development mode
- **Response interceptor:** Maps HTTP errors to user-friendly toast messages:
  - `422` → "Invalid input"
  - `409` → "Already processed"
  - `502` → "WhatsApp/AI service unavailable"
  - `500` → "Server error"
  - `404` → "Resource not found"
  - Network error → "Cannot reach server"

### API Endpoints Consumed

| API Module | Method | Endpoint | Purpose |
|------------|--------|----------|---------|
| `groupsApi` | GET | `/groups` | List WhatsApp groups |
| `groupsApi` | GET | `/groups/{id}` | Get group details |
| `messagesApi` | POST | `/groups/{id}/messages/process` | Sync & process messages |
| `eventsApi` | GET | `/events` | List events with filters |
| `eventsApi` | GET | `/events/{id}` | Get single event |
| `eventsApi` | PATCH | `/events/{id}/status` | Update event status |
| `chatApi` | POST | `/chat/message` | Parse manual message |
| `uploadApi` | POST | `/upload/file` | Upload chat export file |
| `uploadApi` | GET | `/upload/supported-types` | Get supported MIME types |

---

## Styling

### Tailwind CSS Configuration

- **Dark mode:** Class-based toggle (`darkMode: 'class'`)
- **Theme:** Custom One Dark + Light theme color palette

**Custom Colors:**

| Token | Dark | Light |
|-------|------|-------|
| Background | `#282c34` | `#f8fafc` |
| Secondary BG | `#21252b` | `#f1f5f9` |
| Foreground | `#abb2bf` | `#1e293b` |
| Accent | `#61afef` (blue) | `#f59e0b` (amber) |
| Border | `#3e4451` | `#e2e8f0` |

**Fonts:**
- Sans: Geist, Inter, system-ui
- Mono: JetBrains Mono, Fira Code

**Custom component classes** defined in `index.css`: `.badge`, `.card`, `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-ghost`

**Custom animations:** `slide-in` (0.3s) and `fade-in` (0.2s)

---

## Key Features

- **Virtual scrolling** for large event lists (50+ items) via `@tanstack/react-virtual`
- **Drag-and-drop file upload** with progress tracking
- **Debounced filtering** (300ms) to reduce API calls
- **Optimistic UI updates** when changing event status
- **Dark/light theme toggle** persisted via CSS class
- **Responsive layout** with collapsible sidebar

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | Backend API base URL |

---

## Setup & Development

### Prerequisites
- Node.js 18+
- Backend server running on port 8000

### Quick Start

```bash
# Install dependencies
npm install

# Configure environment (optional — defaults to localhost:8000)
cp .env.example .env

# Start development server (port 5173)
npm run dev
```

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server with hot-reload |
| `npm run build` | Type-check + production build |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint (zero warnings enforced) |

---

## Authentication

> **Note:** No frontend authentication is implemented. The app assumes an accessible backend. Auth should be added before production deployment.
