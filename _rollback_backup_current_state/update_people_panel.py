import re

with open('d:/U/ISA/ISA42/people/index.qmd', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Revert <details> back to <article> and remove <summary> wrappers
content = re.sub(r'<details class="rc42-roster-v16__card">', r'<article class="rc42-roster-v16__card">', content)
content = re.sub(r'</details>', r'</article>', content)
content = re.sub(r'<summary class="board-member-summary">\s*(<div class="rc42-roster-v16__person">.*?</p>\s*</div>\s*</div>)\s*<div style="text-align: center;"><span class="board-member-toggle" aria-hidden="true"></span></div>\s*</summary>',
                 r'\1\n                <div style="text-align: center;"><button class="board-member-toggle" type="button" aria-expanded="false">+</button></div>',
                 content, flags=re.DOTALL)

# 2. Add `hidden` to board-member-details
content = re.sub(r'<div class="board-member-details rc42-roster-v16__profile-panel">', r'<div class="board-member-details rc42-roster-v16__profile-panel" hidden>', content)

# 3. Wrap `.rc42-roster-v16__roster` in `.board-directory-layout` and add `<aside>`
content = content.replace(
    '<div class="rc42-roster-v16__roster">',
    '<div class="board-directory-layout">\n      <div class="rc42-roster-v16__roster board-cards-area">'
)

content = content.replace(
    '        </section>\n      </div>\n\n    </section>',
    '        </section>\n      </div>\n\n      <aside class="board-detail-panel" aria-live="polite">\n        <button class="board-detail-close" type="button" aria-label="Close details">×</button>\n        <div class="board-detail-content"></div>\n      </aside>\n\n      </div>\n\n    </section>'
)

# 4. Remove the old script and insert the new one
content = re.sub(r'<script>\s*document.addEventListener\("DOMContentLoaded", function \(\) \{.*?</script>', '', content, flags=re.DOTALL)

new_script = '''<script>
document.addEventListener("DOMContentLoaded", function () {
  const cards = document.querySelectorAll(".rc42-roster-v16__card");
  const panel = document.querySelector(".board-detail-panel");
  const panelContent = document.querySelector(".board-detail-content");
  const closeButton = document.querySelector(".board-detail-close");
  const layout = document.querySelector(".board-directory-layout");

  if (!panel || !panelContent) return;

  function closePanel() {
    panel.classList.remove("is-open");
    if(layout) layout.classList.remove("has-open-panel");
    panelContent.innerHTML = "";

    cards.forEach((card) => {
      card.classList.remove("is-selected");
      const btn = card.querySelector(".board-member-toggle");
      if (btn) {
        btn.setAttribute("aria-expanded", "false");
        btn.textContent = "+";
      }
    });
  }

  cards.forEach((card) => {
    const button = card.querySelector(".board-member-toggle");
    const details = card.querySelector(".board-member-details");

    if (!button || !details) return;

    button.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();

      const isSelected = card.classList.contains("is-selected");

      closePanel();

      if (!isSelected) {
        card.classList.add("is-selected");
        button.setAttribute("aria-expanded", "true");
        button.textContent = "–";
        panelContent.innerHTML = details.innerHTML;
        panel.classList.add("is-open");
        if(layout) layout.classList.add("has-open-panel");
      }
    });
  });

  if (closeButton) {
    closeButton.addEventListener("click", closePanel);
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closePanel();
    }
  });
});
</script>
'''
content = content.replace('```\n', new_script + '\n```\n')

# 5. Remove old CSS block (.rc42-roster-v16__card[open] up to the end of </style>)
content = re.sub(r'\.rc42-roster-v16__card\[open\] \{.*?</style>', '</style>', content, flags=re.DOTALL)

# Add the new CSS
new_css = '''
.board-directory-layout {
  display: block;
  min-width: 0;
}

@media (min-width: 901px) {
  .board-directory-layout.has-open-panel {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 320px;
    gap: 1.5rem;
    align-items: start;
  }
}

.board-cards-area {
  min-width: 0;
}

.board-detail-panel {
  display: none;
  background: #ffffff;
  border: 1px solid #e5eaf0;
  border-radius: 1rem;
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.06);
  padding: 1.2rem;
  position: sticky;
  top: 84px;
}

.board-detail-panel.is-open {
  display: block;
}

.board-detail-close {
  float: right;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  border-radius: 999px;
  width: 28px;
  height: 28px;
  color: #64748b;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.board-detail-close:hover {
  background: #f1f5f9;
}

.board-detail-content {
  clear: both;
  font-size: 0.92rem;
  line-height: 1.6;
  color: #475569;
  padding-top: 1rem;
}

.board-detail-content p {
  margin-top: 0;
  margin-bottom: 1rem;
}

.board-member-toggle {
  margin-top: 1rem;
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
  cursor: pointer;
}

.rc42-roster-v16__card:hover .board-member-toggle {
  background: #00a99d;
  color: #ffffff;
}

.rc42-roster-v16__card.is-selected {
  border-color: #0d9488;
  box-shadow: 0 12px 30px rgba(13, 148, 136, 0.12);
}

.rc42-roster-v16__card.is-selected .board-member-toggle {
  background: #0d9488;
  color: #ffffff;
  border-color: #0d9488;
}

.rc42-roster-v16__tags span {
  font-size: 0.75rem;
}

@media (max-width: 900px) {
  .board-directory-layout,
  .board-directory-layout.has-open-panel {
    display: block;
  }

  .board-detail-panel.is-open {
    margin-top: 1rem;
    position: static;
  }
}
'''

content = content.replace('</style>', new_css + '\n</style>')

with open('d:/U/ISA/ISA42/people/index.qmd', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated people/index.qmd to use side panel layout")
