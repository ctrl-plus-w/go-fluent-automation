# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python automation tool for the GoFluent language learning platform. Uses Selenium (Firefox) for web scraping and OpenAI GPT-4o to solve quiz questions. Package manager is `uv`, Python 3.11+.

## Commands

```bash
# Run (auto mode - solve N activities for the month)
python3 -m src.main --auto-run 10 --grammar --language Anglais

# Run (simple mode - solve a single activity by URL)
python3 -m src.main --simple-run <URL> --language Espagnol

# Useful flags
--language <NAME>    # (Required) Learning language (e.g., Anglais, Espagnol, Allemand, Russe)
--debug              # Verbose console logging
--no-headless        # Show browser window
--cache / --no-cache # Toggle activity URL caching
--profile <NAME>     # Use named credentials from .env
--minimum-level B1   # Filter by CEFR level (A1-C2)
--maximum-level C2

# Install dependencies
uv sync
```

No test suite or linter is configured.

## Architecture

**Entry point:** `src/main.py` — CLI argument parsing, logger/credentials setup, runner dispatch.

**Runners** (`src/runners/`):
- `AutoRun` — logs in, counts completed activities for the month, loops through available activities until target count is met
- `SimpleRun` — validates a single URL and solves that activity

**Core classes** (`src/classes/`):
- `Scraper` — manages Selenium Firefox WebDriver, handles Microsoft/SAML login, page navigation. Uses `@logged_in` decorator to ensure authentication before operations
- `Activity` — data model for a learning activity (URL, questions, answers, markdown output)
- `ActivityLearning` — extracts lesson content from activity tabs to provide context to the AI
- `ActivitySolving` — orchestrates quiz interaction: caches known answers, calls OpenAI for unknown ones, handles retries

**Question type hierarchy** (`src/classes/questions/`):
- `Question` — base class with interface methods (`as_text`, `answer`, `get_correct_answer`, `submit_and_check_correct_answer`)
- `Question.from_element()` — factory method that inspects DOM CSS classes to instantiate the correct subclass
- 8 subclasses: `MultiChoiceTextQuestion`, `MultiChoiceImageQuestion`, `ScrambledLettersQuestion`, `ScrambledSentencesQuestion`, `ShortTextQuestion`, `FillGapsTextQuestion`, `FillGapsBlockQuestion`, `MatchTextQuestion`
- Each subclass handles parsing the question from HTML, submitting answers to the DOM, and retrieving correct answers after submission

**Constants** (`src/constants/`):
- `selectors.py` — centralized CSS/XPath selectors organized by page section (LOGIN, MICROSOFT, DASHBOARD, TRAINING, QUIZ, etc.)
- `credentials.py` — loads `.env` via python-dotenv

**Utilities** (`src/utils/`):
- `ai.py` — OpenAI integration, sends learning context + question, expects JSON array response
- `cache.py` — file-based set of completed activity URLs (`cache.txt`)
- `parser.py` — BeautifulSoup HTML parsing, French locale date parsing
- `strings.py` — XPath-safe quote escaping
- `lists.py` — functional helpers `_f()` (filter) and `_m()` (map)

## Key Patterns

- All module imports use absolute paths from `src.` (e.g., `from src.classes.scraper import Scraper`)
- Circular import avoidance: `Question.from_element()` uses local imports for subclasses; some files use `TYPE_CHECKING` guards
- Logging goes to both console (conditional on `--debug`) and a timestamped file under `logs/`
- Environment variables for credentials and API keys via `.env` (see `.env.example`)
