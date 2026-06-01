document.addEventListener("DOMContentLoaded", () => {
  const tabsContainer = document.getElementById("resources-tabs");
  const contentContainer = document.getElementById("resources-content");
  const searchInput = document.getElementById("resource-search");

  // Define categories and their order
  const categories = [
    {
      id: "publications",
      name: "Publications",
      desc: "Recent books, special journal issues, journals, and significant articles relevant to sociological social psychology."
    },
    {
      id: "teaching-resources",
      name: "Teaching Resources",
      desc: "Syllabi, course outlines, assignments, and pedagogical materials for teaching social psychology."
    },
    {
      id: "datasets-tools",
      name: "Datasets & Tools",
      desc: "Open datasets, methodological tools, and resources useful for comparative sociological research."
    },
    {
      id: "blog-posts",
      name: "Blog / Posts",
      desc: "Short essays, reflections, calls, field notes, and member contributions."
    }
  ];

  let resourcesData = [];

  // Fetch and parse the CSV
  Papa.parse("rc42_resources_workflow.csv", {
    download: true,
    header: true,
    skipEmptyLines: true,
    complete: function(results) {
      resourcesData = results.data;
      initResources();
    },
    error: function(err) {
      console.error("Error fetching or parsing CSV:", err);
      if (contentContainer) {
          contentContainer.innerHTML = "<p>Error loading resources. Please try again later.</p>";
      }
    }
  });

  function initResources() {
    renderTabs();
    renderSections(resourcesData);
    
    if (searchInput) {
      searchInput.addEventListener("input", handleSearch);
    }
  }

  function handleSearch() {
    const query = searchInput.value.toLowerCase();
    
    if (!query) {
      renderSections(resourcesData);
      return;
    }
    
    const filtered = resourcesData.filter(r => {
      const matchText = [
        r.Title,
        r["Author / Institution"],
        r.Description,
        r.Tags,
        r.Category,
        r["Suggested placement"]
      ].join(" ").toLowerCase();
      
      return matchText.includes(query);
    });
    
    renderSections(filtered);
  }

  function renderTabs() {
    if (!tabsContainer) return;
    tabsContainer.innerHTML = "";
    
    categories.forEach(cat => {
      // Find count for this category
      const count = resourcesData.filter(r => matchesCategory(r, cat.name)).length;
      
      const a = document.createElement("a");
      a.href = `#${cat.id}`;
      a.className = "resource-tab";
      
      a.innerHTML = `
        <div class="tab-title">${cat.name}</div>
        <div class="tab-desc">${cat.desc}</div>
        <div class="tab-count">${count} resources</div>
      `;
      
      // Smooth scroll
      a.addEventListener("click", (e) => {
        const target = document.getElementById(cat.id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: "smooth" });
        }
      });
      
      tabsContainer.appendChild(a);
    });
  }

  function matchesCategory(resource, categoryName) {
    // Check "Suggested placement" first, then "Category"
    const placement = (resource["Suggested placement"] || "").trim();
    if (placement && placement === categoryName) return true;
    
    const cat = (resource["Category"] || "").trim();
    if (!placement && cat === categoryName) return true;
    
    return false;
  }

  function renderSections(data) {
    if (!contentContainer) return;
    contentContainer.innerHTML = "";

    if (data.length === 0) {
      contentContainer.innerHTML = "<div class='placeholder-notice' style='grid-column: 1/-1;'>No resources found matching your search.</div>";
      return;
    }

    const fragment = document.createDocumentFragment();

    categories.forEach(cat => {
      let items = data.filter(r => matchesCategory(r, cat.name));
      
      if (items.length === 0) return; // Skip empty categories
      
      // Sort items: Priority rank (1 is highest, 0/empty goes last), then alphabetical by Title
      items.sort((a, b) => {
        let rankA = parseInt(a["Priority rank"], 10);
        let rankB = parseInt(b["Priority rank"], 10);
        
        // Handle NaN, 0, or empty as lowest priority (e.g. assign a very high number)
        rankA = (isNaN(rankA) || rankA === 0) ? 999999 : rankA;
        rankB = (isNaN(rankB) || rankB === 0) ? 999999 : rankB;
        
        if (rankA !== rankB) {
          return rankA - rankB;
        }
        
        // Alphabetical fallback
        const titleA = (a.Title || "").toLowerCase();
        const titleB = (b.Title || "").toLowerCase();
        return titleA.localeCompare(titleB);
      });

      const section = document.createElement("div");
      section.className = "resources-section";
      section.id = cat.id;

      const header = document.createElement("div");
      header.className = "section-header";
      header.innerHTML = `
        <h2>${cat.name}</h2>
        <p>${cat.desc}</p>
      `;
      section.appendChild(header);

      const grid = document.createElement("div");
      grid.className = "resources-category-grid";

      items.forEach(r => {
        const card = createResourceCard(r);
        grid.appendChild(card);
      });

      section.appendChild(grid);
      fragment.appendChild(section);
    });

    contentContainer.appendChild(fragment);
  }

  function createResourceCard(r) {
    const card = document.createElement("div");
    card.className = "resource-card";

    // Badges
    const badgesHtml = [];
    if (r["Resource type"]) {
      badgesHtml.push(`<span class="resource-badge badge-type">${r["Resource type"]}</span>`);
    }
    if (r["Verification status"] && r["Verification status"].toLowerCase().includes("verified")) {
      badgesHtml.push(`<span class="resource-badge badge-verified">Verified</span>`);
    }
    if (r["Access type"]) {
      badgesHtml.push(`<span class="resource-badge badge-access">${r["Access type"]}</span>`);
    }
    if (r["Language"]) {
      badgesHtml.push(`<span class="resource-badge">${r["Language"]}</span>`);
    }
    if (r["Region scope"]) {
      badgesHtml.push(`<span class="resource-badge">${r["Region scope"]}</span>`);
    }
    if (r["Source type"] && r["Source type"] !== "External") {
       badgesHtml.push(`<span class="resource-badge">${r["Source type"]}</span>`);
    }

    let badgesContainer = "";
    if (badgesHtml.length > 0) {
      badgesContainer = `<div class="resource-badges">${badgesHtml.join("")}</div>`;
    }

    // Tags
    let tagsContainer = "";
    if (r.Tags) {
      const tags = r.Tags.split(";").map(t => t.trim()).filter(Boolean);
      if (tags.length > 0) {
        const tagsHtml = tags.map(t => `<span class="resource-tag">${t}</span>`).join("");
        tagsContainer = `<div class="resource-tags">${tagsHtml}</div>`;
      }
    }

    // Author
    let authorHtml = "";
    if (r["Author / Institution"]) {
      authorHtml = `<div class="resource-author">${r["Author / Institution"]}</div>`;
    }

    card.innerHTML = `
      ${badgesContainer}
      <h3 class="resource-title">${r.Title || "Untitled"}</h3>
      ${authorHtml}
      <div class="resource-desc">${r.Description || ""}</div>
      ${tagsContainer}
      <div class="resource-footer">
        <div class="resource-meta-small">
        </div>
        ${r.URL ? `<a href="${r.URL}" target="_blank" rel="noopener noreferrer" class="resource-link">Open resource</a>` : ''}
      </div>
    `;

    return card;
  }
});
