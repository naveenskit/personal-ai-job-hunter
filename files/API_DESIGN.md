# API Design
# Personal AI Job Hunter

**Version:** 1.0.0 | **Framework:** Flask (REST)

---

## Base URL

```
http://localhost:8000/api/v1
```

---

## Authentication

Single-user personal system. Protected by `API_SECRET_KEY` in `.env`.

```
Header: X-API-Key: <API_SECRET_KEY>
```

---

## Endpoints

### Health
```
GET  /health                    → system status
GET  /health/agents             → agent status
```

### Resumes
```
GET    /resumes                 → list all resumes
POST   /resumes                 → upload new resume (multipart/form-data)
GET    /resumes/{id}            → resume detail + parsed data
PUT    /resumes/{id}            → update tags / set active
DELETE /resumes/{id}            → remove resume
GET    /resumes/{id}/gaps       → skill gaps for this resume
POST   /resumes/{id}/analyze    → re-run AI analysis
```

### Opportunities
```
GET    /opportunities           → list (filters: role_type, country, score_band, status)
GET    /opportunities/{id}      → opportunity detail + score
POST   /opportunities/search    → trigger manual discovery run
PUT    /opportunities/{id}      → update manually
DELETE /opportunities/{id}      → soft-delete
POST   /opportunities/{id}/score → re-score with specific resume
GET    /opportunities/today     → today's top-scored, not yet applied
```

### Companies
```
GET    /companies               → list (filters: type, india_presence)
GET    /companies/{id}          → company + research data
POST   /companies               → add company manually
POST   /companies/import        → bulk import CSV/JSON
PUT    /companies/{id}          → update
POST   /companies/{id}/research → trigger AI research
GET    /companies/{id}/opportunities → all jobs at this company
```

### Applications
```
GET    /applications            → pipeline view (group by status)
GET    /applications/{id}       → full detail + events
POST   /applications            → create (link opportunity + resume)
PUT    /applications/{id}/status → state transition
POST   /applications/{id}/note  → add note
GET    /applications/stats      → funnel metrics
GET    /applications/export     → trigger Excel export
```

### Outreach
```
POST   /outreach/email          → generate cold email
        body: { opportunity_id, resume_id, recipient? }
POST   /outreach/linkedin       → generate LinkedIn note/InMail
        body: { opportunity_id, resume_id, message_type }
GET    /outreach/{app_id}       → all messages for application
POST   /outreach/{id}/sent      → mark as sent
```

### Reports
```
GET    /reports                 → list reports
GET    /reports/latest          → latest weekly report
POST   /reports/generate        → trigger report generation
GET    /reports/{id}/export     → download as PDF/Markdown
```

### Agents
```
POST   /agents/discovery/run    → manual trigger
POST   /agents/research/run     → manual trigger
POST   /agents/scoring/run      → manual trigger
GET    /agents/status           → all agent last-run times
```

### Config
```
GET    /config/locations        → current location config
PUT    /config/locations        → update location preferences
GET    /config/roles            → target roles
PUT    /config/roles            → update roles
GET    /config/sources          → job sources config
```

### Telegram
```
POST   /telegram/digest/send    → send digest now
GET    /telegram/subscribers    → list
POST   /telegram/test           → send test message
```

---

## Response Format

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 147
  },
  "error": null
}
```

## Error Format

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "OPPORTUNITY_NOT_FOUND",
    "message": "No opportunity with id 42",
    "details": {}
  }
}
```

---

## Telegram Bot Commands

```
/start          → Register + welcome
/digest         → Send today's top opportunities
/stats          → Application pipeline stats
/search [role]  → Search opportunities
/apply [id]     → Mark opportunity as applied
/report         → Latest weekly report summary
/gaps           → Current skill gaps
/help           → Command list
```

---

## Internal Service Contracts

### AIProvider Interface
```python
class AIProvider(Protocol):
    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str: ...

    async def embed(self, text: str) -> list[float]: ...
    
    @property
    def model_name(self) -> str: ...
```

### JobSource Interface
```python
class JobSource(Protocol):
    @property
    def source_name(self) -> str: ...
    
    async def fetch(
        self,
        query: JobQuery,
        limit: int = 50,
    ) -> list[RawOpportunity]: ...
    
    async def health_check(self) -> bool: ...
```

### Agent Interface
```python
class BaseAgent(ABC):
    async def run(self) -> AgentResult: ...
    async def health_check(self) -> bool: ...
    
    @property
    def name(self) -> str: ...
    
    @property
    def last_run(self) -> datetime | None: ...
```
