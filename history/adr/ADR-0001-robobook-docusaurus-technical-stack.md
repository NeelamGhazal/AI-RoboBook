# ADR-0001: RoboBook Docusaurus Technical Stack and Architecture

- **Status:** Proposed
- **Date:** 2025-12-15
- **Feature:** 001-robobook-docusaurus
- **Context:** Physical AI & Humanoid Robotics textbook requiring modern documentation platform with RoboBook visual identity (dark navy #0f1729, cyan accents #00d4ff), comprehensive syntax highlighting, search, and deployment automation

## Decision

Adopt Docusaurus 3.x Classic Preset with the following technical stack:

**Core Platform:**
- Framework: Docusaurus 3.7+ (React 19 compatible, Classic preset)
- Styling: CSS Variables + Custom CSS (Infima framework override)
- Deployment: GitHub Actions + GitHub Pages
- Search: Algolia DocSearch (primary) with @easyops-cn/docusaurus-search-local fallback

**Content Enhancement:**
- Syntax Highlighting: Prism.js with custom theme (Python, C++, YAML, XML support)
- Diagrams: @docusaurus/theme-mermaid plugin
- Analytics: @docusaurus/plugin-google-gtag (GA4)
- Feedback: Third-party widget (PushFeedback or custom implementation)

**Asset Management:**
- Images <500KB: Standard Git (monorepo docs/ structure)
- Images >500KB: Git LFS with 100MB default threshold
- CDN: GitHub Pages built-in CDN (no external CDN initially)

**Future Readiness:**
- i18n: File-system-based structure prepared (defer implementation)
- PWA: @docusaurus/plugin-pwa available (defer offline capability)

## Rationale

### 1. Docusaurus 3.x Setup

**DECISION:** Use Docusaurus 3.7+ with Classic preset, React 19 support

**RATIONALE:**
- Latest stable version (3.7) includes React 19 compatibility for modern React features
- Classic preset bundles documentation, blog, and theme plugins together for immediate productivity
- Strong community support and active development (Meta-maintained)
- Built-in dark mode support aligns with RoboBook visual identity requirements
- Production-ready with SSR/SSG optimization for <5 second load times

**ALTERNATIVES CONSIDERED:**
- VuePress: Rejected due to smaller community and less robust plugin ecosystem
- MkDocs Material: Rejected because Python-based doesn't align with React/TypeScript preference
- GitBook: Rejected due to commercial pricing and less customization flexibility

**IMPLEMENTATION NOTES:**
- Initialize with `npx create-docusaurus@latest` within monorepo folder
- Configure `docusaurus.config.js` with preset-classic options
- Use React 19 by default for new sites (existing sites can stay on React 18)
- New @docusaurus/plugin-svgr extracted for SVG handling flexibility

### 2. Custom Theming Approach

**DECISION:** Override Infima CSS variables in `src/css/custom.css` for RoboBook visual identity

**RATIONALE:**
- CSS variables provide centralized theming without modifying core files
- Ensures clean upgrades to future Docusaurus versions
- Supports light/dark mode via `data-theme` attributes
- Variables control colors, spacing, fonts - all customization needs
- Docusaurus color palette tool generates 7 shades for consistency

**ALTERNATIVES CONSIDERED:**
- Component swizzling for theme modifications: Rejected due to maintenance complexity during upgrades
- Separate custom theme package: Rejected as over-engineering for single-site use
- Tailwind CSS integration: Rejected to avoid conflicts with Infima framework

**IMPLEMENTATION NOTES:**
- Define CSS variables in `:root` for light mode, `html[data-theme="dark"]` for dark mode
- Use Docusaurus color palette tool for primary color shades (#00d4ff cyan accents)
- Override Infima variables (--ifm-* prefix) for colors, layout, typography
- Override Docusaurus variables (--docusaurus-* prefix) for component-specific styling
- Target stable class names for additional custom CSS
- Typography sizing: H1: 3.5rem, H2: 2.5rem, H3: 1.75rem, Body: 1rem
- Spacing: 8px grid system (8, 16, 24, 32, 48, 64)
- Dark navy backgrounds: #0f1729, #1a1f3a
- Cyan accents: #00d4ff, #0ea5e9
- Ensure WCAG-AA contrast ratio for accessibility

### 3. Asset Management Strategy

**DECISION:** Use standard Git for images <500KB, Git LFS for images >500KB

**RATIONALE:**
- Git LFS reduces repository bloat for large binaries while maintaining version control
- 500KB threshold balances convenience (small images in Git) with performance (large images in LFS)
- GitHub allows Git LFS files up to 2GB per file
- Aligns with pre-commit-hooks default for large file checks
- Documentation sites typically have many small diagrams (<500KB) and few large images

**ALTERNATIVES CONSIDERED:**
- All images in Git: Rejected due to repository bloat concerns for images >500KB
- All images in Git LFS: Rejected due to unnecessary complexity for small diagrams
- External CDN (Cloudflare, imgix): Rejected due to added cost and complexity; GitHub Pages CDN sufficient
- Self-hosted image server: Rejected due to deployment/maintenance overhead

**IMPLEMENTATION NOTES:**
- Configure `.gitattributes` with LFS rules for PNG/JPG/GIF >500KB
- Store images in `static/img/` directory structure
- Organize by module: `static/img/module1/`, `static/img/module2/`, etc.
- Use descriptive filenames: `ros2-node-graph.png`, not `img001.png`
- Optimize images before commit (compress PNGs with pngquant, JPGs with mozjpeg)
- Document image guidelines in contributing docs
- GitHub Pages provides automatic CDN distribution

### 4. Search Integration

**DECISION:** Primary - Algolia DocSearch (free tier), Fallback - @easyops-cn/docusaurus-search-local

**RATIONALE:**
- Algolia DocSearch now offers self-service onboarding (October 2025 update)
- Automated validation in minutes vs. 1-2 business days for manual review
- Free for technical documentation and blogs (open to all, not just open-source)
- Includes AskAI generative AI layer for enhanced search
- Fallback ensures search functionality regardless of Algolia approval status

**ALTERNATIVES CONSIDERED:**
- @cmfcmf/docusaurus-search-local: Considered but @easyops-cn version has better styling match to Algolia
- gabrielcsapo/docusaurus-plugin-search-local: Rejected due to less active maintenance
- Paid search services (Typesense, Meilisearch): Rejected due to cost constraints

**IMPLEMENTATION NOTES:**
- Apply to Algolia DocSearch via dashboard at https://docsearch.algolia.com/
- If approved: Configure `algolia` object in `themeConfig` with appId, apiKey, indexName
- If rejected: Install @easyops-cn/docusaurus-search-local
  - Note: Search only works in production build (`npm run build` + `npm run serve`)
  - Search indexing occurs during build, not in dev mode
- Local search plugin styling matches Algolia aesthetics
- Configure language support (English primary, Urdu future)
- Add search page for comprehensive results

### 5. Deployment Pipeline

**DECISION:** GitHub Actions workflow for automated GitHub Pages deployment with <5 minute builds

**RATIONALE:**
- Native GitHub integration eliminates external service dependencies
- GitHub Pages now uses GitHub Actions instead of legacy "Deploy from a branch"
- Free hosting for public repositories
- Automatic HTTPS with github.io domain
- Built-in CDN for global distribution

**ALTERNATIVES CONSIDERED:**
- Vercel: Rejected to avoid vendor lock-in; GitHub Pages sufficient for documentation
- Netlify: Rejected for same reasons as Vercel
- AWS S3 + CloudFront: Rejected due to cost and configuration complexity
- Self-hosted: Rejected due to infrastructure maintenance burden

**IMPLEMENTATION NOTES:**
- Create `.github/workflows/deploy.yml` workflow file
- Use `actions/checkout@v4` for repository checkout
- Use `actions/setup-node@v4` for Node.js setup (specify version: 20.x)
- Cache dependencies with `actions/cache@v4` (cache: npm, cache-dependency-path: package-lock.json)
- Install: `npm ci` (faster than `npm install`, uses lock file)
- Build: `npm run build` (generates static site in `build/` directory)
- Deploy: `actions/deploy-pages@v4` or `peaceiris/actions-gh-pages@v4`
- Enable GitHub Pages in repository settings: Settings → Pages → Source: GitHub Actions
- Build optimization strategies:
  - Cache node_modules and build artifacts
  - Use `npm ci` for reproducible builds
  - Parallelize builds if multiple documentation sections exist (not needed initially)
  - Monitor build time; implement incremental builds if exceeding 5 minutes
- Trigger on push to main branch and manual workflow_dispatch
- Set NODE_ENV=production for optimized builds
- Configure base URL in `docusaurus.config.js`: `url: 'https://username.github.io', baseUrl: '/repo-name/'`

### 6. Syntax Highlighting

**DECISION:** Prism.js (built-in) with custom RoboBook theme colors for Python, C++, YAML, XML

**RATIONALE:**
- Prism.js included by default in Docusaurus (zero configuration for common languages)
- Python, C++, Bash already included in default language set
- YAML included in default set (robotics configuration files)
- Extensive theme options with customization for RoboBook colors
- High performance with code splitting

**ALTERNATIVES CONSIDERED:**
- Shiki: Rejected due to larger bundle size and slower build times
- highlight.js: Rejected because Prism.js is Docusaurus default with better integration

**IMPLEMENTATION NOTES:**
- Configure in `docusaurus.config.js` under `themeConfig.prism`:
  ```javascript
  const lightCodeTheme = require('prism-react-renderer/themes/vsDark');
  const darkCodeTheme = require('prism-react-renderer/themes/dracula');

  prism: {
    theme: lightCodeTheme,
    darkTheme: darkCodeTheme,
    additionalLanguages: ['bash', 'python', 'cpp', 'yaml', 'xml'],
  }
  ```
- Default languages already included: JavaScript, C++, Bash, Python, SQL
- Available built-in themes: dracula, duotoneDark, duotoneLight, github, nightOwl, nightOwlLight, oceanicNext, okaidia, palenight, shadesofPurple, synthwave84, ultramin, vsDark, vsLight
- Custom theme colors for RoboBook:
  - Create custom theme in `src/theme/prism-theme.js`
  - Override token colors to match cyan accents (#00d4ff, #0ea5e9)
  - Maintain dark navy backgrounds (#0f1729, #1a1f3a)
- For additional languages not in Prism defaults: swizzle `prism-include-languages`
- Test with code blocks using triple backticks: ```python, ```cpp, ```yaml, ```xml

### 7. Mermaid Diagram Integration

**DECISION:** Use @docusaurus/theme-mermaid plugin with custom styling for RoboBook visual identity

**RATIONALE:**
- Official Docusaurus plugin for seamless integration
- Supports flowcharts, sequence diagrams, class diagrams, state diagrams
- Essential for robotics architecture diagrams (ROS 2 node graphs, system architectures)
- Inline diagram definition keeps documentation source-controlled
- Configurable theming for dark/light mode consistency

**ALTERNATIVES CONSIDERED:**
- mdx-mermaid: Rejected because official plugin provides better maintenance
- Pre-rendered images: Rejected due to versioning complexity and lack of source control
- PlantUML: Rejected due to Java dependency and server requirements
- Draw.io integration: Rejected because binary format doesn't align with text-based workflow

**IMPLEMENTATION NOTES:**
- Enable in `docusaurus.config.js`:
  ```javascript
  export default {
    markdown: {
      mermaid: true,
    },
    themes: ['@docusaurus/theme-mermaid'],
  };
  ```
- Configure Mermaid options:
  ```javascript
  themeConfig: {
    mermaid: {
      theme: {light: 'neutral', dark: 'dark'},
      options: {
        themeVariables: {
          primaryColor: '#00d4ff',
          primaryTextColor: '#ffffff',
          primaryBorderColor: '#0ea5e9',
          lineColor: '#00d4ff',
          secondaryColor: '#1a1f3a',
          tertiaryColor: '#0f1729',
        },
      },
    },
  }
  ```
- Known limitations:
  - `fontSize` doesn't work for flowcharts (Mermaid limitation, not Docusaurus)
  - Per-diagram styling requires inline init directives (repetitive)
  - CSS modifications may not work due to Mermaid rendering approach
- Alternative: Swizzle Mermaid renderer component for advanced customization
- Use init directives for per-diagram customization:
  ```mermaid
  %%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#00d4ff'}}}%%
  graph TD
    A[ROS 2 Node] --> B[Topic]
  ```
- Test diagrams in both light and dark modes
- Consider separate configs for light/dark if theming issues arise

### 8. Analytics & Feedback

**DECISION:** Google Analytics 4 via @docusaurus/plugin-google-gtag + Third-party feedback widget (PushFeedback or custom)

**RATIONALE:**
- GA4 is current standard (Universal Analytics sunset July 2024)
- plugin-google-gtag recommended over deprecated plugin-google-analytics
- No official built-in feedback widget; third-party solutions mature and cost-effective
- PushFeedback specifically designed for documentation sites
- Custom implementation possible via swizzle if needed

**ALTERNATIVES CONSIDERED:**
- Universal Analytics: Rejected because sunset as of July 1, 2024
- Self-hosted analytics (Plausible, Matomo): Rejected due to hosting/cost overhead
- Happy React feedback widget: Alternative to PushFeedback with similar features
- Feedback Rocket: Alternative with nav integration
- No analytics: Rejected because usage insights valuable for content improvement

**IMPLEMENTATION NOTES:**
- Install @docusaurus/plugin-google-gtag (NOT plugin-google-analytics)
- Configure in `docusaurus.config.js`:
  ```javascript
  plugins: [
    [
      '@docusaurus/plugin-google-gtag',
      {
        trackingID: 'G-XXXXXXXXXX',
        anonymizeIP: true,
      },
    ],
  ]
  ```
- Create GA4 property in Google Analytics
- For feedback widget:
  - Option 1 (PushFeedback): Follow https://docs.pushfeedback.com/installation/docusaurus
  - Option 2 (Feedback Rocket): Integrates in top nav for any-page feedback
  - Option 3 (Custom): Use swizzle to add feedback button component
  - Option 4 (Happy React): Analytics-integrated feedback widget
- Consider React-Native approach: Use GA4 events to report feedback widget interactions
- Add feedback button to page bottom or floating widget
- Collect: helpful/not helpful, page-specific comments, optional email
- Store feedback in simple backend (Neon Serverless Postgres) or third-party service

### 9. Internationalization Approach

**DECISION:** Structure for i18n plugin readiness, defer Urdu translation implementation to bonus phase

**RATIONALE:**
- i18n support is architectural decision requiring upfront file structure
- File-system-based approach (i18n/[locale]/ directories) must be planned early
- Urdu translation is bonus feature (50 points), not core requirement
- Proper structure now avoids costly refactoring later
- Self-service onboarding for documentation sites via i18n plugin

**ALTERNATIVES CONSIDERED:**
- No i18n preparation: Rejected because retroactive i18n extremely difficult
- Separate config per locale: Rejected as over-engineering for single additional language
- External translation service integration: Rejected due to cost and machine-translation quality concerns

**IMPLEMENTATION NOTES:**
- Configure i18n in `docusaurus.config.js` (even if only English initially):
  ```javascript
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur'],
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
      },
      ur: {
        label: 'اردو',
        direction: 'rtl',
      },
    },
  }
  ```
- File structure (prepare directories):
  - Default content: `docs/`, `blog/`, `src/pages/`
  - Urdu translations: `i18n/ur/docusaurus-plugin-content-docs/current/`
  - Theme translations: `i18n/ur/docusaurus-theme-classic/`
  - Code labels: `i18n/ur/code.json`
- Generate translation files: `npm run write-translations -- --locale ur`
- For React components:
  - Use `<Translate>` component for JSX content
  - Use `translate()` function for string values (placeholders, aria-labels)
- Testing:
  - Dev mode: `npm run start -- --locale ur` (test specific locale)
  - Build: `npm run build` (builds all locales)
  - Cannot test all locales simultaneously in dev mode
- Build independently if needed: `docusaurus build --locale ur`
- Urdu translation guidelines (bonus implementation):
  - NO machine translation gibberish
  - Use technical translation by domain experts
  - Maintain code blocks in English
  - Ensure RTL rendering correct (bidirectional text)
  - Test with Arabic/Urdu speakers
- Consider translation button at chapter start (bonus feature)

### 10. PWA/Offline Access

**DECISION:** Structure for @docusaurus/plugin-pwa, defer offline capability to future phase

**RATIONALE:**
- PWA capability not critical for initial launch (documentation sites typically online)
- Plugin available and easy to enable when needed
- Service worker generation requires production-only build
- Offline precaching downloads all static assets (bandwidth intensive)
- Better to validate core content first, then add PWA as enhancement

**ALTERNATIVES CONSIDERED:**
- Immediate PWA implementation: Rejected because offline capability not in core requirements
- No PWA support: Rejected because future enhancement valuable for learners in low-connectivity areas
- Custom service worker: Rejected because plugin handles complexity

**IMPLEMENTATION NOTES:**
- When implementing (future):
  - Install: `npm install @docusaurus/plugin-pwa`
  - Create PWA manifest: `static/manifest.json`
    ```json
    {
      "name": "RoboBook - Physical AI & Humanoid Robotics",
      "short_name": "RoboBook",
      "theme_color": "#00d4ff",
      "background_color": "#0f1729",
      "display": "standalone",
      "start_url": "/",
      "icons": [
        {
          "src": "img/icon-192.png",
          "sizes": "192x192",
          "type": "image/png"
        },
        {
          "src": "img/icon-512.png",
          "sizes": "512x512",
          "type": "image/png"
        }
      ]
    }
    ```
  - Configure plugin:
    ```javascript
    plugins: [
      [
        '@docusaurus/plugin-pwa',
        {
          offlineModeActivationStrategies: ['mobile', 'saveData'],
          pwaHead: [
            {
              tagName: 'link',
              rel: 'icon',
              href: '/img/icon.png',
            },
            {
              tagName: 'link',
              rel: 'manifest',
              href: '/manifest.json',
            },
            {
              tagName: 'meta',
              name: 'theme-color',
              content: '#00d4ff',
            },
          ],
        },
      ],
    ]
    ```
- Service worker only generated in production build (`npm run build`)
- Reload popup shows when new service worker available
- Activation strategies:
  - `standalone`: Users running as installed app
  - `mobile`: Width <= 996px
  - `saveData`: Users with `navigator.connection.saveData === true`
  - `queryString`: Activates if `?offlineMode=true`
- Workbox customization available for advanced caching rules
- HTTPS required for service workers (GitHub Pages provides)
- Test offline mode:
  1. Build: `npm run build`
  2. Serve: `npm run serve`
  3. Open DevTools → Application → Service Workers
  4. Check "Offline" and reload
- Consider bandwidth implications before enabling for all users

## Consequences

### Positive

1. **Rapid Development**: Docusaurus Classic preset provides immediate productivity with zero configuration
2. **Modern Stack**: React 19, latest tooling, active Meta maintenance
3. **Cost-Effective**: GitHub Pages hosting free, Algolia DocSearch free for technical docs
4. **Customization Balance**: CSS variables allow RoboBook branding without sacrificing upgrade path
5. **Performance**: SSR/SSG optimization delivers <5 second load times
6. **Search Quality**: Algolia provides best-in-class search; local fallback ensures functionality
7. **Community Support**: Large Docusaurus community, extensive plugin ecosystem
8. **Future-Proof**: i18n and PWA ready when needed
9. **Developer Experience**: Hot reload, TypeScript support, modern React patterns
10. **Integrated Analytics**: GA4 + feedback widgets provide comprehensive usage insights
11. **Asset Management**: Git LFS balances version control with performance
12. **Syntax Highlighting**: Prism.js covers all robotics languages (Python, C++, YAML, XML)
13. **Diagram Support**: Mermaid enables architecture diagrams in source control

### Negative

1. **GitHub Dependency**: GitHub Pages hosting ties deployment to GitHub (mitigated: easy migration to Vercel/Netlify)
2. **Build Complexity**: Multiple build steps for production (npm ci → build → deploy)
3. **Search Limitations**: Local search only works in production builds, not dev mode
4. **Algolia Approval**: DocSearch approval not guaranteed (mitigated: local search fallback)
5. **Learning Curve**: Docusaurus configuration, React components, MDX syntax
6. **Git LFS Setup**: Requires Git LFS client installation for contributors
7. **Mermaid Styling**: Limited customization options, fontSize issues in flowcharts
8. **PWA Bandwidth**: Offline precaching downloads all assets (deferred to future)
9. **i18n Complexity**: File-system-based translation requires careful file organization
10. **Plugin Maintenance**: Third-party plugins (Mermaid, local search) require monitoring for updates
11. **Theme Lock-in**: Infima framework customization doesn't transfer to other platforms
12. **React Framework**: Team must know React (mitigated: documentation-focused, minimal custom components)

## Alternatives Considered

### Alternative Stack A: VuePress + Vue 3 + GitHub Pages
- **Framework**: VuePress 2.x
- **Styling**: Custom CSS + Vue components
- **Deployment**: GitHub Actions
- **Why Rejected**: Smaller community, less plugin ecosystem, slower development velocity, Meta backing matters for long-term support

### Alternative Stack B: MkDocs Material + Python + ReadTheDocs
- **Framework**: MkDocs Material theme
- **Styling**: Material Design components
- **Deployment**: ReadTheDocs hosting
- **Why Rejected**: Python-based doesn't align with React/TypeScript preference, less customization flexibility for RoboBook visual identity, ReadTheDocs hosting less control than GitHub Pages

### Alternative Stack C: GitBook + Cloud Hosting
- **Framework**: GitBook platform
- **Styling**: GitBook themes
- **Deployment**: GitBook cloud
- **Why Rejected**: Commercial pricing model, limited customization, vendor lock-in, less control over deployment pipeline

### Alternative Search: Typesense Cloud
- **Why Rejected**: Requires paid plan for production, self-hosting complexity, Algolia free tier covers needs, local search fallback sufficient

### Alternative Asset Management: Cloudflare CDN
- **Why Rejected**: Added complexity, external service dependency, GitHub Pages CDN sufficient for documentation site traffic patterns

## Implementation Checklist

### Phase 1: Core Setup (Week 1)
- [ ] Initialize Docusaurus 3.7+ with Classic preset
- [ ] Configure RoboBook visual identity (CSS variables, dark/light mode)
- [ ] Set up monorepo structure (docs/ + code examples)
- [ ] Configure Git LFS for images >500KB
- [ ] Create GitHub Actions deployment workflow
- [ ] Configure GitHub Pages hosting
- [ ] Test build time (<5 minutes target)

### Phase 2: Content Enhancement (Week 2)
- [ ] Configure Prism.js syntax highlighting (Python, C++, YAML, XML)
- [ ] Customize code theme for RoboBook colors
- [ ] Install and configure @docusaurus/theme-mermaid
- [ ] Style Mermaid diagrams for RoboBook identity
- [ ] Test diagram rendering in light/dark modes
- [ ] Verify responsive design (desktop, tablet, mobile)

### Phase 3: Search & Analytics (Week 3)
- [ ] Apply to Algolia DocSearch program
- [ ] Configure @easyops-cn/docusaurus-search-local as fallback
- [ ] Install @docusaurus/plugin-google-gtag
- [ ] Create GA4 property and configure tracking
- [ ] Integrate feedback widget (PushFeedback or custom)
- [ ] Test search functionality in production build

### Phase 4: Future Readiness (Week 4)
- [ ] Configure i18n structure (en/ur locales)
- [ ] Prepare translation directories
- [ ] Document i18n workflow for Urdu translation (bonus)
- [ ] Create PWA manifest and icons
- [ ] Document PWA activation strategy (deferred)
- [ ] Performance audit (Lighthouse score >90)

### Phase 5: Documentation & Testing (Ongoing)
- [ ] Create contribution guidelines (image optimization, LFS usage)
- [ ] Document build/deployment process
- [ ] Test deployment workflow end-to-end
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Mobile responsiveness testing
- [ ] Accessibility audit (WCAG AA compliance)

## References

- Docusaurus Documentation: https://docusaurus.io/docs
- Docusaurus 3.7 Release (React 19): https://www.x-cmd.com/blog/250108/
- Algolia DocSearch Program: https://docsearch.algolia.com/docs/docsearch-program/
- Git LFS Documentation: https://git-lfs.com/
- Prism.js Themes: https://github.com/PrismJS/prism-themes
- Mermaid Diagram Syntax: https://mermaid.js.org/
- Feature Spec: /mnt/e/phyai-humanoid-textbook/specs/001-robobook-docusaurus/spec.md
- Constitution: /mnt/e/phyai-humanoid-textbook/.specify/memory/constitution.md
- Related Skills: robobook-docusaurus-architect, robobook-docusaurus-ui

## Sources

### Docusaurus Setup & Configuration
- [Configuration | Docusaurus](https://docusaurus.io/docs/configuration)
- [@docusaurus/preset-classic - npm](https://www.npmjs.com/package/@docusaurus/preset-classic)
- [Docusaurus 3.7 Released, Compatible with React 19](https://www.x-cmd.com/blog/250108/)
- [Using Docusaurus to Build A Modern Documentation Website - Semaphore](https://semaphore.io/blog/docusaurus)

### Custom Theming
- [Styling and Layout | Docusaurus](https://docusaurus.io/docs/styling-layout)
- [CSS Variables | Docusaurus.community](https://docusaurus.community/knowledge/design/css/variables/)
- [What's the best approach to customize styles in Docusaurus? - GitHub Discussion](https://github.com/facebook/docusaurus/discussions/5003)

### Asset Management
- [Git Large File Storage](https://git-lfs.com/)
- [Git LFS - Atlassian Tutorial](https://www.atlassian.com/git/tutorials/git-lfs)

### Search Integration
- [DocSearch program | DocSearch by Algolia](https://docsearch.algolia.com/docs/docsearch-program/)
- [Algolia DocSearch is now free for all docs sites](https://www.algolia.com/blog/product/algolia-docsearch-is-now-free-for-all-docs-sites)
- [Algolia Unveils Self-Service Onboarding](https://www.algolia.com/about/news/algolia-unveils-a-new-era-for-documentation-search-with-self-service-onboarding-and-askai)
- [@easyops-cn/docusaurus-search-local - GitHub](https://github.com/easyops-cn/docusaurus-search-local)
- [Search | Docusaurus](https://docusaurus.io/docs/search)

### Deployment
- [Deployment | Docusaurus](https://docusaurus.io/docs/deployment)
- [GitHub Pages Docusaurus - LayZeeDK](https://github.com/LayZeeDK/github-pages-docusaurus)
- [Using Github Actions & Pages - Vergil's Blog](https://vergilwang15.github.io/blog/devs-log/auto-deploy-website/)

### Syntax Highlighting
- [Syntax Highlighting in Docusaurus – The DAX Shepherd](https://thedaxshepherd.com/2023/01/31/docusaurus-syntax-highlighting/)
- [Code blocks | Docusaurus](https://docusaurus.io/docs/markdown-features/code-blocks)
- [PrismJS - GitHub](https://github.com/PrismJS/prism)

### Mermaid Diagrams
- [Diagrams | Docusaurus](https://docusaurus.io/docs/next/markdown-features/diagrams)
- [Tweaking the CSS of Mermaid.js flowcharts - GitHub Discussion](https://github.com/facebook/docusaurus/discussions/8806)
- [Support separate config for mermaid dark mode - GitHub Issue](https://github.com/facebook/docusaurus/issues/10251)

### Analytics & Feedback
- [plugin-google-gtag | Docusaurus](https://docusaurus.io/docs/api/plugins/@docusaurus/plugin-google-gtag)
- [Google Analytics 4 - GitHub Issue](https://github.com/facebook/docusaurus/issues/7221)
- [Feedback widget in Docusaurus – Happy React](https://happyreact.com/blog/feedback-widget-in-docusaurus)
- [Create a feedback widget using Docusaurus | Feedback Rocket](https://www.feedbackrocket.io/integration-guides/docusaurus)

### Internationalization
- [i18n - Introduction | Docusaurus](https://docusaurus.io/docs/i18n/introduction)
- [Implementing Internationalization in Docusaurus - Medium](https://chanmeng666.medium.com/implementing-internationalization-in-a-docusaurus-website-experience-and-lessons-learned-b05139e33876)
- [Adding i18n for a Docusaurus Site - SQYBI.com](https://sqybi.com/en-US/blog/adding-i18n-for-a-docusaurus-site/)

### PWA Support
- [plugin-pwa | Docusaurus](https://docusaurus.io/docs/api/plugins/@docusaurus/plugin-pwa)
- [Progressive Web App Tutorial 2025 - Markaicode](https://markaicode.com/progressive-web-app-tutorial-2025-service-worker-offline/)

### Monorepo Structure
- [Installation | Docusaurus](https://docusaurus.io/docs/next/installation)
- [Support monorepos with multiple docs plugins - GitHub Issue](https://github.com/facebook/docusaurus/issues/4085)
- [Cross-repo documentation - GitHub Discussion](https://github.com/facebook/docusaurus/discussions/6086)
