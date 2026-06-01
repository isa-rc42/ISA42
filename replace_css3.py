import re

with open('d:/U/ISA/webRC42ISA/rc42-site/styles.scss', 'r', encoding='utf-8') as f:
    content = f.read()

# Try to find the section block to remove
start_marker = "// New Board & People Section Redesign"
end_marker = "// Home Page Board Block Styling"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    # Also find the // ====== line right above start_marker
    start_border = content.rfind("// ======", 0, start_idx)
    if start_border != -1:
        start_idx = start_border
    
    new_css = """// =============================================================================
// New Board & People Section Redesign V6 (Editorial, Custom Page Layout)
// =============================================================================

.people-board-v6 {
  background-color: #f8fafc;
  color: #334155;
  padding: 4rem 0 6rem;
  width: 100%; /* Take full width of custom layout */
}

.people-board-v6__shell {
  max-width: 1240px;
  margin: 0 auto;
  padding-inline: clamp(1.5rem, 4vw, 4rem);
}

.people-board-v6__layout {
  display: grid;
  grid-template-columns: minmax(280px, 0.9fr) minmax(680px, 1.8fr);
  gap: clamp(2rem, 4vw, 4rem);
  align-items: start;
}

@media (max-width: 1024px) {
  .people-board-v6__layout {
    grid-template-columns: 1fr;
    gap: 3rem;
  }
}

/* Left Column: Intro */
.people-board-v6__intro {
  position: sticky;
  top: 6rem;
}

@media (max-width: 1024px) {
  .people-board-v6__intro {
    position: static;
  }
}

.people-board-v6__intro .section-kicker {
  display: inline-block;
  color: #0d9488;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.85rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #0d9488;
  padding-bottom: 0.25rem;
}

.people-board-v6__intro h1 {
  font-size: clamp(2.2rem, 4vw, 2.8rem);
  color: #0f172a;
  margin-top: 0;
  margin-bottom: 1.25rem;
  line-height: 1.1;
  border-bottom: none;
}

.people-board-v6__intro .intro-text {
  font-size: 1.15rem;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 2.5rem;
}

/* Secondary CTA for Members Directory */
.people-board-v6__directory {
  background: #ffffff;
  padding: 1.75rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.02);
}

.people-board-v6__directory h3 {
  margin-top: 0;
  color: #1e293b;
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
}

.people-board-v6__directory p {
  color: #64748b;
  margin-bottom: 1.25rem;
  font-size: 0.9rem;
  line-height: 1.5;
}

.people-board-v6__directory .btn {
  width: 100%;
}

/* Right Column: Roster */
.people-board-v6__section {
  margin-bottom: 4rem;
}

.people-board-v6__section:last-child {
  margin-bottom: 0;
}

.board-section-title {
  font-size: 1.75rem;
  color: #0f172a;
  margin-bottom: 2rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e2e8f0;
  margin-top: 0;
}

/* Officers Grid */
.people-board-v6__officers-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(320px, 1fr));
  gap: 2rem;
}

@media (max-width: 1200px) {
  .people-board-v6__officers-grid {
    grid-template-columns: 1fr;
  }
}

/* Members Grid */
.people-board-v6__members-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(200px, 1fr));
  gap: 1.5rem;
}

@media (max-width: 1200px) {
  .people-board-v6__members-grid {
    grid-template-columns: repeat(2, minmax(200px, 1fr));
  }
}

@media (max-width: 640px) {
  .people-board-v6__members-grid {
    grid-template-columns: 1fr;
  }
}

/* Cards */
.people-board-v6__card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
  display: flex;
  flex-direction: column;
}

.people-board-v6__card:hover {
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
  border-color: rgba(13, 148, 136, 0.3);
}

.card-summary {
  display: flex;
  padding: 1.5rem;
  gap: 1.25rem;
  align-items: flex-start;
}

.people-board-v6__card--member .card-summary {
  flex-direction: column;
  text-align: center;
  align-items: center;
}

.card-photo-wrapper {
  flex-shrink: 0;
}

.card-photo {
  width: 85px;
  height: 85px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #f8fafc;
}

.card-fallback {
  width: 85px;
  height: 85px;
  border-radius: 50%;
  background: rgba(13, 148, 136, 0.08);
  color: #0d9488;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.card-meta {
  flex: 1;
}

.card-role {
  display: block;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #0d9488;
  margin-bottom: 0.3rem;
}

.card-name {
  font-size: 1.2rem;
  color: #0f172a;
  margin: 0 0 0.3rem 0;
  line-height: 1.2;
}

.card-affil {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.card-subtitle {
  font-size: 0.8rem;
  color: rgba(100, 116, 139, 0.85);
  margin: 0.3rem 0 0 0;
  font-style: italic;
  line-height: 1.3;
}

/* Details Panel */
.card-details {
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  margin-top: auto;
}

.card-details[open] summary {
  background: #ffffff;
  color: #0d9488;
}

.card-details[open] summary::after {
  transform: rotate(180deg);
}

.card-details summary {
  padding: 0.85rem 1.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e3a8a;
  cursor: pointer;
  list-style: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
  transition: background-color 0.2s, color 0.2s;
}

.card-details summary::-webkit-details-marker {
  display: none;
}

.card-details summary::after {
  content: "▼";
  font-size: 0.6rem;
  transition: transform 0.2s ease;
  opacity: 0.7;
}

.card-details summary:hover {
  background: #ffffff;
  color: #0d9488;
}

.card-details-content {
  padding: 1.5rem;
  background: #ffffff;
  border-top: 1px dashed #e2e8f0;
  text-align: left;
}

.card-details-content p {
  font-size: 0.92rem;
  line-height: 1.6;
  color: #334155;
  margin-top: 0;
  margin-bottom: 1.25rem;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1rem;
}

.card-tags span {
  background: #f8fafc;
  border: 1px solid rgba(30, 41, 59, 0.08);
  border-radius: 4px;
  font-size: 0.75rem;
  color: #64748b;
  padding: 0.2rem 0.5rem;
}

.card-link {
  display: inline-block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #0d9488;
  text-decoration: none;
}

.card-link:hover {
  text-decoration: underline;
}

"""
    
    # Replace content
    new_content = content[:start_idx] + new_css + content[end_idx:]
    
    with open('d:/U/ISA/webRC42ISA/rc42-site/styles.scss', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully replaced styles.scss section.")
else:
    print("Could not find target block.")
