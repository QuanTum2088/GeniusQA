# Site Structure — QASkills.sh

> Generated: February 14, 2026
> Current Pages: 73 indexed | Target: 350+ by Month 12

---

## Current URL Hierarchy

```
qaskills.sh/
│
├── / ........................... Homepage (Priority: 1.0)
│   Schema: WebSite + Organization
│
├── /skills .................... Skills Directory (Priority: 0.9)
│   └── /skills/[author]/[slug] ... 48 Skill Detail Pages (Priority: 0.8)
│       Schema: SoftwareApplication + AggregateRating
│
├── /leaderboard ............... Trending/Top Skills (Priority: 0.8)
├── /packs ..................... Skill Bundles (Priority: 0.7)
│
├── /getting-started ........... CLI Tutorial (Priority: 0.85)
├── /how-to-publish ............ Publisher Guide (Priority: 0.65)
│
├── /blog ...................... Blog Index (Priority: 0.6)
│   └── /blog/[slug] ............ 3 Blog Posts (Priority: 0.6)
│       Schema: BlogPosting
│
├── /users/[username] .......... Publisher Profiles (dynamic)
│
├── /pricing ................... Free & OSS (Priority: 0.7)
├── /about ..................... The Testing Academy (Priority: 0.5)
├── /faq ....................... FAQ (Priority: 0.6)
│   Schema: FAQPage (needs update)
├── /contact ................... Contact Form (Priority: 0.5)
│
├── /terms ..................... Terms of Service (Priority: 0.3)
├── /privacy ................... Privacy Policy (Priority: 0.3)
├── /refund-policy ............. Refund Terms (Priority: 0.3)
│
├── /dashboard ................. User Dashboard (noindex)
│   ├── /dashboard/publish ..... Skill Publishing Wizard
│   └── /dashboard/preferences . Email Settings
│
├── /sign-in ................... Auth (noindex)
├── /sign-up ................... Auth (noindex)
└── /unsubscribe ............... Email Unsubscribe
```

---

## Proposed URL Hierarchy (After SEO Implementation)

```
qaskills.sh/
│
├── / ........................... Homepage
│   Schema: WebSite + Organization + SoftwareApplication
│
├── /skills .................... Skills Directory
│   └── /skills/[author]/[slug] ... Skill Detail Pages
│       Schema: SoftwareApplication + BreadcrumbList
│
├── /agents .................... ★ NEW: Agent Landing Pages
│   ├── /agents/claude-code ..... "QA Skills for Claude Code"
│   ├── /agents/cursor .......... "QA Skills for Cursor"
│   ├── /agents/copilot ......... "QA Skills for GitHub Copilot"
│   ├── /agents/windsurf ........ "QA Skills for Windsurf"
│   ├── /agents/cline ........... "QA Skills for Cline"
│   └── /agents/[agent-slug] .... Template for future agents
│       Schema: SoftwareApplication + ItemList + BreadcrumbList
│
├── /categories ................ ★ NEW: Testing Type Landing Pages
│   ├── /categories/e2e-testing .... "E2E Testing Skills"
│   ├── /categories/unit-testing ... "Unit Testing Skills"
│   ├── /categories/api-testing .... "API Testing Skills"
│   ├── /categories/performance-testing ... "Performance Testing Skills"
│   ├── /categories/accessibility-testing . "Accessibility Testing Skills"
│   └── /categories/[category-slug] ...... Template for new categories
│       Schema: CollectionPage + ItemList + BreadcrumbList
│
├── /compare ................... ★ NEW: Comparison Pages
│   ├── /compare/qaskills-vs-skillsmp .... Direct competitor comparison
│   ├── /compare/playwright-vs-cypress-skills . Framework comparison
│   ├── /compare/best-qa-skills-2026 ..... Roundup
│   └── /compare/[slug] ......... Template for comparisons
│       Schema: Article + BreadcrumbList
│
├── /guides .................... ★ NEW: Deep Educational Content
│   ├── /guides/playwright-e2e-complete-guide
│   ├── /guides/ai-agent-qa-setup
│   └── /guides/[slug]
│       Schema: TechArticle + BreadcrumbList
│
├── /leaderboard ............... Top Skills
├── /packs ..................... Skill Bundles
│
├── /getting-started ........... CLI Tutorial
├── /how-to-publish ............ Publisher Guide
│
├── /blog ...................... Blog Index
│   └── /blog/[slug] ............ Blog Posts (expanding to 50+)
│       Schema: BlogPosting + BreadcrumbList
│
├── /users/[username] .......... Publisher Profiles
│
├── /pricing ................... Pricing
├── /about ..................... About
├── /faq ....................... FAQ
├── /contact ................... Contact
│
├── /terms, /privacy, /refund-policy ... Legal
│
├── /llms.txt .................. ★ NEW: AI Search Discovery
├── /sitemap.xml ............... Sitemap (auto-generated)
├── /robots.txt ................ Robots (with AI crawler directives)
│
└── /dashboard (noindex), /auth (noindex)
```

---

## Internal Linking Strategy

### Link Flow Diagram
```
Homepage
  ├─→ /skills (primary CTA)
  ├─→ /getting-started
  ├─→ /agents/claude-code (featured agent)
  └─→ /blog (latest posts)

/skills
  ├─→ /skills/[author]/[slug] (each skill card)
  ├─→ /categories/[type] (filter tabs)
  └─→ /agents/[agent] (agent filter links)

/skills/[author]/[slug]
  ├─→ /categories/[type] (testing type badges)
  ├─→ /agents/[agent] (compatible agents)
  ├─→ /skills/[related-skill] (related skills)
  └─→ /getting-started (install instructions)

/agents/[agent]
  ├─→ /skills/[filtered-by-agent] (skills for this agent)
  ├─→ /getting-started (setup for this agent)
  └─→ /blog/[relevant-post] (agent-specific content)

/categories/[type]
  ├─→ /skills/[filtered-by-type] (skills in this category)
  ├─→ /guides/[relevant-guide] (deep content)
  └─→ /compare/[relevant-comparison] (framework comparisons)

/blog/[slug]
  ├─→ /skills/[mentioned-skill] (skill references)
  ├─→ /guides/[related-guide] (deeper content)
  └─→ /categories/[relevant-type] (category link)
```

### Breadcrumb Patterns

| Page Type | Breadcrumb Trail |
|-----------|-----------------|
| Skill Detail | Home > Skills > [Skill Name] |
| Agent Page | Home > Agents > [Agent Name] |
| Category Page | Home > Categories > [Category Name] |
| Blog Post | Home > Blog > [Post Title] |
| Guide | Home > Guides > [Guide Title] |
| Comparison | Home > Compare > [Comparison Title] |

---

## Sitemap Priority Map

| Priority | Pages | Change Frequency |
|----------|-------|-----------------|
| 1.0 | Homepage | Daily |
| 0.9 | /skills, /agents/* | Daily |
| 0.85 | /getting-started | Monthly |
| 0.8 | /leaderboard, /skills/*, /categories/* | Daily/Weekly |
| 0.75 | /compare/* | Monthly |
| 0.7 | /packs, /pricing, /guides/* | Weekly/Monthly |
| 0.65 | /how-to-publish | Monthly |
| 0.6 | /blog, /blog/*, /faq | Weekly/Monthly |
| 0.5 | /about, /contact | Monthly |
| 0.3 | /terms, /privacy, /refund-policy | Monthly |
| N/A | /dashboard/*, /auth/*, /unsubscribe | noindex |

---

## Page Count Projection

| Page Type | Current | Month 3 | Month 6 | Month 12 |
|-----------|---------|---------|---------|----------|
| Static pages | 14 | 14 | 14 | 14 |
| Skill pages | 51 | 65 | 100 | 200 |
| Blog posts | 3 | 12 | 25 | 50 |
| Agent pages | 0 | 5 | 8 | 15 |
| Category pages | 0 | 5 | 8 | 12 |
| Comparison pages | 0 | 3 | 6 | 10 |
| Guide pages | 0 | 1 | 4 | 8 |
| User profiles | 5 | 10 | 25 | 50 |
| **Total** | **73** | **115** | **190** | **359** |
