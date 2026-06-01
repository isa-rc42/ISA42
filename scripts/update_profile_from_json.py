"""
Update Member Profile from JSON — PLACEHOLDER

Purpose:
    Update an existing member profile .qmd file and data/members.yml
    from a JSON input with updated fields.

Usage:
    python update_profile_from_json.py --input update_data.json --member-id "jane-doe"

Input JSON example:
    {
        "affiliation": "New University",
        "bio": "Updated biography.",
        "research_interests": ["new-topic1", "new-topic2"],
        "orcid": "https://orcid.org/0000-0000-0000-0001"
    }

Output:
    - Updated members/profiles/{member-id}/index.qmd
    - Updated data/members.yml

TODO:
    - Implement selective field update (only changed fields)
    - Add backup of previous version
    - Add validation for member existence
    - Add GitHub Issue body parsing
    - Add tests
"""

import argparse
import json
import os
import sys
from datetime import date

import yaml


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Update an existing member profile from JSON data."
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to a JSON file with updated profile data."
    )
    parser.add_argument(
        "--member-id",
        type=str,
        required=True,
        help="The member slug/ID (e.g., 'jane-doe')."
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
        help="Print changes without writing files."
    )
    return parser.parse_args()


def load_member_data(member_id: str, site_dir: str) -> dict:
    """
    Load existing member data from members.yml.

    Args:
        member_id: The member slug/ID.
        site_dir: Path to the rc42-site root directory.

    Returns:
        Dictionary with existing member data, or None if not found.
    """
    members_file = os.path.join(site_dir, "data", "members.yml")
    if not os.path.exists(members_file):
        return None

    with open(members_file, "r", encoding="utf-8") as f:
        members_data = yaml.safe_load(f) or {}

    for member in members_data.get("members", []):
        if member.get("id") == member_id:
            return member

    return None


def update_members_yml(member_id: str, updates: dict, site_dir: str):
    """
    Update a member entry in data/members.yml.

    Args:
        member_id: The member slug/ID.
        updates: Dictionary with fields to update.
        site_dir: Path to the rc42-site root directory.
    """
    members_file = os.path.join(site_dir, "data", "members.yml")

    with open(members_file, "r", encoding="utf-8") as f:
        members_data = yaml.safe_load(f) or {}

    updated = False
    for member in members_data.get("members", []):
        if member.get("id") == member_id:
            for key, value in updates.items():
                member[key] = value
            member["last_updated"] = date.today().isoformat()
            updated = True
            break

    if not updated:
        print(f"❌ Member '{member_id}' not found in members.yml.")
        return False

    with open(members_file, "w", encoding="utf-8") as f:
        yaml.dump(members_data, f, default_flow_style=False, allow_unicode=True)

    print(f"✅ Updated {members_file}")
    return True


def main():
    """Main entry point."""
    args = parse_args()

    # Load update data
    with open(args.input, "r", encoding="utf-8") as f:
        updates = json.load(f)

    # Check member exists
    existing = load_member_data(args.member_id, args.site_dir)
    if existing is None:
        print(f"❌ Member '{args.member_id}' not found.")
        sys.exit(1)

    if args.dry_run:
        print(f"--- DRY RUN: Would update member '{args.member_id}' ---")
        print(f"Current data: {json.dumps(existing, indent=2)}")
        print(f"Updates: {json.dumps(updates, indent=2)}")
    else:
        # TODO: Also regenerate the .qmd file from the updated data
        update_members_yml(args.member_id, updates, args.site_dir)

        # TODO: Regenerate profile .qmd
        # from create_profile_from_json import generate_profile_qmd
        # merged_data = {**existing, **updates}
        # qmd_content = generate_profile_qmd(merged_data)
        # ... write to file

        print("⚠️  Note: The .qmd profile file should also be regenerated.")
        print("   This step is not yet implemented in this placeholder script.")

    print("✅ Done.")


if __name__ == "__main__":
    main()
