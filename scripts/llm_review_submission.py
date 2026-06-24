"""
LLM Review Submission Script - PLACEHOLDER

Purpose:
    Send a submission (from a GitHub Issue) to an LLM for editorial draft
    preparation. The LLM output is a suggested revision or formatted version
    of the submission, ready for human review.

Usage:
    python llm_review_submission.py --issue-number 42

Workflow:
    1. Reads the issue body (from GitHub API or local JSON).
    2. Sends the content to an LLM with editorial instructions.
    3. Receives a draft response.
    4. Outputs the draft as a formatted .qmd or .yml snippet.
    5. The output is used by a GitHub Action to create a Pull Request.

Requirements:
    - OPENAI_API_KEY (or equivalent) environment variable
    - pyyaml
    - requests or openai library

TODO:
    - Implement GitHub API integration to fetch issue body
    - Implement LLM API call with appropriate prompt
    - Implement output formatting for .qmd and .yml
    - Add error handling and validation
    - Add logging
    - Add tests
"""

import argparse
import json
import os
import sys
import yaml


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Send a submission to an LLM for editorial draft preparation."
    )
    parser.add_argument(
        "--issue-number",
        type=int,
        required=True,
        help="GitHub issue number to process."
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default=None,
        help="Path to a local JSON file with the issue data (for testing)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Directory to write the draft output."
    )
    return parser.parse_args()


def fetch_issue_data(issue_number: int, input_file: str = None) -> dict:
    """
    Fetch issue data from GitHub API or a local file.

    Args:
        issue_number: The GitHub issue number.
        input_file: Optional path to a local JSON file.

    Returns:
        Dictionary with issue data.
    """
    if input_file:
        with open(input_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # TODO: Implement GitHub API fetch
    # import requests
    # token = os.environ.get("GITHUB_TOKEN")
    # repo = os.environ.get("GITHUB_REPOSITORY", "org/rc42-site")
    # url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    # headers = {"Authorization": f"token {token}"}
    # response = requests.get(url, headers=headers)
    # return response.json()

    print(f"⚠️  GitHub API fetch not implemented. Issue #{issue_number}")
    return {
        "number": issue_number,
        "title": "Example submission",
        "body": "This is a placeholder issue body.",
        "labels": [{"name": "content"}, {"name": "news"}]
    }


def prepare_llm_prompt(issue_data: dict) -> str:
    """
    Prepare the prompt for the LLM based on the issue data.

    Args:
        issue_data: Dictionary with issue data.

    Returns:
        The prompt string.
    """
    # TODO: Customize prompt based on issue labels (profile, news, event, etc.)
    prompt = f"""You are an editorial assistant for the RC42 Social Psychology portal.

Review the following submission and prepare a clean, publication-ready draft.
Follow academic, professional English standards.
Do not fabricate information - only use what is provided.
Flag any missing or unclear information.

Submission:
Title: {issue_data.get('title', 'Untitled')}
Body:
{issue_data.get('body', 'No content provided.')}

Output a formatted draft suitable for the RC42 portal.
"""
    return prompt


def call_llm(prompt: str) -> str:
    """
    Send the prompt to an LLM and return the response.

    Args:
        prompt: The prompt string.

    Returns:
        The LLM response text.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set. Returning placeholder response.")
        return "<!-- LLM draft not generated: API key not configured. -->\n"

    # TODO: Implement actual LLM API call
    # import openai
    # openai.api_key = api_key
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": prompt}],
    #     max_tokens=2000,
    #     temperature=0.3
    # )
    # return response.choices[0].message.content

    print("⚠️  LLM API call not implemented.")
    return "<!-- LLM draft placeholder -->\n"


def save_draft(draft: str, issue_number: int, output_dir: str):
    """
    Save the LLM draft to a file.

    Args:
        draft: The draft content.
        issue_number: The issue number (for filename).
        output_dir: Directory to save the draft.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"draft-issue-{issue_number}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(draft)
    print(f"✅ Draft saved to {filename}")


def validate_issue_data(issue_data: dict) -> bool:
    """
    Basic validation of issue data.

    Args:
        issue_data: Dictionary with issue data.

    Returns:
        True if valid, False otherwise.
    """
    if not issue_data.get("title"):
        print("❌ Issue title is missing.")
        return False
    if not issue_data.get("body"):
        print("❌ Issue body is missing.")
        return False
    return True


def main():
    """Main entry point."""
    args = parse_args()

    print(f"📋 Processing issue #{args.issue_number}...")

    # 1. Fetch issue data
    issue_data = fetch_issue_data(args.issue_number, args.input_file)

    # 2. Validate
    if not validate_issue_data(issue_data):
        sys.exit(1)

    # 3. Prepare prompt
    prompt = prepare_llm_prompt(issue_data)

    # 4. Call LLM
    draft = call_llm(prompt)

    # 5. Save draft
    save_draft(draft, args.issue_number, args.output_dir)

    print("✅ Done.")


if __name__ == "__main__":
    main()
