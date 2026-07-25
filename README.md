# AI-Powered Competitor Marketing Brief Agent

A portfolio-ready Streamlit application that automatically collects public
competitor app evidence and converts it into an evidence-grounded marketing brief.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-competitor-marketing-brief-agent-j8cvm6j4nurwpf6bkhzzgw.streamlit.app/)

**Live demo:** https://ai-competitor-marketing-brief-agent-j8cvm6j4nurwpf6bkhzzgw.streamlit.app/

The project demonstrates the intersection of marketing intelligence, automation,
analytics, prompt design, and product thinking. A scheduled collector records
public Apple App Store release notes, positioning copy, ratings, and source URLs.
The public app uses a transparent rule-based workflow and does not require real AI.

The recommended public portfolio deployment runs in **Rule-based portfolio
demo** mode without any API key. This keeps the app free to operate, prevents
API-credit abuse, and ensures that uploaded data is not sent to a third-party
model. The optional OpenAI integration remains in the codebase as an
architecture and testing example.

## What the app does

1. Collects configured competitors from Apple's public, keyless lookup API.
2. Deduplicates observations and keeps a bounded history in CSV.
3. Refreshes the repository every day through GitHub Actions.
4. Loads the latest collected evidence, with sample/uploaded CSV fallbacks.
5. Validates and filters observations by competitor and marketing category.
6. Visualizes competitor activity and category coverage.
7. Generates a structured brief with either:
   - OpenAI-powered evidence synthesis; or
   - a deterministic rule-based fallback.
8. Exports the report as Markdown and JSON, plus the exact filtered evidence as
   CSV.

## Why this is an AI Marketing project

Marketing teams often collect competitor observations across campaigns,
product launches, content formats, and brand messages. The difficult part is
turning those notes into a concise, decision-useful narrative.

This application productizes that workflow:

- structured evidence intake;
- automated, keyless public-data collection;
- source URLs and collection timestamps;
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
- Requests
- Apple iTunes Search API
- GitHub Actions
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
|-- collector.py
|-- config/
|   `-- competitors.json
|-- requirements.txt
|-- data/
|   |-- sample_competitor_data.csv
|   `-- collected_competitor_data.csv
|-- tests/
|   |-- test_brief_generator.py
|   `-- test_collector.py
|-- .github/
|   `-- workflows/
|       `-- collect-competitor-data.yml
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

Automatically collected rows can also include:

| Column | Meaning |
|---|---|
| `source_url` | Exact public App Store evidence link |
| `collected_at` | Date the collector observed the record |
| `item_id` | Stable deduplication identifier |

The sample fallback is synthetic portfolio data and must not be represented as
official market data. The collected dataset is a dated public-source snapshot,
not a complete market dataset.

## Configure automatic collection

Edit `config/competitors.json` to change the monitored apps:

```json
{
  "country": "cn",
  "max_records_per_competitor": 60,
  "competitors": [
    {
      "name": "Tencent News",
      "track_id": 399363156
    }
  ]
}
```

`track_id` is the numeric ID at the end of an Apple App Store URL. Run a manual
collection with:

```powershell
python collector.py `
  --config config/competitors.json `
  --output data/collected_competitor_data.csv
```

The included GitHub Actions workflow runs at 09:15 China Standard Time every
day and can also be started manually from the repository's **Actions** tab. It
commits only when the collected evidence changes; Streamlit Community Cloud
then redeploys the updated repository automatically.

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
2. Show that the current evidence was collected automatically and retains links.
3. Filter two or more competitors and relevant categories.
4. Show the activity and category charts.
5. Generate the AI brief.
6. Point out grounded recommendations, limitations, and report metadata.
7. Download the report and exact evidence used.

## Current limitations

- Automatic collection currently covers Apple App Store product evidence only.
- App Store ratings are snapshots and may vary by storefront and version.
- The collector runs daily rather than in real time.
- News sites, social media, Android stores, campaigns, and paid media are not yet
  connected.
- Model output quality depends on source quality and evidence coverage.
- The app does not persist datasets or reports in a database.
- A human should review recommendations before business use.
- Live API behavior requires a valid OpenAI API key and available model access.

## Responsible-use choices

- Evidence is sent only when the user selects AI-powered generation.
- The collector uses a public API, does not bypass login controls, and stores
  source links for review.
- Input is capped before it is included in the model prompt.
- The prompt prohibits invented facts and metrics.
- The exact filtered evidence can be exported for review.
- The report always includes limitations and generation metadata.
- Rule-based mode provides a no-cost, auditable fallback.

## Next improvements

- Add additional approved APIs for news, social, and Android app signals.
- Add date-range filtering and trend comparisons.
- Add PDF and presentation exports.
- Store past briefs for change detection.
- Add a small evaluation dataset for factual-grounding checks.
