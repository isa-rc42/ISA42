import re

with open('d:/U/ISA/ISA42/people/index.qmd', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the old board-member summary/details css we added previously.
content = re.sub(r'\.board-member-summary \{.*?</style>', '</style>', content, flags=re.DOTALL)

# Add align-items: start to grid definition if missing
# Wait, let's just make sure it's there.
content = content.replace(
    '.rc42-roster-v16__grid {\n  display: grid;\n  gap: 20px;\n  width: 100%;\n  max-width: 100%;\n  min-width: 0;\n}',
    '.rc42-roster-v16__grid {\n  display: grid;\n  gap: 20px;\n  width: 100%;\n  max-width: 100%;\n  min-width: 0;\n  align-items: start;\n}'
)

new_css = '''
.rc42-roster-v16__card[open] {
  grid-column: 1 / -1;
}

@media (min-width: 901px) {
  .rc42-roster-v16__card[open] {
    display: grid;
    grid-template-columns: minmax(260px, 0.85fr) minmax(320px, 1.15fr);
    column-gap: 1.75rem;
    align-items: stretch;
  }
  .rc42-roster-v16__card[open] .board-member-summary {
    border-right: 1px solid #e5eaf0;
    border-bottom: 0;
    padding: 1.5rem 1.6rem;
  }
  .rc42-roster-v16__card[open] .board-member-details {
    margin-top: 0;
    padding: 1.5rem 1.6rem;
    border-top: 0;
    background: #fbfdff;
    height: 100%;
  }
}

.board-member-summary {
  list-style: none;
  cursor: pointer;
  display: block;
  outline: none;
}

.board-member-summary::-webkit-details-marker {
  display: none;
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
}

.board-member-summary:hover .board-member-toggle {
  background: #00a99d;
  color: #ffffff;
}

.board-member-toggle::before {
  content: "+";
}

.rc42-roster-v16__card[open] .board-member-toggle::before {
  content: "–";
}

.board-member-details {
  font-size: 0.92rem;
  line-height: 1.6;
  color: #475569;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5eaf0;
}

.board-member-details p {
  margin-top: 0;
  margin-bottom: 1rem;
}

.rc42-roster-v16__tags span {
  font-size: 0.75rem;
}

@media (max-width: 900px) {
  .rc42-roster-v16__card[open] {
    display: block;
    grid-column: auto;
  }

  .rc42-roster-v16__card[open] .board-member-summary {
    border-right: 0;
    border-bottom: 1px solid #e5eaf0;
    padding-bottom: 1.5rem;
  }

  .rc42-roster-v16__card[open] .board-member-details {
    padding: 1.15rem 0 0 0;
    border-top: 0;
  }
}
'''

content = content.replace('</style>', new_css + '\n</style>')

# Add the closing JS script right before </div></div> at the end
js_script = '''
<script>
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".rc42-roster-v16__card").forEach((card) => {
    card.addEventListener("toggle", function () {
      if (card.open) {
        document.querySelectorAll(".rc42-roster-v16__card").forEach((other) => {
          if (other !== card) other.open = false;
        });
      }
    });
  });
});
</script>
'''

if js_script not in content:
    content = content.replace('  </div>\n</div>\n```', f'  </div>\n</div>\n{js_script}\n```')

with open('d:/U/ISA/ISA42/people/index.qmd', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated people/index.qmd')
