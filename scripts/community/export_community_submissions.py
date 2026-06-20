import os
import sys
import json
import re
import yaml
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import gspread
from google.oauth2.service_account import Credentials

SANTIAGO_TZ = ZoneInfo("America/Santiago")

def today_santiago_iso():
    return datetime.now(SANTIAGO_TZ).date().isoformat()

# --- Configuration ---
PRIVATE_FIELDS = [
    "submitter_email", "Email Address", "submitter_name", "editorial_comments",
    "editorial_notes", "rejection_reason", "reviewing_member", "publishing_member",
    "editor_responsible", "privacy_checked", "ready_for_export", "duplicate_flag",
    "timestamp"
]

REQUIRED_YAML_FIELDS = [
    "id", "title", "description", "type", "category", "language", "date_published"
]

def load_credentials():
    service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        print("ERROR: GOOGLE_SERVICE_ACCOUNT_JSON is not set.")
        sys.exit(1)
        
    try:
        creds_dict = json.loads(service_account_json)
        scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return creds
    except Exception as e:
        print(f"ERROR: Failed to load Google Credentials: {e}")
        sys.exit(1)

def is_exportable(row):
    try:
        if row.get("review_status", "").strip().lower() != "approved":
            return False
        if row.get("publish_on_site", "").strip().lower() != "yes":
            return False
        if row.get("privacy_checked", "").strip().lower() != "yes":
            return False
        if row.get("duplicate_flag", "").strip().lower() != "no":
            return False
        if row.get("ready_for_export", "").strip().lower() != "yes":
            return False
            
        url_checked = row.get("url_checked", "").strip().lower()
        if url_checked not in ["yes", "not_applicable"]:
            return False
            
        has_url = bool(row.get("public_url", "").strip())
        if has_url and url_checked != "yes":
            return False
        if not has_url and url_checked != "not_applicable":
            return False
            
        return True
    except AttributeError:
        return False

def parse_flexible_date(value, row_number=None, field_name="date", required=False):
    """
    Parse common date formats from Google Sheets and return YYYY-MM-DD.

    If required=True and the value is empty or invalid, return today's date
    in America/Santiago and print a warning.

    If required=False and the value is empty or invalid, return an empty string
    and print a warning only for invalid non-empty values.
    """
    today = today_santiago_iso()

    if value is None:
        if required:
            print(f"WARNING (Row {row_number}): {field_name} is empty. Using today's date: {today}")
            return today
        return ""

    if isinstance(value, datetime):
        return value.date().isoformat()

    if isinstance(value, date):
        return value.isoformat()

    raw = str(value).strip()

    if raw == "":
        if required:
            print(f"WARNING (Row {row_number}): {field_name} is empty. Using today's date: {today}")
            return today
        return ""

    # Google Sheets / Excel serial date support
    if re.fullmatch(r"\d+(\.\d+)?", raw):
        try:
            serial = float(raw)
            # Excel/Google Sheets date origin. Handles common serial dates.
            parsed = date(1899, 12, 30) + timedelta(days=int(serial))
            if 1900 <= parsed.year <= 2100:
                return parsed.isoformat()
        except Exception:
            pass

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%m/%d/%Y",
        "%Y/%m/%d"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue

    if required:
        print(
            f"WARNING (Row {row_number}): {field_name} could not be parsed: {raw!r}. "
            f"Using today's date: {today}"
        )
        return today

    print(
        f"WARNING (Row {row_number}): {field_name} could not be parsed: {raw!r}. "
        "Leaving it empty."
    )
    return ""

def parse_tags(tags_str):
    if not tags_str:
        return []
    return [tag.strip() for tag in tags_str.split(",") if tag.strip()]

def main():
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("ERROR: GOOGLE_SHEET_ID is not set.")
        sys.exit(1)
        
    tab_name = os.environ.get("COMMUNITY_SHEET_TAB", "Editorial Review")
    output_path = os.environ.get("COMMUNITY_OUTPUT_PATH", "data/community_submissions.yml")
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print("Connecting to Google Sheets...")
    creds = load_credentials()
    client = gspread.authorize(creds)
    
    try:
        sheet = client.open_by_key(sheet_id).worksheet(tab_name)
        # Get all records as list of dicts
        rows = sheet.get_all_records()
    except Exception as e:
        print(f"ERROR: Failed to fetch data from sheet '{tab_name}': {e}")
        sys.exit(1)
        
    print(f"Total rows read from '{tab_name}': {len(rows)}")
    
    export_data = []
    seen_ids = set()
    
    for i, row in enumerate(rows, start=2): # Start at 2 to match sheet rows
        # Only process exportable rows
        if not is_exportable(row):
            continue
            
        # Build public record from scratch
        record = {}
        
        # 1. ID
        sub_id = str(row.get("submission_id", "")).strip()
        if not sub_id:
            print(f"ERROR (Row {i}): Missing submission_id for exportable row.")
            sys.exit(1)
        if sub_id in seen_ids:
            print(f"ERROR (Row {i}): Duplicate submission_id detected: {sub_id}")
            sys.exit(1)
        record["id"] = sub_id
        seen_ids.add(sub_id)
        
        # 2. Title
        title = str(row.get("edited_title", "")).strip()
        if not title:
            title = str(row.get("submission_title", "")).strip()
        record["title"] = title
        
        # 3. Description
        desc = str(row.get("edited_description", "")).strip()
        if not desc:
            desc = str(row.get("short_description", "")).strip()
        record["description"] = desc
        
        # 4. Type
        record["type"] = str(row.get("submission_type", "")).strip()
        
        # 5. Category
        record["category"] = str(row.get("thematic_category", "")).strip()
        
        # 6. Territory
        record["territory"] = str(row.get("territory_scope", "")).strip()
        
        # 7. Organization
        record["organization"] = str(row.get("associated_organization", "")).strip()
        
        # 8. URL
        record["url"] = str(row.get("public_url", "")).strip()
        
        # 9. Language
        record["language"] = str(row.get("submission_language", "")).strip()
        
        # 10. Member Display Name
        auth = str(row.get("display_member_name_authorized", "")).strip().lower()
        if auth == "yes":
            record["member_display_name"] = str(row.get("public_member_display_name", "")).strip()
        else:
            record["member_display_name"] = ""
            
        # 11. Date Published
        record["date_published"] = parse_flexible_date(
            row.get("date_published", ""),
            row_number=i,
            field_name="date_published",
            required=True,
        )
        
        # 11b. Optional dates
        for opt_date_field in ["relevant_date", "deadline", "event_date", "date_event", "publication_date"]:
            if opt_date_field in row:
                record[opt_date_field] = parse_flexible_date(
                    row.get(opt_date_field, ""),
                    row_number=i,
                    field_name=opt_date_field,
                    required=False
                )
        
        # 12. Tags
        record["tags"] = parse_tags(str(row.get("suggested_tags", "")))
        
        # Validate Required
        for req in REQUIRED_YAML_FIELDS:
            if not record.get(req):
                print(f"ERROR (Row {i}): Missing required field '{req}' for ID '{sub_id}'.")
                sys.exit(1)
                
        # Security: ensure no private fields leaked
        for field in record.keys():
            if field in PRIVATE_FIELDS:
                print(f"CRITICAL ERROR (Row {i}): Private field '{field}' detected in export record. Aborting.")
                sys.exit(1)
                
        export_data.append(record)

    # Final Security Check on all generated items
    for item in export_data:
        for p_field in PRIVATE_FIELDS:
            if p_field in item:
                print(f"CRITICAL ERROR: Private field '{p_field}' found in final YAML structure. Aborting.")
                sys.exit(1)

    print(f"Validation successful. Exporting {len(export_data)} rows.")
    
    # Write YAML
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(export_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"Data successfully written to {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to write YAML output file: {e}")
        sys.exit(1)

    # Write JSON
    json_output_path = output_path.rsplit(".", 1)[0] + ".json"
    try:
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        print(f"Data successfully written to {json_output_path}")
    except Exception as e:
        print(f"ERROR: Failed to write JSON output file: {e}")
        sys.exit(1)

    print(f"Exported IDs: {[r['id'] for r in export_data]}")

if __name__ == "__main__":
    main()
