"""
Create Post from JSON — PLACEHOLDER

Purpose:
    Generate a news, event, opportunity, or blog post .qmd file
    from a JSON input (e.g., parsed from a GitHub Issue or form submission).

Usage:
    python create_post_from_json.py --input post_data.json --type news
    python create_post_from_json.py --issue-number 42

Input JSON example (news):
    {
        "title": "New publication by RC42 member",
        "description": "Short description of the news item.",
        "main_text": "Full text of the news item.",
        "contributor_name": "Jane Doe",
        "contributor_email": "jane@example.com",
        "date": "2025-06-15",
        "url": "https://example.com/article",
        "type": "news"
    }

Output:
    - news/posts/{slug}/index.qmd  — The post file
    - OR events/events.yml         — Updated with new event entry
    - OR opportunities/opportunities.yml — Updated with new opportunity

TODO:
    - Implement GitHub Issue body parsing
    - Add event and opportunity YAML update logic
    - Add blog post generation
    - Add newsletter item handling
    - Add duplicate detection
    - Add tests
"""

import argparse
import json
import os
import re
import sys
from datetime import date

import yaml


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Create a post .qmd from JSON data."
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to a JSON file with post data."
    )
    parser.add_argument(
        "--issue-number",
        type=int,
        default=None,
        help="GitHub issue number to parse."
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["news", "event", "opportunity", "blog", "resource", "newsletter"],
        default="news",
        help="Type of post to create."
    )
    parser.add_argument(
        "--site-dir",
        type=str,
        default=".",
        help="Path to the rc42-site root directory."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print output without writing files."
    )
    return parser.parse_args()


def slugify(title: str) -> str:
    """
    Convert a title to a URL-safe slug.

    Args:
        title: The title to slugify.

    Returns:
        A lowercase, hyphen-separated slug.
    """
    slug = title.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug[:60]  # Limit slug length


def validate_post_data(data: dict) -> list:
    """
    Validate required post fields.

    Args:
        data: Dictionary with post data.

    Returns:
        List of validation errors (empty if valid).
    """
    errors = []
    required = ["title", "main_text", "contributor_name"]
    for field in required:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")
    return errors


def generate_news_qmd(data: dict) -> str:
    """
    Generate a news post .qmd.

    Args:
        data: Dictionary with post data.

    Returns:
        The .qmd file content.
    """
    title = data.get("title", "Untitled")
    description = data.get("description", "")
    main_text = data.get("main_text", "")
    author = data.get("contributor_name", "RC42")
    post_date = data.get("date", date.today().isoformat())
    url = data.get("url", "")

    url_section = f"\n**Source**: [{url}]({url}){{target=\"_blank\"}}\n" if url else ""

    qmd = f"""---
title: "{title}"
description: "{description}"
author: "{author}"
date: "{post_date}"
categories: [news]
---

## {title}

{main_text}
{url_section}
"""
    return qmd


def add_event_to_yaml(data: dict, site_dir: str):
    """
    Add a new event to data/events.yml.

    Args:
        data: Dictionary with event data.
        site_dir: Path to the rc42-site root directory.
    """
    events_file = os.path.join(site_dir, "data", "events.yml")

    if os.path.exists(events_file):
        with open(events_file, "r", encoding="utf-8") as f:
            events_data = yaml.safe_load(f) or {}
    else:
        events_data = {"events": []}

    new_event = {
        "title": data.get("title", ""),
        "date": data.get("date", ""),
        "location": data.get("location", "To be confirmed"),
        "type": "event",
        "description": data.get("main_text", data.get("description", "")),
        "url": data.get("url", ""),
        "status": "upcoming",
    }

    events_data.setdefault("events", []).append(new_event)

    with open(events_file, "w", encoding="utf-8") as f:
        yaml.dump(events_data, f, default_flow_style=False, allow_unicode=True)

    print(f"✅ Added event to {events_file}")


def main():
    """Main entry point."""
    args = parse_args()

    # Load data
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif args.issue_number:
        # TODO: Implement GitHub Issue parsing
        print(f"⚠️  GitHub Issue parsing not implemented. Issue #{args.issue_number}")
        sys.exit(1)
    else:
        print("❌ Provide --input or --issue-number.")
        sys.exit(1)

    # Override type if specified in data
    post_type = data.get("type", args.type)

    # Validate
    errors = validate_post_data(data)
    if errors:
        print("❌ Validation errors:")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)

    # Route by type
    if post_type == "news":
        qmd_content = generate_news_qmd(data)
        slug = slugify(data["title"])
        post_dir = os.path.join(args.site_dir, "news", "posts", slug)

        if args.dry_run:
            print(f"--- DRY RUN: Would create {post_dir}/index.qmd ---")
            print(qmd_content)
        else:
            os.makedirs(post_dir, exist_ok=True)
            qmd_path = os.path.join(post_dir, "index.qmd")
            with open(qmd_path, "w", encoding="utf-8") as f:
                f.write(qmd_content)
            print(f"✅ Created {qmd_path}")

    elif post_type == "event":
        if args.dry_run:
            print("--- DRY RUN: Would add event to events.yml ---")
            print(json.dumps(data, indent=2))
        else:
            add_event_to_yaml(data, args.site_dir)

    elif post_type == "opportunity":
        # TODO: Implement opportunity YAML update
        print("⚠️  Opportunity post creation not yet implemented.")

    elif post_type == "blog":
        # TODO: Implement blog post generation (similar to news)
        print("⚠️  Blog post creation not yet implemented.")

    elif post_type == "resource":
        # TODO: Implement resource YAML update
        print("⚠️  Resource post creation not yet implemented.")

    else:
        print(f"⚠️  Unknown post type: {post_type}")
        sys.exit(1)

    print("✅ Done.")


if __name__ == "__main__":
    main()
