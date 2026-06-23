import os
import sys
import json
import yaml
import requests
import pandas as pd
from datetime import datetime
from urllib.error import URLError

def clean_column_names(df):
    """Strip whitespace from column names."""
    df.columns = df.columns.str.strip()
    return df

def generate_initials(first_name, surname):
    first = str(first_name).strip() if pd.notna(first_name) else ""
    last = str(surname).strip() if pd.notna(surname) else ""
    initials = ""
    if first:
        initials += first[0].upper()
    if last:
        initials += last[0].upper()
    return initials if initials else "U"

def format_name(first_name, surname):
    first = str(first_name).strip().title() if pd.notna(first_name) else ""
    last = str(surname).strip().title() if pd.notna(surname) else ""
    if first and last:
        return f"{first} {last}"
    return first or last

def is_active(start_date, end_date):
    """Check if member is active based on dates.
    If dates are empty or invalid, keep them (graceful fallback).
    """
    now = datetime.now()
    
    # Check start date
    if pd.notna(start_date):
        try:
            start = pd.to_datetime(start_date)
            if start > now:
                return False
        except:
            pass # Invalid format, assume valid
            
    # Check end date
    if pd.notna(end_date):
        try:
            end = pd.to_datetime(end_date)
            if end < now:
                return False
        except:
            pass # Invalid format, assume valid
            
    return True

def main():
    members_url = os.environ.get("MEMBERS_CSV_URL")
    photos_url = os.environ.get("PHOTOS_CSV_URL")

    if not members_url:
        print("CRITICAL: MEMBERS_CSV_URL environment variable is not set.")
        sys.exit(1)

    try:
        print("Downloading members list...")
        df_members = pd.read_csv(members_url)
        df_members = clean_column_names(df_members)
    except Exception as e:
        print(f"CRITICAL: Failed to download or parse members CSV: {e}")
        sys.exit(1)

    if 'Member ID' not in df_members.columns:
        print("CRITICAL: 'Member ID' column not found in members CSV.")
        sys.exit(1)

    df_photos = None
    if photos_url:
        try:
            print("Downloading photos list...")
            df_photos = pd.read_csv(photos_url)
            df_photos = clean_column_names(df_photos)
            if 'member_id' not in df_photos.columns:
                print("WARNING: 'member_id' column not found in photos CSV. Photos will not be merged.")
                df_photos = None
        except Exception as e:
            print(f"WARNING: Failed to download photos CSV. Proceeding without photos. Error: {e}")
    
    df_members['member_id'] = df_members['Member ID'].astype(str).str.strip()

    # Diagnostics variables
    total_rows = len(df_members)
    active_members = 0
    members_with_photo = 0
    members_without_photo = 0
    missing_member_id = int(df_members['member_id'].isna().sum() + (df_members['member_id'] == "").sum())
    duplicates = int(df_members.duplicated(subset=['member_id']).sum())
    unmatched_photos = 0

    if df_photos is not None:
        df_photos['member_id'] = df_photos['member_id'].astype(str).str.strip()
        photo_map = dict(zip(df_photos['member_id'], df_photos['photo_url']))
        unmatched_photos = len(set(df_photos['member_id']) - set(df_members['member_id']))
    else:
        photo_map = {}

    processed_members = []
    institutions_set = set()
    countries_set = set()

    for _, row in df_members.iterrows():
        # Check active status
        start_date = row.get('RC Membership Start Date')
        end_date = row.get('RC Membership End Date')
        if not is_active(start_date, end_date):
            continue
            
        active_members += 1
        
        m_id = str(row['member_id'])
        first_name = row.get('Member first name')
        surname = row.get('Member surname')
        dept = str(row.get('Department', '')).strip() if pd.notna(row.get('Department')) else ''
        inst = str(row.get('Institutional Affiliation', '')).strip() if pd.notna(row.get('Institutional Affiliation')) else ''
        
        # Build affiliation
        if dept and inst:
            affiliation_display = f"{dept}, {inst}"
        elif dept:
            affiliation_display = dept
        elif inst:
            affiliation_display = inst
        else:
            affiliation_display = ""
            
        country = str(row.get('Primary address country', '')).strip() if pd.notna(row.get('Primary address country')) else ''
        email = str(row.get('Email', '')).strip() if pd.notna(row.get('Email')) else ''
        
        if inst:
            institutions_set.add(inst)
        if country:
            countries_set.add(country)

        # Photos
        photo_url = str(photo_map.get(m_id, '')).strip()
        if photo_url and photo_url.lower() != 'nan':
            members_with_photo += 1
        else:
            photo_url = ""
            members_without_photo += 1

        member = {
            "id": m_id,
            "full_name": format_name(first_name, surname),
            "first_name": str(first_name).strip().title() if pd.notna(first_name) else "",
            "surname": str(surname).strip().title() if pd.notna(surname) else "",
            "initials": generate_initials(first_name, surname),
            "country": country,
            "institutional_affiliation": inst,
            "department": dept,
            "affiliation_display": affiliation_display,
            "email_private": email,
            "avatar_url": photo_url,
            "website_url": "",
            "linkedin_url": "",
            "orcid_url": "",
            "researchgate_url": "",
            "twitter_x_url": ""
        }
        processed_members.append(member)

    # Load overrides
    overrides_file = "data/members_manual_overrides.yml"
    overrides = {}
    if os.path.exists(overrides_file):
        try:
            with open(overrides_file, 'r', encoding='utf-8') as f:
                overrides = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"WARNING: Could not read overrides file: {e}")

    # Apply overrides
    for member in processed_members:
        m_id = member["id"]
        if m_id in overrides:
            o = overrides[m_id]
            if "website" in o: member["website_url"] = o["website"]
            if "linkedin" in o: member["linkedin_url"] = o["linkedin"]
            if "orcid" in o: member["orcid_url"] = o["orcid"]
            if "cv" in o: member["researchgate_url"] = o["cv"] # mapping CV to researchgate to maintain design or use generic
            if "twitter" in o: member["twitter_x_url"] = o["twitter"]
            if "display_name" in o and o["display_name"]: member["full_name"] = o["display_name"]
            if "hide_email" in o and o["hide_email"] == True: member["email_private"] = ""

    # Sort
    processed_members.sort(key=lambda x: (x['surname'], x['first_name']))

    # Write output
    os.makedirs('data', exist_ok=True)
    with open('data/members.json', 'w', encoding='utf-8') as f:
        json.dump(processed_members, f, ensure_ascii=False, indent=2)

    # Write diagnostics
    diagnostics = {
        "last_updated": datetime.now().isoformat(),
        "total_rows_read": total_rows,
        "active_members": active_members,
        "members_with_photo": members_with_photo,
        "members_without_photo": members_without_photo,
        "total_countries": len(countries_set),
        "total_institutions": len(institutions_set),
        "missing_member_id": missing_member_id,
        "duplicate_member_ids": duplicates,
        "unmatched_photos": unmatched_photos
    }
    
    with open('data/members_diagnostics.json', 'w', encoding='utf-8') as f:
        json.dump(diagnostics, f, ensure_ascii=False, indent=2)

    print("Successfully processed members.")

if __name__ == "__main__":
    main()
