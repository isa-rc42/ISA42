# ISA RC42 Social Psychology — Digital Portal

A [Quarto](https://quarto.org/)-based website for **Research Committee 42 (Social Psychology)** of the **International Sociological Association (ISA)**.

This portal serves as a complementary digital presence for RC42, extending the [official ISA RC42 page](https://www.isa-sociology.org/en/research-networks/research-committees/rc42-social-psychology/) with dynamic content, member profiles, and community resources.

> **⚠️ Nothing on this portal is published automatically.** All content undergoes human review by the RC42 board before publication.

---

## Stack

| Component | Technology |
|-----------|------------|
| **Site generator** | [Quarto](https://quarto.org/) |
| **Hosting** | [Netlify](https://www.netlify.com/) (planned) |
| **Repository** | [GitHub](https://github.com/) |
| **Data** | YAML files in `data/` |
| **Forms** | HTML forms with [Netlify Forms](https://www.netlify.com/products/forms/) |
| **Automation** | GitHub Actions (planned) |
| **Content review** | Manual (LLM-assisted drafts in future phase) |

---

## Local Development

### Prerequisites

- [Quarto](https://quarto.org/docs/get-started/) (v1.4 or later recommended)
- A text editor (VS Code with Quarto extension recommended)

### Render the Site

```bash
cd rc42-site
quarto render
```

The rendered site will be output to `_site/`.

### Preview Locally

```bash
quarto preview
```

This starts a local development server with live reload.

---

## Publishing to Netlify

### Option 1: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd rc42-site
quarto render
netlify deploy --dir=_site --prod
```

### Option 2: Netlify + GitHub Integration

1. Push this repository to GitHub.
2. Connect the repository to Netlify.
3. Set the **build command** to `quarto render`.
4. Set the **publish directory** to `_site`.
5. Netlify will automatically deploy on each push to the main branch.

---

## Project Structure

```
rc42-site/
├── _quarto.yml              # Quarto configuration
├── index.qmd                # Home page
├── styles.scss              # Custom theme (SCSS)
├── about/                   # About RC42, objectives, history
├── board/                   # Current board
├── past-boards/             # Previous boards
├── statutes/                # RC42 statutes
├── membership/              # How to join RC42
├── members/                 # Members directory
│   └── profiles/            # Individual member profiles
├── news/                    # News and announcements
│   └── posts/               # Individual news posts
├── blog/                    # Blog posts by members
│   └── posts/               # Individual blog posts
├── events/                  # Events listing
├── opportunities/           # Calls, positions, fellowships
├── newsletter/              # Newsletter archive
│   └── archive/             # Issues by year
├── resources/               # Publications, teaching, datasets
├── discussions/             # Future discussion space
├── participate/             # Forms and participation info
├── contact/                 # Contact information
├── data/                    # Structured data (YAML)
│   ├── board.yml
│   ├── members.yml
│   ├── events.yml
│   ├── opportunities.yml
│   ├── newsletters.yml
│   └── resources.yml
├── scripts/                 # Automation scripts (placeholders)
├── .github/                 # GitHub issue templates and workflows
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
├── README.md                # This file
└── CONTRIBUTING.md           # Contribution guidelines
```

---

## Editorial Workflow

### Current (Manual)

1. A member submits content via the website form or email.
2. The RC42 board receives the submission (via Netlify Forms or email).
3. A board member or designated editor reviews the submission.
4. If approved, the editor creates/updates the relevant `.qmd` or `.yml` file.
5. Changes are committed to the repository.
6. The site is rebuilt and deployed.

### Future (GitHub Issues + LLM + Actions)

1. A submission creates a GitHub Issue (via form integration or manually).
2. A GitHub Action triggers an LLM to prepare a draft `.qmd` or `.yml` file.
3. The LLM draft is submitted as a Pull Request.
4. A human editor reviews the PR.
5. Once approved and merged, the site is automatically rebuilt.
6. Nothing is published without explicit human approval.

> **Note**: The LLM integration and GitHub Actions workflows are included as placeholders. They require API keys (e.g., `OPENAI_API_KEY`) and further configuration before activation.

---

## Content Guidelines

- **Language**: English (primary language of ISA and RC42).
- **Tone**: Academic, professional, international.
- **Accuracy**: No fabricated information. Use clear placeholders when information is missing.
- **Privacy**: Member profiles require explicit consent. Contact information is shared only if the member opts in.
- **Attribution**: All contributions are attributed to their authors.

---

## License

Content on this portal is published by RC42 Social Psychology, a Research Committee of the International Sociological Association. All rights reserved unless otherwise stated.

---

## Contact

- **Email**: [isa-rc42@isa-sociology.org](mailto:isa-rc42@isa-sociology.org)
- **ISA Website**: [www.isa-sociology.org](https://www.isa-sociology.org/)
- **RC42 on ISA**: [RC42 Social Psychology](https://www.isa-sociology.org/en/research-networks/research-committees/rc42-social-psychology/)
