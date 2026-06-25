/**
 * Dynamic Resources Directory Frontend
 * Loads data/resources.json and data/community_resources.json
 */

document.addEventListener("DOMContentLoaded", async () => {
  const coreContainer = document.getElementById("core-resources-container");
  const communityContainer = document.getElementById("community-resources-container");
  const metricsContainer = document.getElementById("overview-metrics-container");
  const tocList = document.getElementById("resources-toc-list");
  const searchInput = document.getElementById("resources-search");
  const catFilterContainer = document.getElementById("category-filter-container");

  if (!coreContainer) return;

  const escapeHtml = (str) => {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  };

  let coreResources = [];
  let communityResources = [];
  let activeCategory = "all";
  let searchQuery = "";

  // 1. Fetch Core Resources
  try {
    const res = await fetch("../data/resources.json");
    if (res.ok) {
      coreResources = await res.json();
    } else {
      console.error("Failed to load resources.json:", res.status);
    }
  } catch (err) {
    console.error("Error loading resources.json:", err);
  }

  // 2. Fetch Community Resources (non-blocking failure)
  try {
    const resComm = await fetch("../data/community_resources.json");
    if (resComm.ok) {
      communityResources = await resComm.json();
    } else {
      console.warn("Failed to load community_resources.json:", resComm.status);
    }
  } catch (err) {
    console.warn("Warning: Error loading community_resources.json:", err);
  }

  if (coreResources.length === 0 && communityResources.length === 0) {
    coreContainer.innerHTML = `<div style="text-align: center; color: #64748b; padding: 3rem;">Resources are currently unavailable. Please check back later.</div>`;
    return;
  }

  // 3. Define Category Metadata
  const categoryMeta = {
    "Publications": { id: "publications", desc: "Recent books, special journal issues, journals, and significant articles relevant to sociological social psychology." },
    "Teaching Resources": { id: "teaching-resources", desc: "Syllabi, course outlines, assignments, and pedagogical materials for teaching social psychology." },
    "Datasets & Tools": { id: "datasets-tools", desc: "Open datasets, methodological tools, and software useful for comparative sociological research." },
    "Blog / Posts": { id: "blog-posts", desc: "Short essays, reflections, calls, field notes, and member contributions." }
  };

  // Extract all categories present
  const allCategories = [...new Set(coreResources.map(r => r.suggested_placement || r.category || "General"))];
  allCategories.forEach(cat => {
    if (!categoryMeta[cat]) {
      const idStr = cat.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "");
      categoryMeta[cat] = { id: idStr, desc: `Resources and materials categorized under ${cat}.` };
    }
  });

  // 4. Render Metrics
  const totalRes = coreResources.length;
  const pubsCount = coreResources.filter(r => (r.suggested_placement || r.category) === "Publications").length;
  const teachCount = coreResources.filter(r => (r.suggested_placement || r.category) === "Teaching Resources").length;
  const dataCount = coreResources.filter(r => (r.suggested_placement || r.category) === "Datasets & Tools").length;

  if (metricsContainer) {
    metricsContainer.innerHTML = `
      <div id="overview" class="resources-section" style="margin-bottom: 2rem;">
        <div class="resources-metrics">
          <div class="metric-item"><span class="metric-value">${totalRes}</span><span class="metric-label">Total Resources</span></div>
          <div class="metric-item"><span class="metric-value">${pubsCount}</span><span class="metric-label">Publications</span></div>
          <div class="metric-item"><span class="metric-value">${teachCount}</span><span class="metric-label">Teaching</span></div>
          <div class="metric-item"><span class="metric-value">${dataCount}</span><span class="metric-label">Datasets</span></div>
          <div class="metric-item"><span class="metric-value">${communityResources.length}</span><span class="metric-label">Community Shared</span></div>
        </div>
      </div>
    `;
  }

  // 5. Render Category Filter Chips
  if (catFilterContainer) {
    let chipsHtml = `<button type="button" class="cat-chip active" data-cat="all" style="padding: 0.35rem 0.85rem; border-radius: 20px; border: 1px solid #0d9488; background: #0d9488; color: white; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.2s;">All Categories (${totalRes})</button>`;
    allCategories.forEach(cat => {
      const cnt = coreResources.filter(r => (r.suggested_placement || r.category) === cat).length;
      chipsHtml += `<button type="button" class="cat-chip" data-cat="${escapeHtml(cat)}" style="padding: 0.35rem 0.85rem; border-radius: 20px; border: 1px solid #cbd5e1; background: #f8fafc; color: #475569; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.2s;">${escapeHtml(cat)} (${cnt})</button>`;
    });
    catFilterContainer.innerHTML = chipsHtml;

    catFilterContainer.querySelectorAll(".cat-chip").forEach(btn => {
      btn.addEventListener("click", (e) => {
        catFilterContainer.querySelectorAll(".cat-chip").forEach(c => {
          c.style.background = "#f8fafc";
          c.style.color = "#475569";
          c.style.borderColor = "#cbd5e1";
          c.classList.remove("active");
        });
        btn.style.background = "#0d9488";
        btn.style.color = "white";
        btn.style.borderColor = "#0d9488";
        btn.classList.add("active");
        activeCategory = btn.getAttribute("data-cat");
        renderCore();
      });
    });
  }

  // 6. Render TOC Sidebar
  const renderToc = () => {
    if (!tocList) return;
    let tocHtml = `<li class="toc-section-item is-active" data-target="overview"><a href="#overview" class="toc-link"><span>Overview</span> <span class="toc-count">${totalRes}</span></a></li>`;
    
    allCategories.forEach(cat => {
      const meta = categoryMeta[cat] || { id: "cat" };
      const items = coreResources.filter(r => (r.suggested_placement || r.category) === cat);
      if (items.length === 0) return;

      let previewHtml = `<ul class="toc-preview" hidden>`;
      items.slice(0, 3).forEach(item => {
        let st = item.title || "Untitled";
        if (st.length > 38) st = st.substring(0, 35) + "...";
        previewHtml += `<li><a href="#res-${item.id}">${escapeHtml(st)}</a></li>`;
      });
      previewHtml += `</ul>`;

      tocHtml += `
        <li class="toc-section-item" data-target="${meta.id}">
          <a href="#${meta.id}" class="toc-link"><span>${escapeHtml(cat)}</span> <span class="toc-count">${items.length}</span></a>
          ${previewHtml}
        </li>
      `;
    });

    tocHtml += `<li class="toc-section-item" data-target="community-resources-section"><a href="#community-resources-section" class="toc-link"><span>Community</span> <span class="toc-count">${communityResources.length}</span></a></li>`;
    tocList.innerHTML = tocHtml;
  };
  renderToc();

  // 7. Render Core Resources
  const renderCore = () => {
    let html = "";
    
    allCategories.forEach(cat => {
      if (activeCategory !== "all" && activeCategory !== cat) return;

      const meta = categoryMeta[cat] || { id: "general", desc: "" };
      let items = coreResources.filter(r => (r.suggested_placement || r.category) === cat);

      if (searchQuery !== "") {
        items = items.filter(r => {
          const sText = (r.title + " " + (r.author_institution || "") + " " + (r.description || "") + " " + (r.tags || []).join(" ") + " " + (r.resource_type || "")).toLowerCase();
          return sText.includes(searchQuery);
        });
      }

      if (items.length === 0) return;

      let itemsHtml = "";
      items.forEach(r => {
        const titleEsc = escapeHtml(r.title || "Untitled");
        const urlEsc = escapeHtml(r.url || "#");
        const author = escapeHtml(r.author_institution || "");
        const type = escapeHtml(r.resource_type || "");
        const desc = escapeHtml(r.description || "");

        // Author & Type line
        let authTypeLine = "";
        if (author && type) {
          authTypeLine = `<div class="resource-author-type">${author} <span class="type-dot">&middot;</span> ${type}</div>`;
        } else if (author || type) {
          authTypeLine = `<div class="resource-author-type">${author || type}</div>`;
        }

        // Meta badges
        let metaParts = [];
        if (r.language) metaParts.push(`Language: ${escapeHtml(r.language)}`);
        if (r.access_type) metaParts.push(`Access: ${escapeHtml(r.access_type)}`);
        if (r.region_scope) metaParts.push(`Region: ${escapeHtml(r.region_scope)}`);
        if (r.verification_status && r.verification_status.toLowerCase().includes("verified")) {
          metaParts.push(`<span class="resource-badge badge-verified">Verified</span>`);
        }

        let metaHtml = metaParts.length > 0 ? `<div class="resource-meta">${metaParts.join(' <span style="color:#cbd5e1;">&middot;</span> ')}</div>` : "";

        // Tags
        let tagsHtml = "";
        if (r.tags && r.tags.length > 0) {
          tagsHtml = `<div class="resource-tags">${r.tags.map(t => `<span class="resource-chip">${escapeHtml(t)}</span>`).join(" ")}</div>`;
        }

        itemsHtml += `
          <article class="resource-item" id="res-${r.id}">
            <div class="resource-main-content">
              <a href="${urlEsc}" target="_blank" rel="noopener noreferrer" class="resource-title">${titleEsc}</a>
              ${authTypeLine}
              ${desc ? `<div class="resource-description">${desc}</div>` : ""}
              ${metaHtml}
              ${tagsHtml}
            </div>
            <div class="resource-action">
              ${urlEsc !== "#" ? `<a href="${urlEsc}" target="_blank" rel="noopener noreferrer" class="resource-link-btn">Open resource &rarr;</a>` : ""}
            </div>
          </article>
        `;
      });

      html += `
        <section class="resources-section" id="${meta.id}" data-resource-section="${meta.id}">
          <h2>${escapeHtml(cat)}</h2>
          <p>${escapeHtml(meta.desc)}</p>
          <div class="resource-directory">
            ${itemsHtml}
          </div>
        </section>
      `;
    });

    if (html === "") {
      coreContainer.innerHTML = `<div style="padding: 2rem; text-align: center; color: #64748b;">No matching resources found.</div>`;
    } else {
      coreContainer.innerHTML = html;
    }
  };

  // 8. Render Community Resources
  const renderCommunity = () => {
    if (!communityContainer) return;
    
    let items = communityResources;
    if (searchQuery !== "") {
      items = items.filter(r => {
        const sText = (r.title + " " + (r.organization || "") + " " + (r.description || "") + " " + (r.tags || []).join(" ")).toLowerCase();
        return sText.includes(searchQuery);
      });
    }

    if (items.length === 0) {
      communityContainer.innerHTML = `<div style="padding: 1.5rem 0; color: #64748b; font-style: italic;">No community resources have been published yet.</div>`;
      return;
    }

    let html = "";
    items.forEach(r => {
      const titleEsc = escapeHtml(r.title || "Untitled");
      const urlEsc = escapeHtml(r.url || "#");
      const org = escapeHtml(r.organization || "");
      const desc = escapeHtml(r.description || "");
      const dateStr = escapeHtml(r.date_published || "");

      let metaParts = [];
      if (dateStr) metaParts.push(`Published: ${dateStr}`);
      if (r.language) metaParts.push(`Language: ${escapeHtml(r.language)}`);
      if (r.territory) metaParts.push(`Scope: ${escapeHtml(r.territory)}`);

      let metaHtml = metaParts.length > 0 ? `<div class="resource-meta">${metaParts.join(' <span style="color:#cbd5e1;">&middot;</span> ')}</div>` : "";

      let tagsHtml = "";
      if (r.tags && r.tags.length > 0) {
        tagsHtml = `<div class="resource-tags">${r.tags.map(t => `<span class="resource-chip" style="background:#eef6f6; border-color:#b2dfdb; color:#00695c;">${escapeHtml(t)}</span>`).join(" ")}</div>`;
      }

      html += `
        <article class="resource-item" id="comm-${r.id}">
          <div class="resource-main-content">
            <a href="${urlEsc}" target="_blank" rel="noopener noreferrer" class="resource-title">${titleEsc}</a>
            ${org ? `<div class="resource-author-type">${org}</div>` : ""}
            ${desc ? `<div class="resource-description">${desc}</div>` : ""}
            ${metaHtml}
            ${tagsHtml}
          </div>
          <div class="resource-action">
            ${urlEsc !== "#" ? `<a href="${urlEsc}" target="_blank" rel="noopener noreferrer" class="resource-link-btn">Open resource &rarr;</a>` : ""}
          </div>
        </article>
      `;
    });

    communityContainer.innerHTML = html;
  };

  // 9. Attach Search Event Listener
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      renderCore();
      renderCommunity();
    });
  }

  // Initial Render
  renderCore();
  renderCommunity();

  // 10. Scroll Observer for TOC Highlighting
  const tocObserver = new IntersectionObserver((entries) => {
    const visible = entries.filter(e => e.isIntersecting);
    if (visible.length > 0) {
      const topSection = visible.sort((a,b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      const targetId = topSection.target.id;
      
      document.querySelectorAll(".toc-section-item").forEach(li => {
        const active = li.getAttribute("data-target") === targetId;
        li.classList.toggle("is-active", active);
        const prev = li.querySelector(".toc-preview");
        if (prev) prev.hidden = !active;
      });
    }
  }, { rootMargin: "-100px 0px -60% 0px" });

  document.querySelectorAll("section.resources-section, div#overview").forEach(sec => tocObserver.observe(sec));
});
