# RC42 Social Psychology — Automation Scripts

This directory contains placeholder scripts for future automation of the RC42 portal editorial workflow.

## Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| `llm_review_submission.py` | Send a submission to an LLM for draft preparation | Placeholder |
| `create_profile_from_json.py` | Generate a member profile `.qmd` from JSON data | Placeholder |
| `update_profile_from_json.py` | Update an existing member profile from JSON data | Placeholder |
| `create_post_from_json.py` | Generate a news/event/opportunity post from JSON data | Placeholder |

## How These Scripts Fit the Workflow

1. A user submits content via the website form or GitHub Issue.
2. A GitHub Action parses the submission into JSON.
3. One of these scripts processes the JSON to generate/update `.qmd` or `.yml` files.
4. The result is submitted as a Pull Request.
5. A human editor reviews and approves the PR.
6. The site is rebuilt upon merge.

## Requirements

- Python 3.10+
- `pyyaml` package
- For LLM integration: an API key (e.g., `OPENAI_API_KEY`)

## Important

⚠️ These scripts are **placeholders**. They provide the structure and intended logic but require full implementation and testing before production use.

⚠️ No content is published automatically. All output from these scripts must undergo human review.
