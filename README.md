# AI-Powered Competitor Marketing Brief Agent

A portfolio-ready Streamlit application that converts structured competitor
observations into an evidence-grounded marketing brief.

The project demonstrates the intersection of AI marketing, competitor
intelligence, marketing analytics, prompt design, and product thinking. It uses
the OpenAI Responses API for AI-powered analysis and includes a transparent
rule-based fallback so the public demo remains usable without an API key.

The recommended public portfolio deployment runs in **Rule-based portfolio
demo** mode without any API key. This keeps the app free to operate, prevents
API-credit abuse, and ensures that uploaded data is not sent to a third-party
model. The optional OpenAI integration remains in the codebase as an
architecture and testing example.

## What the app does

1. Loads the bundled sample dataset or a user-uploaded CSV.
2. Validates the schema, required values, and dates.
3. Filters observations by competitor and marketing category.
4. Visualizes competitor activity and category coverage.
5. Generates a structured brief with either:
   - OpenAI-powered evidence synthesis; or
   - a deterministic rule-based fallback.
6. Exports the report as Markdown and JSON, plus the exact filtered evidence as
   CSV.

## Why this is an AI Marketing project

Marketing teams often collect competitor observations across campaigns,
product launches, content formats, and brand messages. The difficult part is
turning those notes into a concise, decision-useful narrative.

This application productizes that workflow:

- structured evidence intake;
- data-quality checks;
- exploratory marketing analytics;
- grounded AI synthesis;
- explicit limitations and provenance;
- reusable report exports.

The AI prompt instructs the model to use only supplied evidence, separate
observations from recommendations, avoid invented metrics, and return a fixed
seven-section report contract.

## Report structure

- Executive Summary
- Competitor Activity Overview
- Content Strategy Analysis
- Audience and Positioning
- Key Marketing Insights
- Recommendations
- Limitations
- Report Metadata

## Tech stack

- Python
- Streamlit
- pandas
- OpenAI Python SDK
- OpenAI Responses API
- `unittest`

The default text-generation model is `gpt-5.6`. It can be changed with the
`OPENAI_MODEL` environment variable or Streamlit secret.

## Project structure

```text
.
|-- app.py
|-- brief_generator.py
|-- requirements.txt
|-- data/
|   `-- sample_competitor_data.csv
|-- tests/
|   `-- test_brief_generator.py
|-- .streamlit/
|   |-- config.toml
|   `-- secrets.example.toml
|-- .gitignore
`-- README.md
```

## CSV schema

The app accepts UTF-8 CSV files up to 10 MB with these columns:

| Column | Meaning | Example |
|---|---|---|
| `competitor` | Competitor or brand name | `Toutiao` |
| `date` | Observation date in `YYYY-MM-DD` format | `2026-01-13` |
| `source` | Evidence source or disclosure label | `Sample Portfolio Data` |
| `title` | Short observation title | `Short video news packaging` |
| `content` | Factual observation or research note | `Toutiao uses short video...` |
| `category` | Marketing analysis category | `Content Strategy` |

The included dataset is synthetic portfolio data. It must not be represented as
official market data.

## Run locally

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

For AI-powered mode, copy the example secrets file:

```powershell
Copy-Item .streamlit\secrets.example.toml .streamlit\secrets.toml
```

Then replace the placeholder inside `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-5.6"
```

Never commit `secrets.toml`. It is excluded by `.gitignore`.

Run the app:

```powershell
streamlit run app.py
```

Open `http://localhost:8501`.

## Run tests

The test suite validates:

- CSV schema and date handling;
- deterministic evidence ordering;
- prompt grounding instructions;
- Responses API request construction;
- JSON report-contract parsing;
- rejection of incomplete model output.

```powershell
python -m unittest discover -s tests -v
```

The API integration test uses a fake client and does not spend API credits.

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository and push this project.
2. In Streamlit Community Cloud, create an app from `app.py`.
3. For the recommended public demo, leave the **Secrets** field empty.
4. Deploy and test the upload, filtering, report, and export workflow.
5. Add the live URL and a screenshot to this README.

Do not add an API key to a public deployment unless the app also has access
control, usage limits, and an appropriate API budget. If you intentionally
deploy a protected AI-enabled version, add these values under **Secrets**:

```toml
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-5.6"
```

The API key remains server-side. Do not add it to the repository or expose it
through a browser input.

## Portfolio demo script

Use this 60-second flow in interviews:

1. Explain the business problem: competitor notes are fragmented and slow to
   synthesize.
2. Upload or select the sample evidence.
3. Filter two or more competitors and relevant categories.
4. Show the activity and category charts.
5. Generate the AI brief.
6. Point out grounded recommendations, limitations, and report metadata.
7. Download the report and exact evidence used.

## Current limitations

- The bundled dataset is synthetic portfolio data.
- Uploaded rows are structured observations; the app does not scrape websites.
- Model output quality depends on source quality and evidence coverage.
- The app does not persist datasets or reports in a database.
- A human should review recommendations before business use.
- Live API behavior requires a valid OpenAI API key and available model access.

## Responsible-use choices

- Evidence is sent only when the user selects AI-powered generation.
- Input is capped before it is included in the model prompt.
- The prompt prohibits invented facts and metrics.
- The exact filtered evidence can be exported for review.
- The report always includes limitations and generation metadata.
- Rule-based mode provides a no-cost, auditable fallback.

## Next improvements

- Add approved RSS or public API ingestion with source URLs.
- Add date-range filtering and trend comparisons.
- Add PDF and presentation exports.
- Store past briefs for change detection.
- Add a small evaluation dataset for factual-grounding checks.
