# Personal AI Job Hunter

Single-user AI job discovery, company research, opportunity scoring, outreach, tracking, and reporting assistant.

Phase 1 builds the core foundation: configuration, database layer, repositories, AI provider abstraction, and runtime entry point.

Local dev notes:
- The app expects Python 3.11 for best compatibility (some optional C-extension wheels like `PyMuPDF` are built for 3.11).
- To run locally:
	- Install dependencies: `py -3.11 -m pip install -r requirements.txt`
	- (Optional) Install dev/test deps: `py -3.11 -m pip install -r requirements-dev.txt`
	- Copy `.env.example` to `.env` and update secrets
	- Start dev server: `py -3.11 main.py` (serves at http://127.0.0.1:8000)

If you need PDF parsing support (`fitz`/PyMuPDF) on Windows, use Python 3.11 and install the prebuilt wheel or install Visual Studio build tools.
