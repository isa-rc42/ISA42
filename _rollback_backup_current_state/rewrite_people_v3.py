import io

new_content = """---
toc: false
title-block-style: none
page-layout: full
---

```{=html}
<style>
/* Neutralizar margen superior extra de Quarto */
#quarto-content,
main.content,
.page-layout-full {
  padding-top: 0 !important;
  margin-top: 0 !important;
}

.board-directory-section,
.board-directory-section * {
  box-sizing: border-box;
}

.board-directory-section {
  max-width: 1320px;
  width: min(1320px, calc(100vw - 2rem));
  margin: 0 auto;
  padding: 3rem 1rem 5rem;
  color: #08152b;
}

@media (min-width: 768px) {
  .board-directory-section {
    padding: 3rem 2rem 5rem;
  }
}

.board-directory-header {
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(8, 21, 43, 0.12);
}

.section-kicker {
  display: inline-block;
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.26em;
  text-transform: uppercase;
  color: #00a99d;
  margin-bottom: 12px;
}

.section-kicker::after {
  content: "";
  display: block;
  width: 78px;
  height: 2px;
  background: #00a99d;
  margin-top: 10px;
}

.board-directory-header h1 {
  font-size: clamp(1.8rem, 3vw, 2.6rem);
  line-height: 1.1;
  letter-spacing: -0.04em;
  margin: 0 0 16px;
  color: #08152b;
}

.board-directory-header p {
  margin: 0 0 20px;
  font-size: 0.95rem;
  line-height: 1.55;
  color: #506487;
  max-width: 800px;
}

.board-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}

.btn-rc42-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 0 20px;
  border-radius: 999px;
  background: #00a99d;
  color: #ffffff !important;
  font-size: 0.85rem;
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.2s;
}

.btn-rc42-primary:hover {
  background: #008f88;
}

.board-past-link {
  color: #003b7a !important;
  font-size: 0.85rem;
  font-weight: 800;
  text-decoration: none;
}

.board-past-link:hover {
  text-decoration: underline;
}

.board-directory-title {
  margin-bottom: 24px;
}

.board-directory-title h2 {
  font-size: clamp(1.4rem, 2.5vw, 1.8rem);
  line-height: 1.2;
  letter-spacing: -0.03em;
  margin: 10px 0 0;
  color: #08152b;
}

.board-member-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.25rem;
  align-items: stretch;
}

.board-member-card {
  min-width: 0;
  padding: 1.25rem 1rem;
  border: 1px solid #e5eaf0;
  border-radius: 1rem;
  background: #ffffff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.035);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  position: relative;
  cursor: pointer;
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.board-member-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
}

.board-member-card.is-selected {
  border-color: #0d9488;
  box-shadow: 0 12px 28px rgba(13, 148, 136, 0.12);
}

.board-member-card img {
  width: 76px;
  height: 76px;
  object-fit: cover;
  border-radius: 999px;
  margin-bottom: 0.85rem;
  background: #dfe7f2;
}

.board-member-role {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #0d9488;
  margin-bottom: 0.4rem;
}

.board-member-card h3 {
  font-size: 1rem;
  line-height: 1.25;
  margin: 0 0 0.5rem;
  color: #0b1628;
}

.board-member-card p {
  font-size: 0.8rem;
  line-height: 1.4;
  color: #64748b;
  margin: 0 0 1.25rem;
}

.board-member-toggle {
  margin-top: auto;
  width: 32px;
  height: 32px;
  border-radius: 999px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #0d9488;
  font-size: 1.1rem;
  font-weight: 800;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  z-index: 3;
  pointer-events: auto;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
}

.board-member-card:hover .board-member-toggle {
  background: #e6fffb;
  border-color: #5eead4;
}

.board-member-card.is-selected .board-member-toggle {
  background: #0d9488;
  border-color: #0d9488;
  color: #ffffff;
}

.board-member-card::before,
.board-member-card::after {
  pointer-events: none;
}

.board-expanded-detail {
  margin-top: 1.5rem;
  grid-column: 1 / -1;
}

.board-expanded-detail[hidden] {
  display: none;
}

.board-expanded-detail-inner {
  position: relative;
  display: grid;
  grid-template-columns: minmax(220px, 0.8fr) minmax(0, 1.4fr);
  gap: 2rem;
  padding: 1.75rem 2rem;
  border: 1px solid #dbe7e5;
  border-radius: 1.1rem;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  box-shadow: 0 16px 38px rgba(15, 23, 42, 0.065);
}

.board-expanded-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 32px;
  height: 32px;
  border-radius: 999px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #64748b;
  font-weight: 800;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: background 0.2s;
}

.board-expanded-close:hover {
  background: #f1f5f9;
}

.board-expanded-role {
  margin-bottom: 0.5rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #0d9488;
}

.board-expanded-header h3 {
  margin: 0 0 0.5rem;
  font-size: 1.4rem;
  line-height: 1.25;
  color: #0b1628;
}

.board-expanded-header p {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
  color: #64748b;
}

.board-expanded-body {
  font-size: 0.95rem;
  line-height: 1.65;
  color: #475569;
}

.board-expanded-body p {
  margin-top: 0;
  margin-bottom: 1rem;
}

.board-expanded-body a {
  color: #003b7a !important;
  font-weight: 850;
  text-decoration: none;
}

.board-expanded-body a:hover {
  text-decoration: underline;
}

.rc42-tags-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 1rem;
}

.board-expanded-body .tag,
.board-expanded-body .badge,
.rc42-tags-group span {
  display: inline-flex;
  padding: 0.35rem 0.6rem;
  border-radius: 999px;
  background: #e8eef5;
  color: #475569;
  font-size: 0.75rem;
  font-weight: 750;
}

@media (max-width: 900px) {
  .board-expanded-detail-inner {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1.5rem;
  }
}

@media (max-width: 600px) {
  .board-member-grid {
    grid-template-columns: 1fr;
  }
}

</style>

<section class="board-directory-section">

  <div class="board-directory-header">
    <span class="section-kicker">Leadership</span>
    <h1>Board 2023–2027</h1>
    <p>The current executive board coordinates RC42 initiatives, membership communication, and our active participation in International Sociological Association activities.</p>
    <div class="board-actions">
      <a class="btn-rc42-primary" href="/members/index.html">Browse members directory</a>
      <a class="board-past-link" href="past-boards/index.qmd">View past boards since 1988 &rarr;</a>
    </div>
  </div>

  <div class="board-directory-main">
    <div class="board-directory-title">
      <span class="section-kicker">Current Board</span>
      <h2>Officers and Board Members</h2>
    </div>

    <div class="board-member-grid">
      
      <!-- Member 1 -->
      <article class="board-member-card">
        <img src="https://conferencias.coes.cl/wp-content/uploads/2017/03/Juan-Carlos-Castillo_2-e1489158179229.jpg" alt="Juan Carlos Castillo">
        <div class="board-member-role">President</div>
        <h3>Juan Carlos Castillo</h3>
        <p>Universidad de Chile, Chile</p>
        <button class="board-member-toggle" type="button" aria-expanded="false" aria-label="View details">+</button>
        
        <div class="board-member-details" hidden>
          <p>Professor at the Department of Sociology, Universidad de Chile, and Director of Research and Publications at the Faculty of Social Sciences. His work focuses on distributive justice, citizenship education, social cohesion, quantitative methods, structural equation modeling, multilevel analysis, and open science.</p>
          <div class="rc42-tags-group">
            <span>Distributive justice</span>
            <span>Citizenship education</span>
            <span>Social cohesion</span>
            <span>Open science</span>
            <span>Quantitative methods</span>
          </div>
          <div style="margin-top: 1rem;">
            <a href="https://jc-castillo.com/" target="_blank" rel="noopener">Visit website &rarr;</a>
          </div>
        </div>
      </article>

      <!-- Member 2 -->
      <article class="board-member-card">
        <img src="http://pages.charlotte.edu/lisa-walker/wp-content/uploads/sites/23/2024/11/walker_lisa_5096c.jpg" alt="Lisa Slattery Walker">
        <div class="board-member-role">Secretary / Treasurer</div>
        <h3>Lisa Slattery Walker</h3>
        <p>University of North Carolina at Charlotte, USA</p>
        <button class="board-member-toggle" type="button" aria-expanded="false" aria-label="View details">+</button>
        
        <div class="board-member-details" hidden>
          <p>Professor of Sociology at UNC Charlotte. Her research focuses on small group interaction, nonverbal behaviors, identity, emotions, gender, expectations, and status processes.</p>
          <div class="rc42-tags-group">
            <span>Small group interaction</span>
            <span>Identity</span>
            <span>Emotions</span>
            <span>Gender</span>
            <span>Status processes</span>
          </div>
        </div>
      </article>

      <!-- Member 3 -->
      <article class="board-member-card">
        <img src="https://drupalwebprod-files.up.ac.za/Public/styles/responsive_1_1_600w/public/2026-05/Charles%20Puttergill%201%20%282%29.jpg?VersionId=5fI_xxA2nlT5xmEAUCwJm9AFBCwbGEWu&h=ec3aa346&itok=aRk2Jy25" alt="Charles Puttergill">
        <div class="board-member-role">Board Member</div>
        <h3>Charles Puttergill</h3>
        <p>University of Pretoria, South Africa</p>
        <button class="board-member-toggle" type="button" aria-expanded="false" aria-label="View details">+</button>
        
        <div class="board-member-details" hidden>
          <p>Senior Lecturer in the Department of Sociology at the University of Pretoria. His research interests include race, identity, methodology, urban sociology, demography, and research methods.</p>
          <div class="rc42-tags-group">
            <span>Race and identity</span>
            <span>Methodology</span>
            <span>Urban sociology</span>
            <span>Demography</span>
            <span>Research methods</span>
          </div>
        </div>
      </article>

      <!-- Member 4 -->
      <article class="board-member-card">
        <img src="https://i1.rgstatic.net/ii/profile.image/11431281153740428-1682528347352_Q128/Karla-Henriquez-Ojeda.jpg" alt="Karla Henríquez Ojeda">
        <div class="board-member-role">Board Member</div>
        <h3>Karla Henríquez Ojeda</h3>
        <p>Université catholique de Louvain, Belgium</p>
        <button class="board-member-toggle" type="button" aria-expanded="false" aria-label="View details">+</button>
        
        <div class="board-member-details" hidden>
          <p>Researcher with a background in sociological social psychology and American studies. Her work focuses on activism, social movements, youth, subjectivation, and emotions in Latin American contexts.</p>
          <div class="rc42-tags-group">
            <span>Activism</span>
            <span>Social movements</span>
            <span>Youth</span>
            <span>Emotions</span>
            <span>Latin America</span>
          </div>
        </div>
      </article>

      <!-- Member 5 -->
      <article class="board-member-card">
        <img src="https://isaconf.confex.com/data/image/isaconf/gmssi/Person_55816_image_987_0.jpg" alt="Deepak Kumar Verma">
        <div class="board-member-role">Board Member</div>
        <h3>Deepak Kumar Verma</h3>
        <p>Dr. B. R. Ambedkar University of Social Sciences, India</p>
        <button class="board-member-toggle" type="button" aria-expanded="false" aria-label="View details">+</button>
        
        <div class="board-member-details" hidden>
          <p>Professor at Dr. B. R. Ambedkar University of Social Sciences. His work spans social psychology, social inequality, status, development, research methodology, and social justice.</p>
          <div class="rc42-tags-group">
            <span>Social inequality</span>
            <span>Status</span>
            <span>Development</span>
            <span>Research methodology</span>
            <span>Social justice</span>
          </div>
        </div>
      </article>

    </div>

    <!-- The expanded detail card -->
    <div class="board-expanded-detail" hidden></div>

  </div>

</section>

<script>
document.addEventListener("DOMContentLoaded", function () {
  const cards = document.querySelectorAll(".board-member-card");
  const detail = document.querySelector(".board-expanded-detail");

  if (!cards.length || !detail) return;

  function resetCards() {
    cards.forEach(card => {
      card.classList.remove("is-selected");
      const btn = card.querySelector(".board-member-toggle");
      if (btn) {
        btn.textContent = "+";
        btn.setAttribute("aria-expanded", "false");
      }
    });
  }

  function closeDetail() {
    resetCards();
    detail.hidden = true;
    detail.innerHTML = "";
  }

  function openDetail(card) {
    const isSelected = card.classList.contains("is-selected");

    if (isSelected) {
      closeDetail();
      return;
    }

    resetCards();

    const role = card.querySelector(".board-member-role")?.textContent?.trim() || "";
    const name = card.querySelector("h3")?.textContent?.trim() || "";
    const institution = card.querySelector("p")?.textContent?.trim() || "";
    const details = card.querySelector(".board-member-details")?.innerHTML || "<p>No additional information available.</p>";

    card.classList.add("is-selected");

    const btn = card.querySelector(".board-member-toggle");
    if (btn) {
      btn.textContent = "–";
      btn.setAttribute("aria-expanded", "true");
    }

    detail.innerHTML = `
      <div class="board-expanded-detail-inner">
        <button class="board-expanded-close" type="button" aria-label="Close details">×</button>

        <div class="board-expanded-header">
          <div class="board-expanded-role">${role}</div>
          <h3>${name}</h3>
          <p>${institution}</p>
        </div>

        <div class="board-expanded-body">
          ${details}
        </div>
      </div>
    `;

    detail.hidden = false;

    const closeButton = detail.querySelector(".board-expanded-close");
    if (closeButton) {
      closeButton.addEventListener("click", function(event) {
        event.stopPropagation();
        closeDetail();
      });
    }
  }

  cards.forEach(card => {
    card.addEventListener("click", function () {
      openDetail(card);
    });

    const btn = card.querySelector(".board-member-toggle");
    if (btn) {
      btn.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        openDetail(card);
      });
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeDetail();
  });
});
</script>
```
"""

with open('d:/U/ISA/ISA42/people/index.qmd', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated people/index.qmd to use the new compact grid with an expanded detail card underneath.")
