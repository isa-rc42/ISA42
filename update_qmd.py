import os

def read_file(filepath):
    if not os.path.exists(filepath):
        return ""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# 1. Update SCSS
scss_content = read_file('styles.scss')

# Add new styles at the end, before the media queries
new_scss = """
/* News Header Action */
.news-action-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: -1rem;
  margin-bottom: 1.25rem;
}

.news-header-action {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.42rem 0.8rem;
  border-radius: 999px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #173b7a;
  font-size: 0.78rem;
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
  transition: border-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.news-header-action:hover {
  border-color: #0d9488;
  color: #0d9488;
  transform: translateY(-1px);
}

/* Community Filter Bar Sort Updates */
.community-filter-bar {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
  margin: 1rem 0 1.25rem;
  padding: 0.85rem 1rem;
  border: 1px solid #e5eaf0;
  border-radius: 0.85rem;
  background: #f8fafc;
}

.community-filter-bar .filter-controls {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.community-filter-bar .filter-label,
.community-filter-bar .sort-label {
  flex: 0 0 auto;
  font-size: 0.82rem;
  font-weight: 700;
  color: #0b1628;
  margin: 0;
}

.community-filter-bar .form-select,
.community-filter-bar select {
  display: inline-block;
  width: auto;
  min-width: 150px;
  max-width: 190px;
  flex: 0 0 auto;
  font-size: 0.78rem;
  margin: 0;
}

#sort-mode {
  min-width: 170px;
}
"""

mobile_scss = """
  .news-action-bar {
    justify-content: flex-start;
    margin-top: 0;
  }

  .community-filter-bar {
    align-items: flex-start;
  }

  .community-filter-bar .filter-controls {
    width: 100%;
  }

  .community-filter-bar .form-select,
  .community-filter-bar select {
    min-width: 100%;
    max-width: 100%;
  }
"""

if '.news-header-action' not in scss_content:
    # We will remove old .community-filter-bar styles if they exist
    import re
    scss_content = re.sub(r'\.community-filter-bar \{.*?\n\}\n*', '', scss_content, flags=re.DOTALL)
    scss_content = re.sub(r'\.filter-controls \{.*?\n\}\n*', '', scss_content, flags=re.DOTALL)
    
    # wait, new_css is not defined here, using new_scss
    scss_content = scss_content.replace('@media (max-width: 900px) {', new_scss + '\n@media (max-width: 900px) {')
    
    # insert mobile styles
    scss_content = scss_content.replace('  .contribution-summary {', mobile_scss + '\n  .contribution-summary {')
    
    write_file('styles.scss', scss_content)
    print("Updated styles.scss")


# 2. Update qmd files
js_sort_functions = """
  function parseDate(value) {
    if (!value) return null;
    const date = new Date(value);
    return isNaN(date.getTime()) ? null : date;
  }

  function getDeadline(item) {
    return item.relevant_date || item.deadline || "";
  }

  function sortData(data) {
    const sortMode = document.getElementById('sort-mode');
    const mode = sortMode ? sortMode.value : "date_desc";
    const sorted = [...data];

    if (mode === "deadline_asc") {
      sorted.sort((a, b) => {
        const da = parseDate(getDeadline(a));
        const db = parseDate(getDeadline(b));

        if (da && db) return da - db;
        if (da && !db) return -1;
        if (!da && db) return 1;

        const pa = parseDate(a.date_published);
        const pb = parseDate(b.date_published);
        if (pa && pb) return pb - pa;
        return 0;
      });
    } else {
      sorted.sort((a, b) => {
        const da = parseDate(a.date_published);
        const db = parseDate(b.date_published);

        if (da && db) return db - da;
        if (da && !db) return -1;
        if (!da && db) return 1;
        return 0;
      });
    }

    return sorted;
  }
"""

def process_qmd(filepath):
    content = read_file(filepath)
    if not content: return

    # Add Action Bar and modify Filter Bar HTML
    old_html_block = """```{=html}
<div class="community-filter-bar">
  <span class="filter-label">Filter by:</span>
  
  <div class="filter-controls">
    <select id="typeFilter" class="form-select form-select-sm" aria-label="Filter by Type">
      <option value="all">All Types</option>
      <option value="news">News</option>
      <option value="event">Event</option>
      <option value="call">Opportunity/Call</option>
      <option value="publication">Publication</option>
      <option value="resource">Resource</option>
    </select>
    
    <select id="categoryFilter" class="form-select form-select-sm" aria-label="Filter by Category">
      <option value="all">All Categories</option>
    </select>
    
    <select id="languageFilter" class="form-select form-select-sm" aria-label="Filter by Language">
      <option value="all">All Languages</option>
    </select>
  </div>
</div>
```"""

    new_html_block = """::: {.news-action-bar}
[Submit a contribution &rarr;](../contact/index.qmd#community-contributions){.news-header-action}
:::

```{=html}
<div class="community-filter-bar">
  <span class="filter-label">Filter by:</span>
  
  <div class="filter-controls">
    <select id="typeFilter" class="form-select form-select-sm" aria-label="Filter by Type">
      <option value="all">All Types</option>
      <option value="news">News</option>
      <option value="event">Event</option>
      <option value="call">Opportunity/Call</option>
      <option value="publication">Publication</option>
      <option value="resource">Resource</option>
    </select>
    
    <select id="categoryFilter" class="form-select form-select-sm" aria-label="Filter by Category">
      <option value="all">All Categories</option>
    </select>
    
    <select id="languageFilter" class="form-select form-select-sm" aria-label="Filter by Language">
      <option value="all">All Languages</option>
    </select>

    <span class="sort-label">Sort by:</span>

    <select id="sort-mode" class="form-select form-select-sm" aria-label="Sort by">
      <option value="date_desc">Contribution date</option>
      <option value="deadline_asc">Deadline</option>
    </select>
  </div>
</div>
```"""
    
    if 'sort-mode' not in content:
        content = content.replace(old_html_block, new_html_block)

    # Insert sort functions
    if 'function sortData' not in content:
        content = content.replace('function populateFilters(data) {', js_sort_functions + '\n  function populateFilters(data) {')

    # Update event listeners
    if "const sortMode = document.getElementById('sort-mode');" not in content:
        content = content.replace(
            "const languageFilter = document.getElementById('languageFilter');",
            "const languageFilter = document.getElementById('languageFilter');\n  const sortMode = document.getElementById('sort-mode');"
        )
        content = content.replace(
            "languageFilter.addEventListener('change', () => renderCards(allData));",
            "languageFilter.addEventListener('change', () => renderCards(allData));\n    if (sortMode) sortMode.addEventListener('change', () => renderCards(allData));"
        )

    # Update renderCards to use sortData
    if "let filtered = sortData(data.filter(item => {" not in content:
        content = content.replace(
            "const filtered = data.filter(item => {",
            "let filtered = sortData(data.filter(item => {"
        )
        content = content.replace(
            "return tMatch && cMatch && lMatch;\n    });",
            "return tMatch && cMatch && lMatch;\n    }));"
        )
        # also we need to update the allData sort logic on load to use sortData
        # but allData is currently sorted by `allData.sort((a, b) => new Date(b.date_published) - new Date(a.date_published));`
        # we can just let renderCards sort it again, or we can just leave it as is because renderCards now sorts anyway.

    write_file(filepath, content)
    print(f"Updated {filepath}")

process_qmd('news/index.qmd')
process_qmd('news/community-contributions.qmd')
