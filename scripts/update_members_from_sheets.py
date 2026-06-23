import os
import sys
import json
import yaml
import shutil
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

def parse_member_date(value):
    if pd.isna(value):
        return pd.NaT
    value = str(value).strip()
    if value in {"", "-", "None", "nan", "NaN"}:
        return pd.NaT
    return pd.to_datetime(value, format="%d-%m-%Y", errors="coerce")

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
    missing_member_id = int(df_members['member_id'].isna().sum() + (df_members['member_id'] == "").sum())
    duplicates = int(df_members.duplicated(subset=['member_id']).sum())
    
    if df_photos is not None:
        df_photos['member_id'] = df_photos['member_id'].astype(str).str.strip()
        photo_map = dict(zip(df_photos['member_id'], df_photos['photo_url']))
        unmatched_photos = len(set(df_photos['member_id']) - set(df_members['member_id']))
    else:
        photo_map = {}
        unmatched_photos = 0

    # Date parsing and strict filtering
    df_members["rc_start_dt"] = df_members["RC Membership Start Date"].apply(parse_member_date)
    df_members["rc_end_dt"] = df_members["RC Membership End Date"].apply(parse_member_date)
    df_members["isa_expiration_dt"] = df_members["ISA Expiration Date"].apply(parse_member_date)

    today = pd.Timestamp.today().normalize()

    rc_active = (
        df_members["rc_start_dt"].notna()
        & df_members["rc_end_dt"].notna()
        & (df_members["rc_start_dt"] <= today)
        & (df_members["rc_end_dt"] >= today)
    )

    member_type = df_members["Member Type"].fillna("").astype(str).str.upper().str.strip()

    isa_active = (
        df_members["isa_expiration_dt"].notna()
        & (df_members["isa_expiration_dt"] >= today)
    )

    life_member = member_type.eq("LIFE")

    active_mask = rc_active & (isa_active | life_member)
    active_members_df = df_members.loc[active_mask].copy()
    excluded_members_df = df_members.loc[~active_mask].copy()

    # Diagnostics calculations
    invalid_dates_mask = df_members["rc_start_dt"].isna() | df_members["rc_end_dt"].isna() | df_members["isa_expiration_dt"].isna()
    excluded_invalid = int(invalid_dates_mask.sum())

    rc_expired_mask = ~invalid_dates_mask & ~rc_active
    excluded_rc = int(rc_expired_mask.sum())

    active_members_after_rc = int(rc_active.sum())

    isa_expired_mask = rc_active & ~isa_active & ~life_member
    excluded_isa = int(isa_expired_mask.sum())
    active_members_after_isa = len(active_members_df)

    excluded_isa_list = []
    for _, row in df_members.loc[isa_expired_mask].iterrows():
        excluded_isa_list.append({
            "member_id": str(row.get('member_id')),
            "full_name": format_name(row.get('Member first name'), row.get('Member surname')),
            "isa_expiration_date": str(row.get('ISA Expiration Date')),
            "rc_membership_end_date": str(row.get('RC Membership End Date'))
        })

    members_with_photo = 0
    members_without_photo = 0
    institutions_set = set()
    countries_set = set()

    processed_members = []

    for _, row in active_members_df.iterrows():
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
            if "cv" in o: member["researchgate_url"] = o["cv"]
            if "twitter" in o: member["twitter_x_url"] = o["twitter"]
            if "display_name" in o and o["display_name"]: member["full_name"] = o["display_name"]
            if "hide_email" in o and o["hide_email"] == True: member["email_private"] = ""

    # Sort
    processed_members.sort(key=lambda x: (x['surname'], x['first_name']))

    # Strict check before output
    expired_ids_that_must_not_publish = {"52540", "16506", "44628", "344629"}
    published_ids = {str(member.get("id", "")).strip() for member in processed_members}

    bad_ids = expired_ids_that_must_not_publish.intersection(published_ids)
    if bad_ids:
        raise RuntimeError(
            f"Expired ISA members are still being published: {sorted(bad_ids)}"
        )

    # Write output
    os.makedirs('data', exist_ok=True)
    with open('data/members.json', 'w', encoding='utf-8') as f:
        json.dump(processed_members, f, ensure_ascii=False, indent=2)

    # Write diagnostics
    diagnostics = {
        "last_updated": datetime.now().isoformat(),
        "total_rows_read": total_rows,
        "active_members_after_filter": active_members_after_isa,
        "excluded_isa_expired": excluded_isa,
        "excluded_rc_not_active": excluded_rc,
        "excluded_missing_or_invalid_dates": excluded_invalid,
        "expired_isa_members_excluded": excluded_isa_list,
        "active_members_after_rc_filter": active_members_after_rc,
        "active_members_after_isa_filter": active_members_after_isa,
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

    # Copy to docs/data/
    os.makedirs('docs/data', exist_ok=True)
    shutil.copy('data/members.json', 'docs/data/members.json')
    shutil.copy('data/members_diagnostics.json', 'docs/data/members_diagnostics.json')

    print("Successfully processed members.")

if __name__ == "__main__":
    main()
