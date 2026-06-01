"""
Create Member Profile from JSON — PLACEHOLDER

Purpose:
    Generate a member profile .qmd file and update data/members.yml
    from a JSON input (e.g., parsed from a GitHub Issue or form submission).

Usage:
    python create_profile_from_json.py --input profile_data.json
    python create_profile_from_json.py --issue-number 42

Input JSON example:
    {
        "full_name": "Jane Doe",
        "affiliation": "University of Example",
        "country": "Country",
        "bio": "Short biography text.",
        "research_interests": ["topic1", "topic2"],
        "orcid": "https://orcid.org/0000-0000-0000-0000",
        "google_scholar": "",
        "linkedin": "",
        "website": "https://janedoe.example.com",
        "photo_url": "",
        "public_email": "",
        "publications": ["Doe, J. (2024). Title. Journal."],
        "rc42_relationship": "current-member"
    }

Output:
    - members/profiles/{slug}/index.qmd  — The member profile page
    - data/members.yml                   — Updated with new entry

TODO:
    - Implement GitHub Issue body parsing
    - Add photo download/copy logic
    - Add duplicate detection
    - Add validation for required fields
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
        description="Create a member profile .qmd from JSON data."
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to a JSON file with profile data."
    )
    parser.add_argument(
        "--issue-number",
        type=int,
        default=None,
        help="GitHub issue number to parse (requires GitHub API)."
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


def slugify(name: str) -> str:
    """
    Convert a name to a URL-safe slug.

    Args:
        name: The name to slugify.

    Returns:
        A lowercase, hyphen-separated slug.
    """
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug


def validate_profile_data(data: dict) -> list:
    """
    Validate required profile fields.

    Args:
        data: Dictionary with profile data.

    Returns:
        List of validation errors (empty if valid).
    """
    errors = []
    required_fields = ["full_name", "affiliation", "country", "bio", "research_interests"]
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")
    return errors


def generate_profile_qmd(data: dict) -> str:
    """
    Generate the .qmd content for a member profile.

    Args:
        data: Dictionary with profile data.

    Returns:
        The .qmd file content as a string.
    """
    name = data.get("full_name", "Member Name")
    affiliation = data.get("affiliation", "")
    country = data.get("country", "")
    bio = data.get("bio", "Content to be confirmed.")
    interests = data.get("research_interests", [])
    orcid = data.get("orcid", "")
    scholar = data.get("google_scholar", "")
    linkedin = data.get("linkedin", "")
    website = data.get("website", "")
    public_email = data.get("public_email", "")
    publications = data.get("publications", [])
    role = data.get("rc42_relationship", "Member")
    today = date.today().isoformat()

    # Build links section
    links = []
    if orcid:
        links.append(f'[ORCID]({orcid}){{target="_blank"}}')
    if scholar:
        links.append(f'[Google Scholar]({scholar}){{target="_blank"}}')
    if linkedin:
        links.append(f'[LinkedIn]({linkedin}){{target="_blank"}}')
    if website:
        links.append(f'[Website]({website}){{target="_blank"}}')
    links_str = "\n".join(links) if links else "*No links provided.*"

    # Build interests list
    interests_str = "\n".join(f"- {i}" for i in interests) if interests else "- *To be confirmed.*"

    # Build publications list
    pubs_str = "\n".join(f"{idx+1}. {p}" for idx, p in enumerate(publications)) if publications else "*No publications listed.*"

    # Build contact
    contact_str = f"📧 **Public email**: [{public_email}](mailto:{public_email})" if public_email else "📧 **Public email**: *Not provided.*"

    qmd = f"""---
title: "{name}"
description: "RC42 member profile — {name}"
---

::: {{.member-profile}}

::: {{.profile-header}}

::: {{.profile-info}}
# {name}

**Affiliation**: {affiliation}

**Country**: {country}

**RC42 Role**: {role}

::: {{.profile-links}}
{links_str}
:::

:::
:::

::: {{.profile-section}}
### Biography

{bio}
:::

::: {{.profile-section}}
### Research Interests

{interests_str}
:::

::: {{.profile-section}}
### Selected Works

{pubs_str}
:::

::: {{.profile-section}}
### Contact

{contact_str}
:::

---

*Last updated: {today}*

[Request profile update →](../../participate/update-profile.qmd){{.btn-rc42-dark}}

:::
"""
    return qmd


def update_members_yml(data: dict, site_dir: str):
    """
    Add a new entry to data/members.yml.

    Args:
        data: Dictionary with profile data.
        site_dir: Path to the rc42-site root directory.
    """
    members_file = os.path.join(site_dir, "data", "members.yml")

    if os.path.exists(members_file):
        with open(members_file, "r", encoding="utf-8") as f:
            members_data = yaml.safe_load(f) or {}
    else:
        members_data = {"members": []}

    slug = slugify(data.get("full_name", "unknown"))
    new_entry = {
        "id": slug,
        "name": data.get("full_name", ""),
        "affiliation": data.get("affiliation", ""),
        "country": data.get("country", ""),
        "role": data.get("rc42_relationship", "Member"),
        "bio": data.get("bio", ""),
        "research_interests": data.get("research_interests", []),
        "orcid": data.get("orcid", ""),
        "google_scholar": data.get("google_scholar", ""),
        "linkedin": data.get("linkedin", ""),
        "website": data.get("website", ""),
        "photo": data.get("photo_url", ""),
        "profile_confirmed": True,
        "last_updated": date.today().isoformat(),
    }

    members_data.setdefault("members", []).append(new_entry)

    with open(members_file, "w", encoding="utf-8") as f:
        yaml.dump(members_data, f, default_flow_style=False, allow_unicode=True)

    print(f"✅ Updated {members_file}")


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

    # Validate
    errors = validate_profile_data(data)
    if errors:
        print("❌ Validation errors:")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)

    # Generate .qmd
    qmd_content = generate_profile_qmd(data)
    slug = slugify(data["full_name"])
    profile_dir = os.path.join(args.site_dir, "members", "profiles", slug)

    if args.dry_run:
        print(f"--- DRY RUN: Would create {profile_dir}/index.qmd ---")
        print(qmd_content)
    else:
        os.makedirs(profile_dir, exist_ok=True)
        qmd_path = os.path.join(profile_dir, "index.qmd")
        with open(qmd_path, "w", encoding="utf-8") as f:
            f.write(qmd_content)
        print(f"✅ Created {qmd_path}")

        # Update members.yml
        update_members_yml(data, args.site_dir)

    print("✅ Done.")


if __name__ == "__main__":
    main()
