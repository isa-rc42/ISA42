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
  width: min(1360px, calc(100vw - 2rem));
  margin: 0 auto;
  padding: 3rem 1.5rem 5rem;
  color: #08152b;
}

@media (min-width: 1101px) {
  .board-directory-section {
    display: grid;
    grid-template-columns: 280px minmax(0, 1fr);
    gap: 3rem;
    align-items: start;
  }
}

.board-directory-intro {
  position: sticky;
  top: 84px;
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

.board-directory-intro h1 {
  font-size: clamp(1.8rem, 3.2vw, 2.8rem);
  line-height: 0.96;
  letter-spacing: -0.06em;
  margin: 0 0 16px;
  color: #08152b;
}

.board-directory-intro p {
  margin: 0 0 22px;
  font-size: 0.88rem;
  line-height: 1.55;
  color: #506487;
}

.board-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
}

.btn-rc42-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 0 18px;
  border-radius: 999px;
  background: #00a99d;
  color: #ffffff !important;
  font-size: 0.82rem;
  font-weight: 850;
  text-decoration: none;
  white-space: nowrap;
}

.btn-rc42-primary:hover {
  background: #008f88;
}

.board-past-link {
  color: #003b7a !important;
  font-size: 0.82rem;
  font-weight: 850;
  text-decoration: none;
}

.board-past-link:hover {
  text-decoration: underline;
}

.board-directory-header {
  margin: 0 0 24px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(8, 21, 43, 0.12);
}

.board-directory-header h2 {
  font-size: clamp(1.6rem, 2.8vw, 2.2rem);
  line-height: 1;
  letter-spacing: -0.055em;
  margin: 10px 0 0;
  color: #08152b;
}

.board-directory-workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 1.5rem;
  align-items: start;
}

.board-member-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(190px, 1fr));
  gap: 1rem;
  align-items: start;
}

.board-list-group {
  margin-bottom: 2rem;
  grid-column: 1 / -1;
}

.board-list-group h3 {
  font-size: 1rem;
  font-weight: 850;
  margin: 0 0 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(8, 21, 43, 0.12);
  color: #2b364a;
}

.board-member-card {
  position: relative;
  background: #ffffff;
  border: 1px solid rgba(8, 21, 43, 0.10);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 10px 24px rgba(8, 21, 43, 0.03);
  text-align: center;
  cursor: pointer;
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.board-member-card.is-selected {
  border-color: #0d9488;
  box-shadow: 0 12px 28px rgba(13, 148, 136, 0.12);
}

.board-member-photo {
  width: 72px;
  height: 72px;
  border-radius: 999px;
  object-fit: cover;
  background: #dfe7f2;
  margin-bottom: 12px;
}

.board-member-role {
  font-size: 0.6rem;
  line-height: 1.2;
  font-weight: 900;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #00a99d;
  margin-bottom: 6px;
}

.board-member-card h3 {
  font-size: 1.05rem;
  line-height: 1.2;
  margin: 0 0 6px;
  color: #08152b;
}

.board-member-card p {
  font-size: 0.85rem;
  line-height: 1.4;
  color: #506487;
  margin: 0 0 16px;
}

.board-member-toggle {
  pointer-events: auto;
  position: relative;
  z-index: 2;
  cursor: pointer;
  margin-top: auto;
  width: 32px;
  height: 32px;
  border-radius: 999px;
  border: 1px solid #cbd5e1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #0d9488;
  font-weight: 800;
  background: #ffffff;
  transition: background 0.2s, color 0.2s;
}

.board-member-card.is-selected .board-member-toggle {
  background: #0d9488;
  color: #ffffff;
  border-color: #0d9488;
}

.board-member-card::before,
.board-member-card::after {
  pointer-events: none;
}

.board-member-detail-panel {
  position: sticky;
  top: 84px;
  min-height: 320px;
  padding: 1.5rem;
  border: 1px solid #e5eaf0;
  border-radius: 1rem;
  background: #ffffff;
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.05);
}

.board-detail-kicker {
  display: inline-block;
  margin-bottom: 0.45rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #0d9488;
}

.board-detail-content h3 {
  margin: 0 0 0.4rem;
  font-size: 1.25rem;
  color: #0b1628;
}

.board-detail-institution {
  margin: 0 0 1rem;
  font-size: 0.9rem;
  color: #64748b;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5eaf0;
}

.board-detail-body {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #475569;
}

.board-detail-body p {
  margin-top: 0;
  margin-bottom: 1rem;
}

.rc42-roster-v16__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.rc42-roster-v16__tags span {
  display: inline-flex;
  padding: 5px 8px;
  border-radius: 999px;
  background: #e8eef6;
  color: #405273;
  font-size: 0.7rem;
  font-weight: 750;
}

.board-detail-body a {
  display: inline-block;
  margin-top: 10px;
  color: #003b7a !important;
  font-size: 0.82rem;
  font-weight: 850;
  text-decoration: none;
}

@media (max-width: 1100px) {
  .board-directory-section {
    grid-template-columns: 1fr;
  }
  .board-directory-intro {
    position: static;
  }
  .board-directory-workspace {
    grid-template-columns: 1fr;
  }
  .board-member-detail-panel {
    margin-top: 1rem;
    position: static;
  }
  .board-actions {
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
  }
}

@media (max-width: 700px) {
  .board-directory-section {
    width: 100%;
    padding: 2rem 1rem;
  }
  .board-member-list {
    grid-template-columns: 1fr;
  }
}

</style>

<section class="board-directory-section">

  <div class="board-directory-intro">
    <span class="section-kicker">Leadership</span>
    <h1>Board 2023–2027</h1>
    <p>The current executive board coordinates RC42 initiatives, membership communication, and our active participation in International Sociological Association activities.</p>
    <div class="board-actions">
      <a class="btn-rc42-primary" href="/members/index.html">Browse members directory</a>
      <a class="board-past-link" href="past-boards/index.qmd">View past boards since 1988 &rarr;</a>
    </div>
  </div>

  <div class="board-directory-main">
    <div class="board-directory-header">
      <span class="section-kicker">Current Board</span>
      <h2>Officers and Board Members</h2>
    </div>

    <div class="board-directory-workspace">

      <div class="board-cards-area">
      
        <div class="board-list-group">
          <h3>Officers</h3>
          <div class="board-member-list">
            
            <article class="board-member-card">
              <img class="board-member-photo" src="https://conferencias.coes.cl/wp-content/uploads/2017/03/Juan-Carlos-Castillo_2-e1489158179229.jpg" alt="Juan Carlos Castillo">
              <div class="board-member-role">President</div>
              <h3>Juan Carlos Castillo</h3>
              <p>Universidad de Chile, Chile</p>
              <button class="board-member-toggle" type="button" aria-expanded="false">+</button>
              
              <div class="board-member-details" hidden>
                <p>Professor at the Department of Sociology, Universidad de Chile, and Director of Research and Publications at the Faculty of Social Sciences. His work focuses on distributive justice, citizenship education, social cohesion, quantitative methods, structural equation modeling, multilevel analysis, and open science.</p>
                <div class="rc42-roster-v16__tags">
                  <span>Distributive justice</span>
                  <span>Citizenship education</span>
                  <span>Social cohesion</span>
                  <span>Open science</span>
                  <span>Quantitative methods</span>
                </div>
                <a href="https://jc-castillo.com/" target="_blank" rel="noopener">Visit website &rarr;</a>
              </div>
            </article>

            <article class="board-member-card">
              <img class="board-member-photo" src="http://pages.charlotte.edu/lisa-walker/wp-content/uploads/sites/23/2024/11/walker_lisa_5096c.jpg" alt="Lisa Slattery Walker">
              <div class="board-member-role">Secretary / Treasurer</div>
              <h3>Lisa Slattery Walker</h3>
              <p>University of North Carolina at Charlotte, USA</p>
              <button class="board-member-toggle" type="button" aria-expanded="false">+</button>
              
              <div class="board-member-details" hidden>
                <p>Professor of Sociology at UNC Charlotte. Her research focuses on small group interaction, nonverbal behaviors, identity, emotions, gender, expectations, and status processes.</p>
                <div class="rc42-roster-v16__tags">
                  <span>Small group interaction</span>
                  <span>Identity</span>
                  <span>Emotions</span>
                  <span>Gender</span>
                  <span>Status processes</span>
                </div>
              </div>
            </article>

          </div>
        </div>

        <div class="board-list-group">
          <h3>Board Members</h3>
          <div class="board-member-list">
            
            <article class="board-member-card">
              <img class="board-member-photo" src="https://drupalwebprod-files.up.ac.za/Public/styles/responsive_1_1_600w/public/2026-05/Charles%20Puttergill%201%20%282%29.jpg?VersionId=5fI_xxA2nlT5xmEAUCwJm9AFBCwbGEWu&h=ec3aa346&itok=aRk2Jy25" alt="Charles Puttergill">
              <div class="board-member-role">Board Member</div>
              <h3>Charles Puttergill</h3>
              <p>University of Pretoria, South Africa</p>
              <button class="board-member-toggle" type="button" aria-expanded="false">+</button>
              
              <div class="board-member-details" hidden>
                <p>Senior Lecturer in the Department of Sociology at the University of Pretoria. His research interests include race, identity, methodology, urban sociology, demography, and research methods.</p>
                <div class="rc42-roster-v16__tags">
                  <span>Race and identity</span>
                  <span>Methodology</span>
                  <span>Urban sociology</span>
                  <span>Demography</span>
                  <span>Research methods</span>
                </div>
              </div>
            </article>

            <article class="board-member-card">
              <img class="board-member-photo" src="https://i1.rgstatic.net/ii/profile.image/11431281153740428-1682528347352_Q128/Karla-Henriquez-Ojeda.jpg" alt="Karla Henríquez Ojeda">
              <div class="board-member-role">Board Member</div>
              <h3>Karla Henríquez Ojeda</h3>
              <p>Université catholique de Louvain, Belgium</p>
              <button class="board-member-toggle" type="button" aria-expanded="false">+</button>
              
              <div class="board-member-details" hidden>
                <p>Researcher with a background in sociological social psychology and American studies. Her work focuses on activism, social movements, youth, subjectivation, and emotions in Latin American contexts.</p>
                <div class="rc42-roster-v16__tags">
                  <span>Activism</span>
                  <span>Social movements</span>
                  <span>Youth</span>
                  <span>Emotions</span>
                  <span>Latin America</span>
                </div>
              </div>
            </article>

            <article class="board-member-card">
              <img class="board-member-photo" src="https://isaconf.confex.com/data/image/isaconf/gmssi/Person_55816_image_987_0.jpg" alt="Deepak Kumar Verma">
              <div class="board-member-role">Board Member</div>
              <h3>Deepak Kumar Verma</h3>
              <p>Dr. B. R. Ambedkar University of Social Sciences, India</p>
              <button class="board-member-toggle" type="button" aria-expanded="false">+</button>
              
              <div class="board-member-details" hidden>
                <p>Professor at Dr. B. R. Ambedkar University of Social Sciences. His work spans social psychology, social inequality, status, development, research methodology, and social justice.</p>
                <div class="rc42-roster-v16__tags">
                  <span>Social inequality</span>
                  <span>Status</span>
                  <span>Development</span>
                  <span>Research methodology</span>
                  <span>Social justice</span>
                </div>
              </div>
            </article>

          </div>
        </div>

      </div>

      <aside class="board-member-detail-panel" aria-live="polite">
        <div class="board-detail-empty">
          <span class="board-detail-kicker">Profile details</span>
          <p>Select a board member to view their research interests and additional information.</p>
        </div>
      </aside>

    </div>
  </div>

</section>

<script>
document.addEventListener("DOMContentLoaded", function () {
  const cards = document.querySelectorAll(".board-member-card");
  const panel = document.querySelector(".board-member-detail-panel");

  if (!cards.length || !panel) return;

  function clearSelection() {
    cards.forEach(card => {
      card.classList.remove("is-selected");
      const btn = card.querySelector(".board-member-toggle");
      if (btn) {
        btn.textContent = "+";
        btn.setAttribute("aria-expanded", "false");
      }
    });
  }

  function openCard(card) {
    const details = card.querySelector(".board-member-details");
    const name = card.querySelector("h3")?.textContent || "";
    const role = card.querySelector(".board-member-role")?.textContent || "";
    const institution = card.querySelector("p")?.textContent || "";

    clearSelection();

    card.classList.add("is-selected");

    const btn = card.querySelector(".board-member-toggle");
    if (btn) {
      btn.textContent = "–";
      btn.setAttribute("aria-expanded", "true");
    }

    panel.innerHTML = `
      <div class="board-detail-content">
        <div class="board-detail-kicker">${role}</div>
        <h3>${name}</h3>
        <p class="board-detail-institution">${institution}</p>
        <div class="board-detail-body">
          ${details ? details.innerHTML : "<p>No additional information available.</p>"}
        </div>
      </div>
    `;
  }

  cards.forEach(card => {
    // Make entire card clickable
    card.addEventListener("click", function () {
      if (card.classList.contains("is-selected")) {
          // If clicked again, close it
          clearSelection();
          panel.innerHTML = `
            <div class="board-detail-empty">
              <span class="board-detail-kicker">Profile details</span>
              <p>Select a board member to view their research interests and additional information.</p>
            </div>
          `;
      } else {
        openCard(card);
      }
    });

    const btn = card.querySelector(".board-member-toggle");
    if (btn) {
      btn.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();

        if (card.classList.contains("is-selected")) {
          clearSelection();
          panel.innerHTML = `
            <div class="board-detail-empty">
              <span class="board-detail-kicker">Profile details</span>
              <p>Select a board member to view their research interests and additional information.</p>
            </div>
          `;
        } else {
          openCard(card);
        }
      });
    }
  });
  
  // Open first card by default in desktop
  if (window.innerWidth > 1100 && cards[0]) {
    openCard(cards[0]);
  }
});
</script>
```
"""

with open('d:/U/ISA/ISA42/people/index.qmd', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated people/index.qmd to use the horizontal directory layout with compact cards.")
