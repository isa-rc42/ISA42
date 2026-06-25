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

    # Past members processing
    active_member_ids = {str(member["id"]).strip() for member in processed_members}
    past_url = os.environ.get("PAST_MEMBERS_CSV_URL")
    past_members = []
    past_rows_read = 0
    past_unique_ids = 0
    past_excluded_active = 0
    past_from_historical = 0
    past_from_expired = 0

    dfs_to_concat = []

    # 1. Historical sheet
    if past_url:
        try:
            print("Downloading past members list...")
            df_past_sheet = pd.read_csv(past_url)
            df_past_sheet = clean_column_names(df_past_sheet)
            past_rows_read = len(df_past_sheet)
            if 'Member ID' in df_past_sheet.columns:
                df_past_sheet['member_id'] = df_past_sheet['Member ID'].astype(str).str.strip()
                df_past_sheet['source_type'] = 'historical'
                dfs_to_concat.append(df_past_sheet)
            else:
                print("WARNING: 'Member ID' column not found in past members CSV.")
        except Exception as e:
            print(f"WARNING: Failed to download or process past members CSV: {e}")

    # 2. Expired current sheet
    df_expired_current = excluded_members_df.copy()
    if not df_expired_current.empty and 'member_id' in df_expired_current.columns:
        df_expired_current['source_type'] = 'expired_current'
        dfs_to_concat.append(df_expired_current)

    if not dfs_to_concat:
        print("WARNING: No past members data available. Creating empty past_members.json.")
    else:
        past_candidates_df = pd.concat(dfs_to_concat, ignore_index=True)
        past_candidates_df = past_candidates_df[
            past_candidates_df['member_id'].notna()
            & (past_candidates_df['member_id'] != "")
            & (past_candidates_df['member_id'].str.lower() != "nan")
        ].copy()

        past_unique_ids = past_candidates_df['member_id'].nunique()

        if "RC Membership Start Date" in past_candidates_df.columns:
            past_candidates_df["rc_start_dt"] = past_candidates_df["RC Membership Start Date"].apply(parse_member_date)
        else:
            past_candidates_df["rc_start_dt"] = pd.NaT

        if "RC Membership End Date" in past_candidates_df.columns:
            past_candidates_df["rc_end_dt"] = past_candidates_df["RC Membership End Date"].apply(parse_member_date)
        else:
            past_candidates_df["rc_end_dt"] = pd.NaT

        active_overlap = set(past_candidates_df['member_id']).intersection(active_member_ids)
        past_excluded_active = len(active_overlap)

        df_past_clean = past_candidates_df[~past_candidates_df['member_id'].isin(active_member_ids)].copy()

        for m_id, group in df_past_clean.groupby('member_id'):
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

            min_start = group['rc_start_dt'].min()
            max_end = group['rc_end_dt'].max()

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
            if 'expired_current' in sources and 'historical' not in sources:
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

        past_members.sort(key=lambda x: (x.get("full_name") or "").lower(), reverse=False)
        past_members.sort(key=lambda x: x.get("last_rc_end_date") or "0000-00-00", reverse=True)

    past_member_ids = {str(member.get("id", "")).strip() for member in past_members}
    overlap = active_member_ids.intersection(past_member_ids)
    if overlap:
        raise RuntimeError(
            f"Active members are duplicated in past_members.json: {sorted(overlap)}"
        )

    with open('data/past_members.json', 'w', encoding='utf-8') as f:
        json.dump(past_members, f, ensure_ascii=False, indent=2)

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
        "unmatched_photos": unmatched_photos,
        "past_members_total_rows_read": past_rows_read,
        "past_members_unique_ids": past_unique_ids,
        "past_members_from_historical_sheet": past_from_historical,
        "past_members_from_expired_current_sheet": past_from_expired,
        "past_members_excluded_because_active": past_excluded_active,
        "past_members_published": len(past_members),
        "active_past_overlap": len(overlap)
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
