# Research: RoboBook Docusaurus Technical Stack

**Feature**: 001-robobook-docusaurus
**Date**: 2025-12-13
**Status**: Complete
**Related ADR**: ADR-0001

## Overview

This document consolidates research findings for technical decisions needed to implement the RoboBook Docusaurus documentation website. All decisions align with the feature specification and clarified requirements.

## 1. Docusaurus 3.x Setup & Configuration

**Decision**: Use Docusaurus 3.7+ with Classic preset

**Rationale**:
- React 19 support (latest as of 2025)
- Mature plugin ecosystem for documentation sites
- Built-in dark mode, mobile responsiveness, search integration
- Strong community support (40k+ GitHub stars, Meta-backed)
- Aligns with monorepo structure requirement

**Alternatives Considered**:
- VuePress 2.x: Smaller ecosystem, less active development
- MkDocs Material: Python-based, doesn't align with React/TypeScript stack
- GitBook: Commercial pricing, vendor lock-in concerns

**Implementation Notes**:
- Initialize with `npx create-docusaurus@latest robobook classic --typescript`
- Configure `docusaurus.config.ts` for GitHub Pages deployment
- Use Classic preset (includes docs plugin, blog plugin, pages plugin)
- Enable TypeScript for type safety in custom components

## 2. Custom Theming Strategy

**Decision**: CSS Variables override approach using Infima framework

**Rationale**:
- Minimal code changes (no React component overrides needed)
- Easy maintenance (all customization in `src/css/custom.css`)
- Predictable cascade (CSS variables override Infima defaults)
- Performance (no additional JavaScript bundles)

**Alternatives Considered**:
- Swizzling (ejecting) components: High maintenance, breaks on Docusaurus updates
- Custom theme plugin: Overkill for color/typography changes
- Styled Components: Adds bundle size, runtime overhead

**Implementation Notes**:
```css
/* src/css/custom.css */
:root {
  --ifm-color-primary: #00d4ff;
  --ifm-color-primary-dark: #0ea5e9;
  --ifm-background-color: #0f1729;
  --ifm-background-surface-color: #1a1f3a;
  --ifm-heading-font-size-h1: 3.5rem;
  --ifm-heading-font-size-h2: 2.5rem;
  --ifm-heading-font-size-h3: 1.75rem;
  --ifm-font-size-base: 1rem;
  --ifm-spacing-horizontal: 8px; /* Base 8px grid */
}
```

## 3. Asset Management Strategy

**Decision**: Git for <500KB assets, Git LFS for >500KB, GitHub Pages CDN

**Rationale**:
- Git: Simple workflow, no additional setup for small assets
- Git LFS: Efficient handling of large diagrams/images without bloating repo
- GitHub Pages: Free CDN with global edge locations, no external service needed
- Cost: $0 (within GitHub free tier limits)

**Alternatives Considered**:
- Cloudflare CDN: Added complexity, external dependency
- AWS S3 + CloudFront: Overkill for static assets, monthly costs
- All Git (no LFS): Would bloat repository over time

**Implementation Notes**:
- Configure `.gitattributes`: `*.png filter=lfs diff=lfs merge=lfs -text`
- GitHub free tier: 1GB storage, 1GB/month bandwidth (sufficient for educational site)
- Lazy-load images with `@docusaurus/plugin-ideal-image`
- Optimize images before commit (<500KB target)

## 4. Search Integration

**Decision**: Algolia DocSearch (primary) + @easyops-cn/docusaurus-search-local (fallback)

**Rationale**:
- Algolia DocSearch: Free for open-source docs, self-service onboarding (Oct 2025 update), <1s query time
- Local search: Zero-cost fallback if Algolia rejects application, works offline
- Dual strategy: Ensures search functionality regardless of external approval

**Alternatives Considered**:
- Typesense Cloud: Requires paid plan, no free tier for docs
- Algolia only: Risk of no search if application rejected
- Local only: Slower indexing, no cloud-powered relevance

**Implementation Notes**:
- Apply to Algolia DocSearch via https://docsearch.algolia.com/apply
- Configure `docusaurus.config.ts` with Algolia app ID + API key
- Install local search plugin as fallback: `npm install @easyops-cn/docusaurus-search-local`
- Local search only works in production builds (`npm run build` + `npm run serve`)

## 5. Deployment Pipeline

**Decision**: GitHub Actions → GitHub Pages with automated build optimization

**Rationale**:
- GitHub Actions: Free for public repos, 2000 minutes/month (sufficient for <5 min builds)
- GitHub Pages: Free hosting, custom domain support, HTTPS by default
- Automated: Push to main triggers build and deploy
- Performance: Build caching reduces build time to <3 minutes

**Alternatives Considered**:
- Vercel: Vendor lock-in, commercial platform (though free tier exists)
- Netlify: Similar concerns, less alignment with GitHub-native workflow
- Manual deployment: Error-prone, slows iteration

**Implementation Notes**:
- Create `.github/workflows/deploy.yml` for automated deployment
- Use `actions/cache@v4` for Node.js dependencies caching
- Deploy to `gh-pages` branch for GitHub Pages
- Configure `organizationName` and `projectName` in `docusaurus.config.ts`
- Enable GitHub Pages in repository settings (source: gh-pages branch)

## 6. Syntax Highlighting Configuration

**Decision**: Prism.js with custom RoboBook theme for Python, C++, YAML, XML

**Rationale**:
- Prism.js: Built into Docusaurus, zero additional setup
- Theme customization: CSS variables enable RoboBook color matching
- Language support: All required languages included by default
- Performance: Lightweight, client-side highlighting

**Alternatives Considered**:
- Highlight.js: Not default in Docusaurus, additional bundle size
- Shiki: Server-side only, doesn't work with Docusaurus client rendering
- Monaco Editor: Overkill for code snippets (designed for full IDE experience)

**Implementation Notes**:
```typescript
// docusaurus.config.ts
const config: Config = {
  themeConfig: {
    prism: {
      theme: prismThemes.vsDark, // Base theme
      additionalLanguages: ['python', 'cpp', 'yaml', 'xml'],
    },
  },
};
```
Customize colors in `src/css/custom.css`:
```css
.token.keyword { color: #00d4ff; } /* RoboBook cyan */
.token.string { color: #0ea5e9; } /* RoboBook cyan dark */
```

## 7. Mermaid Diagram Integration

**Decision**: @docusaurus/theme-mermaid with RoboBook-styled themes

**Rationale**:
- Official plugin: Maintained by Docusaurus core team
- Markdown support: Render diagrams directly in `.md` files
- Themeable: Supports custom color schemes matching RoboBook
- Performance: Lazy-loaded, doesn't impact initial page load

**Alternatives Considered**:
- Mermaid.js standalone: Requires custom integration, no SSR support
- Embedded images: Loses interactivity, harder to maintain
- PlantUML: Separate rendering pipeline, more complex workflow

**Implementation Notes**:
```typescript
// docusaurus.config.ts
themes: ['@docusaurus/theme-mermaid'],
markdown: {
  mermaid: true,
},
```
Configure theme colors:
```typescript
themeConfig: {
  mermaid: {
    theme: {
      dark: {
        primaryColor: '#00d4ff',
        primaryTextColor: '#ffffff',
        primaryBorderColor: '#0ea5e9',
        lineColor: '#00d4ff',
        secondaryColor: '#1a1f3a',
        tertiaryColor: '#0f1729',
      },
    },
  },
},
```
Known limitation: `fontSize` doesn't work for flowcharts (Mermaid upstream issue).

## 8. Analytics & Feedback

**Decision**: Google Analytics 4 via @docusaurus/plugin-google-gtag + PushFeedback widget

**Rationale**:
- GA4: Industry standard, free tier, privacy controls, educational exemptions
- Official plugin: Simple configuration, no custom code
- PushFeedback: Open-source widget, customizable, no vendor lock-in
- Privacy: GA4 anonymize IP by default (GDPR compliant)

**Alternatives Considered**:
- Plausible Analytics: Requires paid plan, no free tier
- Matomo: Self-hosted complexity, server maintenance overhead
- No analytics: Miss insights into user behavior and content effectiveness

**Implementation Notes**:
```typescript
// docusaurus.config.ts
plugins: [
  [
    '@docusaurus/plugin-google-gtag',
    {
      trackingID: 'G-XXXXXXXXXX',
      anonymizeIP: true,
    },
  ],
],
```
Feedback widget:
```bash
npm install @pushfeedback/react
```
Add to layout component with RoboBook styling.

## 9. Internationalization (i18n) Readiness

**Decision**: File-system structure prepared for Urdu translation, implementation deferred

**Rationale**:
- i18n plugin: Built into Docusaurus, zero additional dependencies
- File-system approach: Scalable, maintainable, version-controlled
- Deferred implementation: Avoids premature complexity, structure in place for bonus feature
- Cost of retrofitting: High (requires renaming/moving all existing docs)

**Alternatives Considered**:
- Implement immediately: Adds complexity before MVP, delays launch
- External translation service: Ongoing costs, less control over quality
- Never support i18n: Misses bonus feature opportunity (50 points)

**Implementation Notes**:
```typescript
// docusaurus.config.ts (prepared structure)
i18n: {
  defaultLocale: 'en',
  locales: ['en', 'ur'], // Urdu ready for bonus implementation
  path: 'i18n',
  localeConfigs: {
    en: { label: 'English' },
    ur: { label: 'اردو', direction: 'rtl' }, // Right-to-left for Urdu
  },
},
```
File structure:
```
i18n/
├── en/ (default, docs live here initially)
└── ur/ (Urdu translations, bonus feature)
    └── docusaurus-plugin-content-docs/
        └── current/
            └── module1/
                └── chapter1.md (translated)
```

## 10. PWA / Offline Access

**Decision**: Configure @docusaurus/plugin-pwa, defer offline functionality

**Rationale**:
- PWA plugin: Official, well-maintained, production-ready
- Deferred offline: Not in MVP scope, adds complexity to caching strategy
- Manifest prepared: Enables future "Add to Home Screen" on mobile
- Performance: No runtime cost if offline not activated

**Alternatives Considered**:
- Implement immediately: Caching logic for ROS 2 code examples complex, delays MVP
- Never support offline: Misses opportunity for field use cases (robotics labs without WiFi)
- Workbox custom: More control, significantly more implementation effort

**Implementation Notes**:
```typescript
// docusaurus.config.ts (prepared structure)
plugins: [
  [
    '@docusaurus/plugin-pwa',
    {
      offlineModeActivationStrategies: ['appInstalled', 'standalone', 'queryString'],
      pwaHead: [
        {
          tagName: 'link',
          rel: 'icon',
          href: '/img/robobook-logo.png',
        },
        {
          tagName: 'link',
          rel: 'manifest',
          href: '/manifest.json',
        },
        {
          tagName: 'meta',
          name: 'theme-color',
          content: '#0f1729', // RoboBook dark navy
        },
      ],
    },
  ],
],
```
Create `static/manifest.json`:
```json
{
  "name": "RoboBook - Physical AI Textbook",
  "short_name": "RoboBook",
  "theme_color": "#0f1729",
  "background_color": "#0f1729",
  "display": "standalone",
  "scope": "/",
  "start_url": "/",
  "icons": [
    {
      "src": "/img/robobook-icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/img/robobook-icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

## Cross-Cutting Decisions

### Monorepo Structure

**Decision**: Single repository with organized subdirectories

```
phyai-humanoid-textbook/
├── docs/                    # Docusaurus content
│   ├── module1/
│   ├── module2/
│   ├── module3/
│   ├── module4/
│   └── supporting/
├── examples/                # Code examples (tested in Docker)
│   ├── module1/
│   ├── module2/
│   ├── module3/
│   └── module4/
├── static/                  # Static assets
│   ├── img/
│   └── diagrams/
├── src/                     # Custom React components
│   ├── components/
│   ├── css/
│   └── pages/
├── .github/                 # CI/CD workflows
│   └── workflows/
├── .gitattributes           # Git LFS configuration
├── docusaurus.config.ts     # Main configuration
├── sidebars.ts              # Navigation structure
└── package.json             # Dependencies
```

### Docker Testing Environment

**Decision**: Dockerfile for ROS 2 Humble + Ubuntu 22.04 in `/examples`

**Rationale**:
- Reproducibility: Same environment for all learners
- Cross-platform: Works on Windows, macOS, Linux
- Isolation: No conflicts with host system
- Testing: CI can verify examples in same container

**Implementation**:
```dockerfile
# examples/Dockerfile
FROM osrf/ros:humble-desktop-full-jammy
WORKDIR /workspace
COPY . .
RUN apt-get update && apt-get install -y python3-pip
# Additional dependencies as needed
```

## Summary of Technical Stack

| Category | Technology | Version | Rationale |
|----------|-----------|---------|-----------|
| Framework | Docusaurus | 3.7+ | React 19, mature ecosystem |
| Language | TypeScript | 5.x | Type safety, tooling |
| Styling | CSS Variables | - | Infima override, simple |
| Search | Algolia DocSearch | - | Free, <1s queries |
| Search Fallback | easyops local search | - | Zero-cost, offline |
| Deployment | GitHub Actions | - | Free, automated |
| Hosting | GitHub Pages | - | Free, HTTPS, CDN |
| Syntax Highlighting | Prism.js | Built-in | Lightweight, themeable |
| Diagrams | Mermaid.js | Via plugin | Official, Markdown-native |
| Analytics | Google Analytics 4 | - | Free, GDPR-compliant |
| Feedback | PushFeedback | OSS | Customizable, no lock-in |
| i18n | Docusaurus i18n | Built-in | File-system, scalable |
| PWA | Docusaurus PWA | Built-in | Manifest ready, offline deferred |
| Asset Storage | Git + Git LFS | - | <500KB Git, >500KB LFS |
| Testing | Docker | - | ROS 2 Humble + Ubuntu 22.04 |

## Implementation Readiness Checklist

- [x] All 10 research areas completed
- [x] Decisions documented with rationale
- [x] Alternatives evaluated
- [x] Implementation notes provided
- [x] No "NEEDS CLARIFICATION" markers remain
- [x] Aligns with constitution principles (Educational Excellence, Technical Rigor, AI-Native Architecture)
- [x] Supports clarified requirements (Docker testing, monorepo, progressive depth, typography/spacing)

## Next Steps

1. Create `data-model.md` for content entities (Module, Chapter, Code Example, etc.)
2. Generate `contracts/` for deployment pipeline and build validation
3. Create `quickstart.md` with setup instructions
4. Complete `plan.md` with all research findings
5. Proceed to `/sp.tasks` for task breakdown

## References

- Docusaurus Documentation: https://docusaurus.io
- ADR-0001: RoboBook Docusaurus Technical Stack
- Feature Specification: `specs/001-robobook-docusaurus/spec.md`
- Clarifications: Session 2025-12-13
- Constitution: `.specify/memory/constitution.md`
