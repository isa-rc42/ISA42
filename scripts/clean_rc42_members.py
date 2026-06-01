import json
import os
import re

def clean_name(name):
    if not name:
        return ""
    # Capitalize each word, handle hyphens
    parts = name.split()
    cleaned_parts = []
    for part in parts:
        if '-' in part:
            cleaned_parts.append('-'.join([p.capitalize() for p in part.split('-')]))
        else:
            cleaned_parts.append(part.capitalize())
    return " ".join(cleaned_parts)

def get_initials(name):
    if not name:
        return ""
    parts = [p for p in name.split() if p.isalpha()]
    if not parts:
        return name[:1].upper() if name else ""
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()

def clean_country(country_str):
    if not country_str:
        return "", ""
    country_str = country_str.strip()
    cob = ""
    if "Country of Birth:" in country_str:
        parts = country_str.split("Country of Birth:")
        c = parts[0].strip()
        cob = parts[1].strip()
        c = re.sub(r'(?i)\bcountry\s+of\s+birth\s*:?.*$', '', c).strip(" ,|")
        cob = cob.strip(" ,|")
        return c, cob
    
    c = re.sub(r'(?i)\bcountry\s+of\s+birth\s*:?.*$', '', country_str).strip(" ,|")
    return c, ""

def clean_affiliation(affil):
    if not affil:
        return ""
    affil = affil.strip()
    if affil.lower() in ["no affiliation", "no affiliation |", "none", "n/a", "-"]:
        return ""
    # Remove VAT and OIB strings case-insensitively
    affil = re.sub(r'(?i)\bvat\s*:\s*[A-Z0-9]+', '', affil)
    affil = re.sub(r'(?i)\boib\s*:\s*[A-Z0-9]+', '', affil)
    # Clean up multiple commas, pipes, and whitespace
    affil = re.sub(r'\s*,\s*,', ',', affil)
    affil = re.sub(r'\s*\|\s*\|', '|', affil)
    return affil.strip(" |,")

def clean_department(dept):
    if not dept:
        return ""
    dept = dept.strip()
    if re.search(r'(?i)\bno\s+department\b', dept) or dept.lower() in ["none", "n/a", "-", ""]:
        return ""
    
    # Sometimes it comes as "Germany | Sociology"
    parts = dept.split("|")
    if len(parts) > 1:
        dept = parts[-1].strip()
        
    return dept.strip(" |,")

def main():
    raw_path = os.path.join(os.path.dirname(__file__), '..', 'members', 'profiles', 'isa_rc42_members_raw.json')
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'rc42_members_clean.json')
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    cleaned_data = []
    
    for row in raw_data:
        member_of = row.get("member_of", "")
        if "RC42" not in member_of and "Social Psychology" not in member_of:
            continue
            
        raw_full_name = row.get("full_name", "").strip()
        full_name = clean_name(raw_full_name)
        initials = get_initials(full_name)
        
        country, cob = clean_country(row.get("country", ""))
        
        affiliation = clean_affiliation(row.get("institutional_affiliation", ""))
        department = clean_department(row.get("department", ""))
        
        email = row.get("email", "").strip()
        # Sometimes email might have markdown like [email](mailto:email) from copy-paste
        if "mailto:" in email:
            m = re.search(r'mailto:([^\)]+)', email)
            if m:
                email = m.group(1)
        email = email.strip()
        
        # Link cleaning
        def clean_link(l):
            if not l: return ""
            if isinstance(l, list):
                return l[0] if l else ""
            if "membership-search" in l:
                return ""
            return str(l).strip()
            
        website = clean_link(row.get("website_url"))
        linkedin = clean_link(row.get("linkedin_url"))
        orcid = clean_link(row.get("orcid_url"))
        researchgate = clean_link(row.get("researchgate_url"))
        twitter = clean_link(row.get("twitter_x_url"))
        
        # Avatar extraction
        raw_avatar = row.get("profile_image_url", "").strip()
        avatar_url = ""
        # Filter out placeholders like isa-member.jpg and empty domains
        if raw_avatar and "isa-member.jpg" not in raw_avatar and "blueSky" not in raw_avatar and len(raw_avatar) > 40:
            avatar_url = raw_avatar
        
        # ID generation
        base_id = re.sub(r'[^a-z0-9-]', '', full_name.lower().replace(' ', '-'))
        
        clean_member = {
            "id": base_id,
            "full_name": full_name,
            "raw_full_name": raw_full_name,
            "initials": initials,
            "country": country,
            "country_of_birth": cob,
            "institutional_affiliation": affiliation,
            "department": department,
            "member_of": member_of,
            "email_private": email,
            "show_email": False,
            "website_url": website,
            "linkedin_url": linkedin,
            "orcid_url": orcid,
            "researchgate_url": researchgate,
            "twitter_x_url": twitter,
            "avatar_url": avatar_url,
            "source_url": row.get("source_url", "")
        }
        cleaned_data.append(clean_member)
        
    # Deduplication
    unique_members = {}
    
    # Sort so that records with more data come later and overwrite sparse ones
    def score_record(r):
        score = 0
        if r['email_private']: score += 5
        if r['institutional_affiliation']: score += 2
        if r['department']: score += 1
        if r['website_url'] or r['linkedin_url'] or r['orcid_url']: score += 3
        return score
        
    cleaned_data.sort(key=score_record)
    
    for m in cleaned_data:
        email = m['email_private'].lower() if m['email_private'] else ""
        name_affil = f"{m['full_name']}_{m['institutional_affiliation']}".lower()
        name_country = f"{m['full_name']}_{m['country']}".lower()
        
        # Priority: Email, Name+Affiliation, Name+Country, Name
        key = None
        if email:
            key = f"email_{email}"
        elif m['full_name'] and m['institutional_affiliation']:
            key = f"affil_{name_affil}"
        elif m['full_name'] and m['country']:
            key = f"country_{name_country}"
        else:
            key = f"name_{m['full_name'].lower()}"
            
        unique_members[key] = m
        
    final_list = list(unique_members.values())
    
    # Sort alphabetically by full name
    final_list.sort(key=lambda x: x['full_name'])
    
    # Reassign IDs if duplicates
    seen_ids = set()
    for m in final_list:
        base_id = m['id']
        if not base_id:
            base_id = "member"
        new_id = base_id
        counter = 1
        while new_id in seen_ids:
            new_id = f"{base_id}-{counter}"
            counter += 1
        seen_ids.add(new_id)
        m['id'] = new_id
        
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
        
    js_out_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'js', 'members-data.js')
    os.makedirs(os.path.dirname(js_out_path), exist_ok=True)
    with open(js_out_path, 'w', encoding='utf-8') as f:
        f.write(f"window.RC42_MEMBERS_DATA = {json.dumps(final_list, ensure_ascii=False)};")
        
    print(f"Processed {len(raw_data)} raw records.")
    print(f"Generated {len(final_list)} clean, deduplicated records.")
    
    countries = set(m['country'] for m in final_list if m['country'])
    print(f"Found {len(countries)} unique countries.")

if __name__ == "__main__":
    main()
