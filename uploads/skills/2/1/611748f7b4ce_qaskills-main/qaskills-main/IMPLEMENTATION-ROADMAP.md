# Implementation Roadmap — QASkills.sh SEO

> Generated: February 14, 2026
> Estimated Effort: 4 phases over 12 months

---

## Phase 1 — Technical Foundation (Weeks 1-2)

> Goal: Fix all technical SEO gaps. Zero new content, pure infrastructure.

### Week 1: Critical Fixes

| # | Task | File(s) | Priority | Est. Time |
|---|------|---------|----------|-----------|
| 1.1 | Add `viewport` export to root layout | `layout.tsx` | Critical | 15 min |
| 1.2 | Add `icons` metadata (favicon, apple-touch-icon) | `layout.tsx` | Critical | 30 min |
| 1.3 | Add `themeColor` metadata | `layout.tsx` | Critical | 5 min |
| 1.4 | Add Google Search Console verification meta | `layout.tsx` | Critical | 5 min |
| 1.5 | Add Bing Webmaster Tools verification meta | `layout.tsx` | Critical | 5 min |
| 1.6 | Add `preconnect` hints for external resources | `layout.tsx` | High | 15 min |
| 1.7 | Add skip-to-main-content link (accessibility) | `layout.tsx` | Medium | 10 min |
| 1.8 | Create `generateBreadcrumbJsonLd()` function | `json-ld.ts` | Critical | 30 min |
| 1.9 | Add BreadcrumbList to skill detail pages | `skills/[author]/[slug]/page.tsx` | Critical | 15 min |
| 1.10 | Add BreadcrumbList to blog post pages | `blog/[slug]/page.tsx` | Critical | 15 min |

### Week 2: Schema & Sitemap

| # | Task | File(s) | Priority | Est. Time |
|---|------|---------|----------|-----------|
| 2.1 | Remove or update FAQPage schema | `faq/page.tsx` | High | 15 min |
| 2.2 | Add `logo` and `founder` to Organization schema | `json-ld.ts` | High | 15 min |
| 2.3 | Add `dateModified`, `image` to BlogPosting schema | `json-ld.ts` | Medium | 15 min |
| 2.4 | Add user profile pages to sitemap | `sitemap.ts` | Medium | 30 min |
| 2.5 | Use actual blog publish dates in sitemap | `sitemap.ts` | Medium | 15 min |
| 2.6 | Add explicit canonical URLs to pages with query params | Various | Medium | 30 min |
| 2.7 | Create `/llms.txt` API route | `app/llms.txt/route.ts` | High | 30 min |
| 2.8 | Add AI crawler directives to robots.txt | `robots.ts` | High | 15 min |
| 2.9 | Verify all pages have proper metadata exports | Various | Medium | 1 hr |

**Phase 1 Deliverables:**
- All technical SEO issues resolved
- BreadcrumbList schema on all detail pages
- AI search readiness (llms.txt, crawler directives)
- Verification tags for GSC and Bing
- Clean sitemap with proper dates

---

## Phase 2 — Content Expansion (Weeks 3-8)

> Goal: Create high-value landing pages and start content marketing.

### Weeks 3-4: Programmatic Pages

| # | Task | Priority | Est. Time |
|---|------|----------|-----------|
| 3.1 | Create agent landing page template component | Critical | 2 hrs |
| 3.2 | Create `/agents/claude-code` page | Critical | 1 hr |
| 3.3 | Create `/agents/cursor` page | Critical | 1 hr |
| 3.4 | Create `/agents/copilot` page | High | 1 hr |
| 3.5 | Create `/agents/windsurf` page | High | 45 min |
| 3.6 | Create `/agents/cline` page | High | 45 min |
| 3.7 | Create category landing page template | Critical | 2 hrs |
| 3.8 | Create `/categories/e2e-testing` page | Critical | 1 hr |
| 3.9 | Create `/categories/unit-testing` page | Critical | 1 hr |
| 3.10 | Create `/categories/api-testing` page | High | 1 hr |
| 3.11 | Create `/categories/performance-testing` page | High | 45 min |
| 3.12 | Create `/categories/accessibility-testing` page | Medium | 45 min |
| 3.13 | Add all new pages to sitemap | Critical | 30 min |
| 3.14 | Add internal links from skill pages to agent/category pages | High | 1 hr |

### Weeks 5-6: Comparison & Blog Content

| # | Task | Priority | Est. Time |
|---|------|----------|-----------|
| 4.1 | Create comparison page template | Critical | 2 hrs |
| 4.2 | Write: QASkills vs SkillsMP | High | 3 hrs |
| 4.3 | Write: Playwright vs Cypress Skills for AI | High | 3 hrs |
| 4.4 | Write blog: 5 Must-Have QA Skills for Claude Code | High | 2 hrs |
| 4.5 | Write blog: How AI Agents Are Changing QA Testing | Medium | 2 hrs |
| 4.6 | Add schema markup to comparison pages | High | 30 min |

### Weeks 7-8: Guides & Internal Linking

| # | Task | Priority | Est. Time |
|---|------|----------|-----------|
| 5.1 | Write guide: Complete Playwright E2E Guide for AI | High | 4 hrs |
| 5.2 | Implement "Related Skills" component for skill pages | High | 2 hrs |
| 5.3 | Add cross-linking between agents, categories, and skills | High | 2 hrs |
| 5.4 | Write blog: TDD with AI Agents | Medium | 2 hrs |
| 5.5 | Write blog: API Testing with AI Skills | Medium | 2 hrs |

**Phase 2 Deliverables:**
- 5 agent landing pages
- 5 category landing pages
- 2 comparison pages
- 4 new blog posts
- 1 deep guide
- Internal linking framework

---

## Phase 3 — Scale & Authority (Weeks 9-24)

> Goal: Build content moat and establish authority.

### Monthly Recurring Tasks
| Task | Frequency | Owner |
|------|-----------|-------|
| Publish 4 blog posts | Monthly | Content |
| Publish 1 deep guide | Monthly | Content |
| Update comparison pages | Quarterly | Content |
| Monitor Core Web Vitals | Monthly | Engineering |
| Check keyword rankings | Weekly | SEO |
| Review and update existing content | Quarterly | Content |

### Key Milestones

**Month 3 (Week 12)**
- 20+ total blog posts published
- 2 deep guides published
- 3+ comparison pages live
- Target: 50% organic traffic increase

**Month 4 (Week 16)**
- Begin outreach for backlinks
- Guest post on TestGuild or Ministry of Testing
- Submit to "best QA tools" roundup articles
- Target: 15 keywords in top 10

**Month 6 (Week 24)**
- 30+ blog posts published
- 4+ guides published
- Publish "State of AI Testing 2026" report
- Target: 150% organic traffic increase, 50 keywords in top 10

---

## Phase 4 — Authority & Dominance (Months 7-12)

> Goal: Become THE authority for QA + AI agents.

| Initiative | Timeline | Expected Impact |
|-----------|----------|-----------------|
| Publish annual "State of AI Testing" report | Month 7 | High — linkable asset, media coverage |
| Launch QA Skills certification/badges | Month 8 | Medium — community engagement |
| Create video content (YouTube integration) | Month 9 | High — leverage 189K subscriber base |
| Build glossary of QA + AI terms | Month 10 | Medium — programmatic SEO, 50+ pages |
| Launch community showcase (user stories) | Month 11 | Medium — UGC content, E-E-A-T |
| Expand to new agent integrations | Ongoing | High — capture emerging agents |

---

## Resource Requirements

### Engineering (Weeks 1-8, then maintenance)
- Technical SEO fixes: 1 developer, ~2 days
- Programmatic pages (agents, categories): 1 developer, ~5 days
- Templates and components: 1 developer, ~3 days
- Ongoing maintenance: ~2 hrs/week

### Content (Ongoing from Week 3)
- Blog posts: 4-8 hrs/month (2-4 posts)
- Guides: 4-6 hrs/month (1 guide)
- Comparison pages: 3-4 hrs each (quarterly updates)
- Content review: 2 hrs/month

### SEO (Ongoing)
- Keyword research: 2 hrs/month
- Ranking monitoring: 1 hr/week
- Competitor analysis: 2 hrs/month
- Technical audits: 2 hrs/quarter

---

## Success Criteria

| Phase | Timeline | Key Metric | Target |
|-------|----------|-----------|--------|
| Phase 1 | Week 2 | Technical SEO score | 90+ (Lighthouse) |
| Phase 2 | Week 8 | Indexed pages | 120+ |
| Phase 3 | Month 6 | Organic traffic | +150% from baseline |
| Phase 4 | Month 12 | Top-10 keywords | 150+ |
