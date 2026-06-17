# Product Requirements Document
# Personal AI Job Hunter, Company Researcher & Application Assistant

**Version:** 1.0.0  
**Target User:** CS Engineering Student, Graduation 2027  
**Primary Market:** India (Bengaluru, Hyderabad, Pune, Chennai, Jaipur, Gurgaon, Noida, Mumbai)  
**Status:** Phase 0 — Planning

---

## 1. Problem Statement

A CS student graduating in 2027 must manage a chaotic, multi-channel job search across LinkedIn, company portals, referral networks, and campus placements — simultaneously. Manual tracking fails at scale. Personalization is lost. Opportunities are missed. Response rates are low because outreach is generic.

This system replaces that chaos with a personal AI operating system.

---

## 2. Goals

| Goal | Metric |
|------|--------|
| Surface relevant opportunities daily | ≥ 10 scored opportunities/day |
| Eliminate duplicate tracking | 0% duplicate entries |
| Personalize every outreach | Resume-match score per message |
| Track application pipeline | Full funnel: discovered → applied → responded → offer |
| Identify skill gaps proactively | Gap report updated weekly |
| Deliver career intelligence | Weekly Telegram digest + Excel export |

---

## 3. Non-Goals

- This is NOT a portfolio project or demo
- This is NOT a multi-user SaaS
- This is NOT a browser extension / automated form filler
- This does NOT scrape LinkedIn in violation of ToS

---

## 4. User Personas

**Primary: Arjun (the user)**
- 3rd year CS student, graduating 2027
- Strong in Python, learning DevOps/Cloud
- Wants SDE Intern → Associate SWE pipeline
- Located in Jaipur, open to Bengaluru/remote
- Checks Telegram daily, dislikes context-switching

---

## 5. Feature Requirements

### P0 — Core (Must Have)
| ID | Feature | Description |
|----|---------|-------------|
| F01 | Multi-Resume Support | Store multiple resume versions; tag by role type |
| F02 | Resume Intelligence | Parse, extract skills, experience, projects, education |
| F03 | Automated Job Discovery | Search jobs via APIs + configured sources |
| F04 | Company Research Agent | AI-powered company profile builder |
| F05 | Opportunity Scoring | 6-factor weighted score (see scoring model) |
| F06 | Application Tracker | Full pipeline state machine |
| F07 | Telegram Bot | Daily digest, alerts, commands |
| F08 | Duplicate Detection | Hash-based + semantic dedup |
| F09 | Configuration System | .env + YAML, no hardcoded values |
| F10 | Structured Logging | Per-module logs with rotation |

### P1 — High Value
| ID | Feature | Description |
|----|---------|-------------|
| F11 | Email Generator | Personalized cold email per opportunity |
| F12 | LinkedIn Message Generator | 300-char InMail + connection note |
| F13 | Skill Gap Analysis | Resume vs. JD gap extraction |
| F14 | Company List Import | CSV/JSON bulk company import |
| F15 | Excel Export | Application tracker export |
| F16 | Weekly Career Report | Markdown + Telegram summary |

### P2 — Nice to Have
| ID | Feature | Description |
|----|---------|-------------|
| F17 | Application Learning System | Outcome → future ranking signal |
| F18 | Dashboard UI | Minimalist web UI (Linear-inspired) |
| F19 | Opportunity Prioritization | AI-ranked daily shortlist |

---

## 6. Opportunity Scoring Model

```
Score = (resume_match × 0.35) 
      + (hiring_probability × 0.20) 
      + (location_preference × 0.15) 
      + (freshness × 0.15) 
      + (company_quality × 0.10) 
      + (competition_estimate × 0.05)
```

**Score Bands:**
- 95–100: Dream Match 🏆
- 90–94: Excellent Match ⭐
- 80–89: Strong Match ✅
- 70–79: Good Match 👍
- < 70: Low Priority 📋

---

## 7. Location Priority

```yaml
India: 100
Remote: 95
Singapore: 80
UAE: 75
Europe: 70
United States: 65
```

**Indian Cities (default):** Bengaluru, Hyderabad, Pune, Chennai, Jaipur, Gurgaon, Noida, Mumbai, Ahmedabad, Kolkata

---

## 8. Target Roles

- Software Engineer Intern / SDE Intern
- Backend Engineer Intern
- Cloud Engineer Intern
- DevOps Engineer Intern
- Platform Engineer Intern
- Associate Software Engineer
- Graduate Software Engineer

---

## 9. Application States

```
DISCOVERED → RESEARCHED → MATCHED → OUTREACH_SENT 
→ APPLIED → ACKNOWLEDGED → INTERVIEWING 
→ OFFERED / REJECTED / GHOSTED / WITHDRAWN
```

---

## 10. Constraints

- Gemini API (primary AI); OpenAI/Claude as future providers
- SQLite now; PostgreSQL migration path required
- All credentials in `.env` only
- Must run on a single machine (student's laptop or VPS)
- Telegram is the primary notification channel
- No browser automation / ToS violations
