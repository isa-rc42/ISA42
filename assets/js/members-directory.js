document.addEventListener("DOMContentLoaded", () => {
  const membersGrid = document.getElementById("members-grid");
  const searchInput = document.getElementById("member-search");
  const countryFilter = document.getElementById("country-filter");
  const linkFilter = document.getElementById("link-filter");
  const clearBtn = document.getElementById("clear-filters");
  const noResultsMsg = document.getElementById("no-results");
  const resultsCount = document.getElementById("results-count");
  const totalCountSpan = document.getElementById("total-count");

  const statTotal = document.getElementById("stat-total");
  const statCountries = document.getElementById("stat-countries");
  const statInstitutions = document.getElementById("stat-institutions");
  const statUpdated = document.getElementById("stat-updated");

  let membersData = [];

  fetch("../data/members.json")
    .then(response => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.json();
    })
    .then(data => {
      membersData = data;
      if (membersData.length > 0) {
        initDirectory();
      } else {
        membersGrid.innerHTML = "<p>No active members found.</p>";
      }
    })
    .catch(err => {
      console.error("Error fetching members data:", err);
      membersGrid.innerHTML = "<p>Error loading directory data. Please try again later.</p>";
    });

  function initDirectory() {
    populateFilters();
    updateMetrics();
    renderMembers(membersData);

    searchInput.addEventListener("input", handleFilter);
    countryFilter.addEventListener("change", handleFilter);
    linkFilter.addEventListener("change", handleFilter);
    clearBtn.addEventListener("click", clearFilters);
  }

  function populateFilters() {
    const countries = new Set();
    membersData.forEach((m) => {
      if (m.country) countries.add(m.country);
    });

    const sortedCountries = Array.from(countries).sort();
    sortedCountries.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c;
      opt.textContent = c;
      countryFilter.appendChild(opt);
    });
  }

  function updateMetrics() {
    if (!statTotal) return;

    statTotal.textContent = membersData.length;
    if (totalCountSpan) totalCountSpan.textContent = membersData.length;
    
    const countries = new Set(membersData.map((m) => m.country).filter(Boolean));
    statCountries.textContent = countries.size;

    const institutions = new Set(membersData.map((m) => m.institutional_affiliation).filter(Boolean));
    statInstitutions.textContent = institutions.size;

    const now = new Date();
    statUpdated.textContent = `${now.toLocaleString('default', { month: 'short' })} ${now.getFullYear()}`;
  }

  function clearFilters() {
    searchInput.value = "";
    countryFilter.value = "";
    linkFilter.value = "";
    renderMembers(membersData);
  }

  function cleanText(str) {
    if (!str) return "";
    str = str.trim();
    // Remove VAT/OIB patterns case-insensitively
    str = str.replace(/\bvat\s*:\s*[a-z0-9]+/gi, "");
    str = str.replace(/\boib\s*:\s*[a-z0-9]+/gi, "");
    // Remove "no department", "no affiliation" etc. case-insensitively
    if (/^(no department|no affiliation|none|n\/a|-)$/i.test(str)) {
      return "";
    }
    // Clean up multiple commas, pipes, spaces
    str = str.replace(/,\s*,/g, ",");
    str = str.replace(/\|\s*\|/g, "|");
    return str.replace(/^[ ,|]+|[ ,|]+$/g, "").trim();
  }

  function handleFilter() {
    const query = searchInput.value.toLowerCase();
    const country = countryFilter.value;
    const linkType = linkFilter.value;

    const filtered = membersData.filter((m) => {
      // Name or Affiliation Match safely
      const nameVal = (m.full_name || "").toLowerCase();
      const affilVal = (m.institutional_affiliation || "").toLowerCase();
      const countryVal = (m.country || "").toLowerCase();

      const matchesSearch =
        nameVal.includes(query) ||
        affilVal.includes(query) ||
        countryVal.includes(query);

      // Country Match
      const matchesCountry = country === "" || m.country === country;

      // Link Match
      let matchesLink = true;
      if (linkType === "website") matchesLink = !!m.website_url;
      if (linkType === "linkedin") matchesLink = !!m.linkedin_url;
      if (linkType === "orcid") matchesLink = !!m.orcid_url;
      if (linkType === "twitter") matchesLink = !!m.twitter_x_url;

      return matchesSearch && matchesCountry && matchesLink;
    });

    renderMembers(filtered);
  }

  function renderMembers(members) {
    membersGrid.innerHTML = "";
    
    if (resultsCount) resultsCount.textContent = members.length;

    if (members.length === 0) {
      noResultsMsg.style.display = "block";
    } else {
      noResultsMsg.style.display = "none";
      const fragment = document.createDocumentFragment();

      members.forEach((m) => {
        const row = document.createElement("article");
        row.className = "member-row";

        // Avatar
        const avatar = document.createElement("div");
        avatar.className = "member-avatar";
        if (m.avatar_url) {
            const img = document.createElement("img");
            img.src = m.avatar_url;
            img.alt = `${m.full_name} Photo`;
            img.className = "member-avatar-img";
            avatar.appendChild(img);
        } else {
            avatar.textContent = m.initials || "";
        }

        // Main info
        const main = document.createElement("div");
        main.className = "member-main";

        const header = document.createElement("div");
        header.className = "member-header";
        const name = document.createElement("h3");
        name.className = "member-name";
        name.textContent = m.full_name;
        header.appendChild(name);
        main.appendChild(header);

        // Affiliation & Department (hierarchy)
        const affil = cleanText(m.institutional_affiliation);
        const dept = cleanText(m.department);
        if (affil) {
          const affilDiv = document.createElement("div");
          affilDiv.className = "member-affiliation";
          affilDiv.textContent = dept ? `${dept}, ${affil}` : affil;
          main.appendChild(affilDiv);
        } else if (dept) {
          const affilDiv = document.createElement("div");
          affilDiv.className = "member-affiliation";
          affilDiv.textContent = dept;
          main.appendChild(affilDiv);
        }

        // Country
        const country = cleanText(m.country);
        if (country) {
          const countryDiv = document.createElement("div");
          countryDiv.className = "member-country";
          countryDiv.textContent = country;
          main.appendChild(countryDiv);
        }

        // Links
        const linksDiv = document.createElement("div");
        linksDiv.className = "member-links";

        if (m.email_private) {
          const emailLink = document.createElement("a");
          emailLink.href = "#";
          emailLink.className = "member-link-item";
          emailLink.textContent = "Email";
          emailLink.title = "Copy email to clipboard";
          emailLink.addEventListener("click", async function(e) {
            e.preventDefault();
            try {
              await navigator.clipboard.writeText(m.email_private);
              this.textContent = "Copied!";
              setTimeout(() => {
                this.textContent = m.email_private;
              }, 1500);
            } catch (err) {
              this.textContent = m.email_private;
            }
          });
          linksDiv.appendChild(emailLink);
        }
        if (m.website_url) linksDiv.appendChild(createLink("Website", m.website_url));
        if (m.orcid_url) linksDiv.appendChild(createLink("ORCID", m.orcid_url));
        if (m.linkedin_url) linksDiv.appendChild(createLink("LinkedIn", m.linkedin_url));
        if (m.researchgate_url) linksDiv.appendChild(createLink("ResearchGate", m.researchgate_url));
        if (m.twitter_x_url) linksDiv.appendChild(createLink("Twitter/X", m.twitter_x_url));

        if (linksDiv.children.length > 0) {
          main.appendChild(linksDiv);
        }

        row.appendChild(avatar);
        row.appendChild(main);
        fragment.appendChild(row);
      });

      membersGrid.appendChild(fragment);
    }
  }

  function createLink(text, href) {
    const a = document.createElement("a");
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.textContent = text;
    a.className = "member-link-item";
    return a;
  }
});
