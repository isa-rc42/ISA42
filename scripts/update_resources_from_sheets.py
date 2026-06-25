import os
import sys
import json
import yaml
import shutil
import pandas as pd
from datetime import datetime

DEFAULT_RESOURCES_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRw78IC9rg3BeTVqIJHvGbr5p5f1cSkPpv6uCLo3gJVxGQSlk6dDZfZP-GeD-2S63sH5FYHxuwGNiYF/pub?output=csv"

def clean_column_names(df):
    """Strip whitespace from column names."""
    df.columns = df.columns.str.strip()
    return df

def clean_str(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    if s in {"nan", "NaN", "None", "-"}:
        return ""
    return s

def parse_tags(val):
    s = clean_str(val)
    if not s:
        return []
    # replace semicolon with comma
    s = s.replace(";", ",")
    tags = [t.strip().lower() for t in s.split(",") if t.strip()]
    return list(dict.fromkeys(tags)) # remove duplicates keeping order

def main():
    resources_url = os.environ.get("RESOURCES_CSV_URL", DEFAULT_RESOURCES_URL)
    
    total_rows = 0
    excluded_missing_title = 0
    excluded_missing_url = 0
    excluded_unverified = 0
    published_resources = []
    categories_set = set()

    try:
        print(f"Downloading resources list from {resources_url}...")
        df = pd.read_csv(resources_url)
        df = clean_column_names(df)
        total_rows = len(df)
    except Exception as e:
        print(f"WARNING: Failed to download or parse resources CSV: {e}")
        df = pd.DataFrame()

    if not df.empty:
        for idx, row in df.iterrows():
            title = clean_str(row.get("Title"))
            url = clean_str(row.get("URL"))
            status = clean_str(row.get("Verification status"))

            if not title:
                excluded_missing_title += 1
                continue

            if not url or url == "#":
                excluded_missing_url += 1
                continue

            if not status.lower().startswith("verified"):
                excluded_unverified += 1
                continue

            r_id = clean_str(row.get("ID")) or f"RC42-R{idx+1:03d}"
            category = clean_str(row.get("Category")) or "General"
            author_inst = clean_str(row.get("Author / Institution"))
            res_type = clean_str(row.get("Resource type"))
            desc = clean_str(row.get("Description"))
            relevance = clean_str(row.get("Relevance for RC42"))
            suggested_placement = clean_str(row.get("Suggested placement"))
            access_type = clean_str(row.get("Access type"))
            language = clean_str(row.get("Language")) or "English"
            region_scope = clean_str(row.get("Region scope"))
            source_type = clean_str(row.get("Source type")) or "External"

            try:
                p_rank = int(float(str(row.get("Priority rank", 0)).strip() or 0))
            except (ValueError, TypeError):
                p_rank = 0

            tags = parse_tags(row.get("Tags"))

            categories_set.add(category)
            if suggested_placement:
                categories_set.add(suggested_placement)

            published_resources.append({
                "id": r_id,
                "category": category,
                "title": title,
                "author_institution": author_inst,
                "resource_type": res_type,
                "description": desc,
                "relevance_for_rc42": relevance,
                "suggested_placement": suggested_placement,
                "url": url,
                "tags": tags,
                "access_type": access_type,
                "language": language,
                "region_scope": region_scope,
                "verification_status": status,
                "priority_rank": p_rank,
                "source_type": source_type
            })

        # Sort resources
        def sort_key(x):
            pr = x["priority_rank"]
            rank_val = pr if pr > 0 else 999999
            cat_val = (x["suggested_placement"] or x["category"]).lower()
            title_val = x["title"].lower()
            return (rank_val, cat_val, title_val)

        published_resources.sort(key=sort_key)

    # --- Community Resources Processing ---
    community_resources = []
    submissions_json_path = "data/community_submissions.json"
    submissions_yml_path = "data/community_submissions.yml"
    
    sub_data = []
    if os.path.exists(submissions_json_path):
        try:
            with open(submissions_json_path, "r", encoding="utf-8") as f:
                sub_data = json.load(f) or []
        except Exception as e:
            print(f"WARNING: Failed to read community submissions JSON: {e}")
    elif os.path.exists(submissions_yml_path):
        try:
            with open(submissions_yml_path, "r", encoding="utf-8") as f:
                sub_data = yaml.safe_load(f) or []
        except Exception as e:
            print(f"WARNING: Failed to read community submissions YML: {e}")

    if isinstance(sub_data, list):
        for item in sub_data:
            if not isinstance(item, dict):
                continue
            
            s_type = clean_str(item.get("type") or item.get("submission_type")).lower()
            s_cat = clean_str(item.get("category")).lower()
            s_placement = clean_str(item.get("suggested_placement") or item.get("Suggested placement")).lower()
            
            raw_tags = item.get("tags") or []
            if isinstance(raw_tags, str):
                tag_list = parse_tags(raw_tags)
            elif isinstance(raw_tags, list):
                tag_list = [clean_str(t).lower() for t in raw_tags if clean_str(t)]
            else:
                tag_list = []

            is_resource = (
                "resource" in s_type
                or "resource" in s_cat
                or any(t in {"resource", "resources", "teaching"} for t in tag_list)
                or "resource" in s_placement
            )

            if is_resource:
                c_id = clean_str(item.get("id")) or "sub-resource"
                c_title = clean_str(item.get("title"))
                c_desc = clean_str(item.get("description"))
                c_url = clean_str(item.get("url"))
                c_org = clean_str(item.get("organization") or item.get("author"))
                c_lang = clean_str(item.get("language"))
                c_terr = clean_str(item.get("territory") or item.get("region"))
                c_date = clean_str(item.get("date_published") or item.get("relevant_date"))

                if not c_title or not c_url:
                    continue

                if "resource" not in tag_list and "resources" not in tag_list:
                    tag_list.insert(0, "resource")

                community_resources.append({
                    "id": c_id,
                    "title": c_title,
                    "description": c_desc,
                    "url": c_url,
                    "organization": c_org,
                    "language": c_lang,
                    "territory": c_terr,
                    "date_published": c_date,
                    "tags": list(dict.fromkeys(tag_list)),
                    "source": "Community contribution"
                })

        community_resources.sort(key=lambda x: x.get("date_published") or "0000-00-00", reverse=True)

    # --- Write Outputs ---
    os.makedirs("data", exist_ok=True)
    os.makedirs("docs/data", exist_ok=True)

    with open("data/resources.json", "w", encoding="utf-8") as f:
        json.dump(published_resources, f, ensure_ascii=False, indent=2)

    with open("data/community_resources.json", "w", encoding="utf-8") as f:
        json.dump(community_resources, f, ensure_ascii=False, indent=2)

    diagnostics = {
        "last_updated": datetime.now().isoformat(),
        "total_rows_read": total_rows,
        "published_resources": len(published_resources),
        "excluded_missing_title": excluded_missing_title,
        "excluded_missing_url": excluded_missing_url,
        "excluded_unverified": excluded_unverified,
        "categories": len(categories_set),
        "community_resources_detected": len(community_resources)
    }

    with open("data/resources_diagnostics.json", "w", encoding="utf-8") as f:
        json.dump(diagnostics, f, ensure_ascii=False, indent=2)

    # Copy to docs/data/
    shutil.copy("data/resources.json", "docs/data/resources.json")
    shutil.copy("data/community_resources.json", "docs/data/community_resources.json")
    shutil.copy("data/resources_diagnostics.json", "docs/data/resources_diagnostics.json")

    print(f"Successfully updated resources. Published {len(published_resources)} core resources and {len(community_resources)} community resources.")

if __name__ == "__main__":
    main()
