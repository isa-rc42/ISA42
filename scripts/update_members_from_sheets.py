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

    # 1. Download past members source
    past_url = os.environ.get("PAST_MEMBERS_CSV_URL")
    df_past_sheet = pd.DataFrame()
    past_rows_read = 0
    if past_url:
        try:
            print("Downloading past members list...")
            df_past_sheet = pd.read_csv(past_url)
            df_past_sheet = clean_column_names(df_past_sheet)
            past_rows_read = len(df_past_sheet)
            if 'Member ID' in df_past_sheet.columns:
                df_past_sheet['source_type'] = 'historical'
            else:
                print("WARNING: 'Member ID' column not found in past members CSV.")
                df_past_sheet = pd.DataFrame()
        except Exception as e:
            print(f"WARNING: Failed to download or process past members CSV: {e}")
            df_past_sheet = pd.DataFrame()

    # 2. Combine all membership rows
    df_members['source_type'] = 'current'
    dfs = [df_members]
    if not df_past_sheet.empty:
        dfs.append(df_past_sheet)

    all_membership_rows = pd.concat(dfs, ignore_index=True)
    if 'Member ID' in all_membership_rows.columns:
        all_membership_rows['member_id'] = all_membership_rows['Member ID'].astype(str).str.strip()

    all_membership_rows = all_membership_rows[
        all_membership_rows['member_id'].notna()
        & (all_membership_rows['member_id'] != "")
        & (all_membership_rows['member_id'].str.lower() != "nan")
    ].copy()

    # 3 & 4. Date parsing
    all_membership_rows["rc_start_dt"] = all_membership_rows["RC Membership Start Date"].apply(parse_member_date)
    all_membership_rows["rc_end_dt"] = all_membership_rows["RC Membership End Date"].apply(parse_member_date)
    if "ISA Expiration Date" in all_membership_rows.columns:
        all_membership_rows["isa_expiration_dt"] = all_membership_rows["ISA Expiration Date"].apply(parse_member_date)
    else:
        all_membership_rows["isa_expiration_dt"] = pd.NaT

    # 5. Calculate RC42 active mask
    today = pd.Timestamp.today().normalize()

    rc_active_mask = (
        all_membership_rows["rc_start_dt"].notna()
        & all_membership_rows["rc_end_dt"].notna()
        & (all_membership_rows["rc_start_dt"] <= today)
        & (all_membership_rows["rc_end_dt"] >= today)
    )

    # 7. Keep best active candidate row per Member ID
    active_candidates_df = all_membership_rows.loc[rc_active_mask].copy()
    active_candidates_df = active_candidates_df.sort_values(
        by=["rc_end_dt", "rc_start_dt"],
        ascending=[False, False]
    )
    active_members_df = active_candidates_df.drop_duplicates(
        subset=["member_id"],
        keep="first"
    ).copy()

    # 8. Create active_member_ids
    active_member_ids = set(active_members_df["member_id"].astype(str).str.strip())

    # Build active directory list
    processed_members = []
    members_with_photo = 0
    members_without_photo = 0
    institutions_set = set()
    countries_set = set()

    for _, row in active_members_df.iterrows():
        m_id = str(row['member_id'])
        first_name = row.get('Member first name')
        surname = row.get('Member surname')
        dept = str(row.get('Department', '')).strip() if pd.notna(row.get('Department')) else ''
        inst = str(row.get('Institutional Affiliation', '')).strip() if pd.notna(row.get('Institutional Affiliation')) else ''
        
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

    # Load manual overrides
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

    # Sort active members
    processed_members.sort(key=lambda x: (x['surname'], x['first_name']))

    # Write active directory output
    os.makedirs('data', exist_ok=True)
    with open('data/members.json', 'w', encoding='utf-8') as f:
        json.dump(processed_members, f, ensure_ascii=False, indent=2)

    # 9. Past members processing
    past_candidates_df = all_membership_rows.loc[
        ~all_membership_rows["member_id"].isin(active_member_ids)
    ].copy()

    past_unique_ids = past_candidates_df['member_id'].nunique()
    past_members = []
    past_from_historical = 0
    past_from_expired = 0

    for m_id, group in past_candidates_df.groupby('member_id'):
        min_start = group['rc_start_dt'].min()
        max_end = group['rc_end_dt'].max()

        # Step 11: Publicar como past solo si last_rc_end_date < today
        if pd.isna(max_end) or max_end >= today:
            continue

        group_sorted = group.sort_values(by='rc_end_dt', ascending=True, na_position='first')
        rows_reversed = list(group_sorted.iloc[::-1].iterrows())

        def get_best_val(col_name):
            for _, r in rows_reversed:
                val = r.get(col_name)
                if pd.notna(val):
                    s = str(val).strip()
                    if s and s.lower() not in {"nan", "none", "-"}:
                        return s
            return ""

        first_name = get_best_val('Member first name')
        surname = get_best_val('Member surname')
        member_name = get_best_val('Member name')

        fname_formatted = first_name.title() if first_name else ""
        sname_formatted = surname.title() if surname else ""

        if fname_formatted and sname_formatted:
            full_name = f"{fname_formatted} {sname_formatted}"
        elif fname_formatted or sname_formatted:
            full_name = fname_formatted or sname_formatted
        else:
            full_name = member_name.title() if member_name else ""

        country = get_best_val('Primary address country')
        inst = get_best_val('Institutional Affiliation')
        dept = get_best_val('Department')

        if dept and inst:
            affil_display = f"{dept}, {inst}"
        elif dept:
            affil_display = dept
        elif inst:
            affil_display = inst
        else:
            affil_display = ""

        first_start_str = min_start.strftime("%Y-%m-%d") if pd.notna(min_start) else ""
        last_end_str = max_end.strftime("%Y-%m-%d") if pd.notna(max_end) else ""

        start_year = first_start_str[:4] if first_start_str else ""
        end_year = last_end_str[:4] if last_end_str else ""

        if start_year and end_year:
            if start_year == end_year:
                mem_years = start_year
            else:
                mem_years = f"{start_year}–{end_year}"
        elif start_year:
            mem_years = start_year
        elif end_year:
            mem_years = end_year
        else:
            mem_years = ""

        sources = set(group['source_type'])
        if 'historical' in sources:
            past_from_historical += 1
        if 'current' in sources and 'historical' not in sources:
            past_from_expired += 1

        past_members.append({
            "id": m_id,
            "full_name": full_name,
            "first_name": fname_formatted,
            "surname": sname_formatted,
            "country": country,
            "institutional_affiliation": inst,
            "department": dept,
            "affiliation_display": affil_display,
            "first_rc_start_date": first_start_str,
            "last_rc_end_date": last_end_str,
            "membership_years": mem_years
        })

    # Sort past members
    past_members.sort(key=lambda x: (x.get("full_name") or "").lower(), reverse=False)
    past_members.sort(key=lambda x: x.get("last_rc_end_date") or "0000-00-00", reverse=True)

    # 12 & 13. Hard validations
    bad_past_future = [
        member for member in past_members
        if member.get("last_rc_end_date") and member["last_rc_end_date"] >= today.strftime("%Y-%m-%d")
    ]

    if bad_past_future:
        raise RuntimeError(
            "Past members contains members with future/current RC end dates: "
            + ", ".join([m.get("id", "") for m in bad_past_future])
        )

    past_member_ids = {str(member.get("id", "")).strip() for member in past_members}
    overlap = active_member_ids.intersection(past_member_ids)

    if overlap:
        raise RuntimeError(
            f"Members duplicated in active and past outputs: {sorted(overlap)}"
        )

    with open('data/past_members.json', 'w', encoding='utf-8') as f:
        json.dump(past_members, f, ensure_ascii=False, indent=2)

    # 14. Write diagnostics
    diagnostics = {
        "last_updated": datetime.now().isoformat(),
        "active_members_rule": "RC Membership Start Date <= today and RC Membership End Date >= today",
        "isa_expiration_used_as_filter": False,
        "past_members_rule": "last_rc_end_date < today and not active",
        "total_rows_read": total_rows,
        "active_members_published": len(processed_members),
        "past_members_total_rows_read": past_rows_read,
        "past_members_unique_ids": past_unique_ids,
        "past_members_from_historical_sheet": past_from_historical,
        "past_members_from_expired_current_sheet": past_from_expired,
        "past_members_published": len(past_members),
        "active_past_overlap": len(overlap),
        "past_members_with_future_rc_end_date": len(bad_past_future),
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
    shutil.copy('data/past_members.json', 'docs/data/past_members.json')

    print("Successfully processed members.")

if __name__ == "__main__":
    main()
