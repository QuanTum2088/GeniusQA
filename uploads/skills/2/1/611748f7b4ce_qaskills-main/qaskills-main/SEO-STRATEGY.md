# QASkills.sh — SEO Strategy 2026

> Generated: February 14, 2026
> Business Type: SaaS / Developer Tool Directory (QA Testing Niche)
> Current Status: 73 indexed pages, 48 skills, 3 blog posts

---

## 1. Executive Summary

QASkills.sh is the only AI agent skills directory focused exclusively on QA testing — a defensible niche in a rapidly growing market (SkillsMP: 66K+ skills, ClawHub: 3K+). The site has solid technical SEO foundations (proper metadata, OG tags, JSON-LD, sitemap) but significant growth opportunities in content marketing, comparison pages, AI search readiness, and technical polish.

**Key Strengths:**
- Strong E-E-A-T: The Testing Academy (189K+ YouTube subscribers), author Pramod Dutta
- QA-only niche = less competition than general agent skills marketplaces
- 48 skills with quality scores, install counts — strong programmatic SEO base
- Free & open source positioning
- Good JSON-LD implementation (WebSite, Organization, SoftwareApplication, BlogPosting)

**Critical Gaps:**
- Only 3 blog posts — minimal content marketing footprint
- No comparison/alternative pages (highest-converting SaaS content type: 4-7% CVR)
- No AI crawler optimization (llms.txt, AI bot directives)
- Missing BreadcrumbList schema across all pages
- No integration/agent-specific landing pages
- FAQPage schema still used (restricted by Google since Aug 2023)
- Limited internal linking strategy

---

## 2. Target Audience & Search Intent

### Primary Audiences
| Segment | Search Behavior | Content Needs |
|---------|----------------|---------------|
| QA Engineers using AI agents | "playwright skills for Claude Code", "AI testing automation" | How-to guides, skill comparisons |
| Developers new to AI coding | "best skills for Cursor", "Claude Code setup" | Getting started guides, curated lists |
| QA Managers evaluating tools | "AI QA tools comparison 2026", "test automation skills" | ROI content, case studies |
| Skill publishers | "how to publish AI agent skill", "SKILL.md format" | Publishing docs, contributor guides |

### High-Value Keyword Clusters

**Cluster 1: Agent + QA Skills (Transactional)**
- "Claude Code testing skills" (low comp, high intent)
- "Cursor QA plugins" / "Copilot testing extensions"
- "AI agent playwright skills" / "AI agent cypress skills"
- "best QA skills for AI coding agents"

**Cluster 2: Framework + Testing (Informational → Transactional)**
- "playwright e2e testing best practices 2026"
- "cypress vs playwright for AI agents"
- "jest unit testing with AI agents"
- "automated API testing with AI"

**Cluster 3: Competitor/Alternative (High CVR)**
- "SkillsMP alternatives for QA"
- "QASkills vs SkillsMP"
- "best AI testing skills directory"
- "free AI agent skills for testing"

**Cluster 4: AI Search / GEO (Emerging)**
- "QA automation tools for AI agents"
- "AI coding agent test automation"
- "install testing skills Claude Code"

---

## 3. Competitive Analysis

### Direct Competitors

| Competitor | Skills Count | Focus | Strengths | Weaknesses |
|-----------|-------------|-------|-----------|------------|
| **SkillsMP** | 66,541 | General SDLC | Scale, broad coverage, enterprise features | Generic — no QA focus, overwhelming catalog |
| **ClawHub** | 3,000+ | General | 15K daily installs, fast growing | No niche specialization |
| **Skills.sh** | Unknown | Open directory | Open ecosystem | Lacks curation, quality signals |
| **Smithery.ai** | Unknown | MCP + Skills | Strong developer community | Not QA-specific |
| **Vercel agent-skills** | ~10 | React/Next.js | Brand authority, Vercel backing | Very narrow focus (React only) |

### QASkills.sh Competitive Advantages
1. **Only QA-focused directory** — unique positioning in a crowded general market
2. **Quality scoring system** — curated, not just aggregated
3. **The Testing Academy brand** — 189K YouTube subscribers, established E-E-A-T
4. **Multi-agent support** — 30+ AI agents vs competitors' narrower support
5. **Free & open source** — lower barrier than premium competitors

### Content Gap Opportunities vs Competitors
- **Comparison pages**: No competitor has QA-focused comparison content
- **Framework guides**: Deep Playwright/Cypress/Jest content tied to skills
- **Agent-specific landing pages**: "QA Skills for Claude Code" etc.
- **Testing type guides**: "E2E Testing with AI", "API Testing with AI"

---

## 4. Site Architecture (Current vs Recommended)

### Current Architecture (Good Foundation)
```
/
├── /skills (directory + search)
│   └── /skills/[author]/[slug] (48 skill pages)
├── /leaderboard
├── /packs (skill bundles)
├── /getting-started
├── /blog (3 posts)
│   └── /blog/[slug]
├── /users/[username]
├── /pricing, /about, /contact, /faq
├── /how-to-publish
├── /terms, /privacy, /refund-policy
└── /dashboard (noindex — correct)
```

### Recommended Architecture (Phase 2-3 additions)
```
/
├── /skills (existing)
│   └── /skills/[author]/[slug]
├── /agents (NEW — agent-specific landing pages)
│   ├── /agents/claude-code
│   ├── /agents/cursor
│   ├── /agents/copilot
│   ├── /agents/windsurf
│   └── /agents/[agent-slug]
├── /categories (NEW — testing type landing pages)
│   ├── /categories/e2e-testing
│   ├── /categories/unit-testing
│   ├── /categories/api-testing
│   ├── /categories/performance-testing
│   └── /categories/[category-slug]
├── /compare (NEW — comparison pages)
│   ├── /compare/qaskills-vs-skillsmp
│   ├── /compare/playwright-vs-cypress-skills
│   └── /compare/[slug]
├── /guides (NEW — deep educational content)
│   ├── /guides/playwright-e2e-complete-guide
│   ├── /guides/ai-agent-qa-setup
│   └── /guides/[slug]
├── /blog (expand to 2-4 posts/month)
│   └── /blog/[slug]
├── /leaderboard, /packs (existing)
├── /getting-started, /how-to-publish (existing)
├── /pricing, /about, /contact, /faq (existing)
└── /llms.txt (NEW — AI search readiness)
```

---

## 5. Technical SEO Fixes (Priority Order)

### Critical (Week 1)

#### 5.1 Add Missing `<head>` Elements
**File:** `packages/web/src/app/layout.tsx`

Missing from root layout:
- `viewport` export (Next.js 15 best practice)
- `icons` configuration (favicon, apple-touch-icon)
- `themeColor` for mobile browsers
- Preconnect hints for external resources
- Verification meta tags (Google Search Console, Bing Webmaster)

#### 5.2 Add BreadcrumbList Schema
**File:** `packages/web/src/lib/json-ld.ts`

No BreadcrumbList schema exists. Should be added to:
- Every skill detail page: Home → Skills → [Skill Name]
- Every blog post: Home → Blog → [Post Title]
- Every category page (when created): Home → Categories → [Category]
- Every agent page (when created): Home → Agents → [Agent Name]

#### 5.3 Fix FAQPage Schema
**File:** `packages/web/src/app/faq/page.tsx`

Google restricted FAQPage rich results to government and healthcare sites (Aug 2023). Current inline FAQPage schema won't generate rich results. Options:
- Remove FAQPage schema entirely (cleanest)
- Keep for AI search parsability but don't expect SERP features

#### 5.4 Add Canonical URLs
Each page should have explicit canonical URL in metadata. Currently relying on `metadataBase` but explicit canonicals prevent duplicate content issues, especially for filtered/paginated views.

### High (Week 2)

#### 5.5 AI Search Readiness
- Create `/llms.txt` endpoint describing what QASkills.sh is, its content structure, and API
- Add AI crawler directives in robots.txt (GPTBot, ClaudeBot, PerplexityBot)
- Ensure all skill descriptions are structured as quotable passages

#### 5.6 Sitemap Enhancements
**File:** `packages/web/src/app/sitemap.ts`

Currently missing from sitemap:
- Blog post individual pages with actual dates (uses `new Date()` instead of publish dates)
- User profile pages
- Future: agent pages, category pages, comparison pages

#### 5.7 Internal Linking Strategy
- Each skill page should link to related skills (same framework, testing type)
- Blog posts should link to relevant skill pages
- Getting Started should link to top skills
- Each skill should show its categories with links

### Medium (Weeks 3-4)

#### 5.8 Structured Data Enhancements
- Add `dateModified` to BlogPosting schema
- Add `image` to BlogPosting schema
- Add `logo` to Organization schema
- Add `founder` to Organization schema (Pramod Dutta)
- Add `SoftwareSourceCode` schema for skills with GitHub URLs

#### 5.9 Performance Optimization
- Add `preconnect` hints for Clerk, Datafast, Typesense
- Lazy-load below-fold images
- Ensure dynamic OG image generation is fast (<200ms)

---

## 6. Content Strategy

### Content Pillars

| Pillar | Purpose | Target Keywords | Content Types |
|--------|---------|----------------|---------------|
| **AI Agent QA Skills** | Core product content | "QA skills for [agent]" | Agent landing pages, skill comparisons |
| **Testing Best Practices** | Educational SEO | "[framework] testing guide" | Deep guides, tutorials |
| **AI in Testing** | Thought leadership | "AI test automation 2026" | Blog posts, trend reports |
| **Tool Comparisons** | High-conversion content | "[tool] vs [tool]" | Comparison pages |

### Content Priorities (by Funnel Stage)

**Bottom of Funnel (BoFU) — Create First**
1. Agent-specific landing pages (5 pages): `/agents/claude-code`, `/agents/cursor`, etc.
2. Comparison pages (3 pages): vs SkillsMP, Playwright vs Cypress skills
3. Category landing pages (5 pages): e2e, unit, api, performance, accessibility

**Middle of Funnel (MoFU)**
4. Framework-specific guides: "Complete Playwright E2E Guide with AI Skills"
5. Use case guides: "Setting Up QA Automation with AI Agents"
6. Case studies / success stories

**Top of Funnel (ToFU)**
7. Blog posts: Industry trends, AI testing news, framework comparisons
8. Glossary: QA testing terms for AI agents
9. "State of AI Testing" annual report

### Publishing Cadence
- **Blog**: 2-4 posts per month (currently at 3 total — need to ramp up)
- **Guides**: 1 per month (deep, 2000+ word content)
- **Comparison pages**: 2 in first month, then 1 per quarter
- **Agent/category pages**: All 10 in first month (programmatic)

---

## 7. E-E-A-T Strategy

### Experience
- Showcase Pramod Dutta's hands-on QA experience on /about
- Add "Used by X developers" social proof on homepage
- Include real install counts and quality scores (already doing this)

### Expertise
- Author bio on every blog post with credentials
- Link to The Testing Academy YouTube (189K subscribers)
- Publish original research / testing benchmarks
- Feature skill author expertise on skill pages

### Authoritativeness
- Build backlinks from QA/testing community sites
- Contribute to testing-related open source projects
- Seek mentions in "best QA tools" roundup articles
- Guest posts on TestGuild, Ministry of Testing, etc.

### Trustworthiness
- SSL: Active (already)
- Privacy policy, terms of service: Present (already)
- Clear pricing (free): Present (already)
- Transparent quality scoring methodology (add to /about or /faq)
- Contact page with real channels: Present (already)

---

## 8. Generative Engine Optimization (GEO)

### AI Search Readiness Checklist
- [ ] Create `/llms.txt` — machine-readable site description
- [ ] Structure skill descriptions as quotable passages (complete sentences, factual, self-contained)
- [ ] Add clear attribution signals ("QASkills.sh, a product by The Testing Academy")
- [ ] Ensure SoftwareApplication schema has complete feature lists
- [ ] Publish original data that AI systems cite (install counts, quality scores, comparisons)
- [ ] Add `data-nosnippet` to non-essential UI text to guide AI extraction
- [ ] Monitor citations in Google AI Overviews, ChatGPT web search, Perplexity

### Content Formatting for AI Citability
- Use clear H2/H3 headings that match search queries
- Include bullet-point summaries at top of long-form content
- Use comparison tables with structured data
- Add "key takeaways" sections to blog posts
- Ensure each page has a single, clear topic focus

---

## 9. KPI Targets

| Metric | Current (Feb 2026) | 3 Month Target | 6 Month Target | 12 Month Target |
|--------|-------------------|----------------|----------------|-----------------|
| Indexed Pages | 73 | 120 | 200 | 350 |
| Organic Traffic (monthly) | Baseline TBD | +50% | +150% | +400% |
| Keyword Rankings (top 10) | Baseline TBD | 15 keywords | 50 keywords | 150 keywords |
| Blog Posts | 3 | 12 | 25 | 50 |
| Skills Listed | 48 | 65 | 100 | 200 |
| Backlinks | Baseline TBD | +20 | +60 | +150 |
| Core Web Vitals | TBD (audit needed) | All green | All green | All green |
| AI Search Citations | 0 (assumed) | 5 | 20 | 50 |

---

## 10. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| SkillsMP dominates with 66K skills | High | Double down on QA niche, quality over quantity |
| Google algorithm update impacts rankings | Medium | Diversify traffic sources (AI search, YouTube, social) |
| AI search reduces click-through | Medium | Optimize for citations, build direct brand recognition |
| Competitor launches QA-specific directory | High | First-mover advantage, build community, publish content moat |
| Content quality dilution from scale | Medium | Maintain quality scoring, editorial review for guides |

---

## 11. Tools & Tracking

### Required Setup
- [ ] Google Search Console (verification meta tag needed)
- [ ] Bing Webmaster Tools (verification meta tag needed)
- [ ] Google Analytics 4 or existing Datafast analytics
- [ ] Schema markup testing (Google Rich Results Test)
- [ ] Core Web Vitals monitoring (PageSpeed Insights)
- [ ] AI citation monitoring (manual: search for "qaskills" on ChatGPT, Perplexity)

### Recommended Tools
- Ahrefs or Semrush for keyword tracking and backlink monitoring
- Screaming Frog for technical SEO crawls
- Google Trends for keyword research
- AnswerThePublic for content ideation

---

## Quick Reference: Immediate Actions

### This Week
1. Add viewport export, icons, themeColor to `layout.tsx`
2. Add BreadcrumbList schema to `json-ld.ts`
3. Remove or update FAQPage schema
4. Add Google/Bing verification meta tags
5. Create `/llms.txt` endpoint

### This Month
6. Create 5 agent-specific landing pages (`/agents/[agent]`)
7. Create 5 category landing pages (`/categories/[type]`)
8. Write 2 comparison pages
9. Publish 4 new blog posts
10. Add AI crawler directives to robots.txt
