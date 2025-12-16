---
name: "robobook-docusaurus-architect"
description: "Ensure Docusaurus architecture correctness and stability: proper file structure (docs/, blog/, src/pages/), docusaurus.config.js setup, plugin configuration, SSR/SSG compatibility, sidebars.js, routing, build optimization, and long-term maintainability. Focuses ONLY on architecture, configuration, and build logic. Use when user needs Docusaurus setup, troubleshooting build errors, plugin integration, or structural decisions. Does NOT handle CSS styling or visual design."
version: "1.1.0"
---

# RoboBook Docusaurus Architect Skill

## When to Use This Skill

- User asks to "set up Docusaurus" or "initialize documentation site"
- User has build errors or configuration issues
- User needs plugin integration or routing setup
- User asks about file structure or project organization
- User mentions sidebars, navigation structure, or docs organization
- User needs performance optimization or build configuration
- **Does NOT handle**: CSS styling, colors, hover effects, or visual design

## Core Architecture Responsibilities

This skill handles the **technical foundation** of Docusaurus:

1. **File Structure Setup**
2. **Configuration Files** (docusaurus.config.js, sidebars.js)
3. **Plugin Integration**
4. **Build Process & SSR/SSG**
5. **Routing & Navigation**
6. **Performance Optimization**
7. **Asset Management**

## Proper Docusaurus File Structure

```
robobook-docs/
├── docs/                          # Documentation pages
│   ├── introduction.md
│   ├── getting-started.md
│   ├── fundamentals/
│   │   ├── sensors.md
│   │   ├── actuators.md
│   │   └── control-systems.md
│   └── advanced-topics/
│       ├── ai-integration.md
│       └── computer-vision.md
├── blog/                          # Blog posts
│   ├── 2024-12-01-welcome.md
│   └── authors.yml
├── src/
│   ├── components/                # Custom React components
│   │   ├── HomepageFeatures/
│   │   ├── CustomCard/
│   │   └── Hero/                  # Hero section component
│   ├── pages/                     # Custom pages
│   │   ├── index.js              # Landing page with hero
│   │   └── about.md
│   └── css/
│       └── custom.css            # UI skill handles this
├── static/                        # Static assets
│   ├── img/
│   │   ├── robobook-logo.svg    # USER'S LOGO (stacked layers icon)
│   │   ├── humanoid-robot.jpg   # Hero section robot image
│   │   ├── robotics-arm-1.jpg   # USER'S IMAGES
│   │   └── favicon.ico
│   └── files/
├── docusaurus.config.js          # Main configuration
├── sidebars.js                   # Sidebar structure
├── package.json
└── README.md
```

## Critical Configuration Files

### 1. docusaurus.config.js (Complete Setup)

```javascript
// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'RoboBook',
  tagline: 'Physical AI & Humanoid Robotics',
  url: 'https://your-domain.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',

  // GitHub pages deployment config
  organizationName: 'your-org', // Usually your GitHub org/user name
  projectName: 'robobook-docs', // Usually your repo name

  // Internationalization (i18n) - English and Urdu support
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur'], // English / اردو
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Edit this page link
          editUrl: 'https://github.com/your-org/robobook-docs/tree/main/',
          // Show last update author and time
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/your-org/robobook-docs/tree/main/',
          blogSidebarTitle: 'All posts',
          blogSidebarCount: 'ALL',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
        // Optional: Google Analytics
        gtag: {
          trackingID: 'G-XXXXXXXXXX',
          anonymizeIP: true,
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // IMPORTANT: Dark mode configuration
      colorMode: {
        defaultMode: 'dark',
        disableSwitch: false, // Allow users to toggle
        respectPrefersColorScheme: false,
      },

      // Navbar configuration - UPDATED STRUCTURE
      navbar: {
        title: 'RoboBook',
        logo: {
          alt: 'RoboBook Logo',
          src: 'img/robobook-logo.png', // USER'S LOGO (stacked layers icon)
          srcDark: 'img/robobook-logo.png', // Same for dark mode
        },
        items: [
          // LEFT SIDE
          {
            type: 'doc',
            docId: 'introduction',
            position: 'left',
            label: 'Book', // Opens book content on click
          },
          
          // RIGHT SIDE
          {
            type: 'search',
            position: 'right',
          },
          {
            label: 'Sign In',
            position: 'right',
            href: '#', // Update with actual auth URL
          },
          {
            label: 'Sign Up',
            position: 'right',
            href: '#', // Update with actual auth URL
            className: 'navbar-signup-button', // For special styling by UI skill
          },
          {
            type: 'localeDropdown',
            position: 'right',
            dropdownItemsAfter: [
              {
                label: 'English',
                lang: 'en',
              },
              {
                label: 'اردو',
                lang: 'ur',
              },
            ],
          },
          {
            type: 'html',
            position: 'right',
            value: '<button class="theme-toggle-button" aria-label="Toggle theme"></button>', // Theme toggle
          },
        ],
      },

      // Footer configuration
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Quick Links',
            items: [
              {
                label: 'Documentation',
                to: '/docs/introduction',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/your-org/robobook-docs',
              },
              {
                label: 'Community',
                href: '#',
              },
            ],
          },
          {
            title: 'Connect',
            items: [
              {
                label: 'Discord',
                href: 'https://discord.gg/your-invite',
              },
              {
                label: 'Twitter',
                href: 'https://twitter.com/your-handle',
              },
              {
                label: 'YouTube',
                href: 'https://youtube.com/@your-channel',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Blog',
                to: '/blog',
              },
            ],
          },
        ],
        copyright: `© ${new Date().getFullYear()} RoboBook. Built with Docusaurus. Open-source and free forever.`,
      },

      // Code block theme
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['python', 'cpp', 'java', 'bash'],
      },

      // Search configuration (Algolia)
      algolia: {
        appId: 'YOUR_APP_ID',
        apiKey: 'YOUR_SEARCH_API_KEY',
        indexName: 'robobook',
        contextualSearch: true,
      },
    }),

  // Plugins
  plugins: [
    // Add custom plugins here
  ],
};

module.exports = config;
```

### 2. sidebars.js (Documentation Structure)

```javascript
/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation
 */

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // Main documentation sidebar
  docsSidebar: [
    {
      type: 'category',
      label: 'Introduction',
      items: ['introduction', 'overview', 'getting-started'],
    },
    {
      type: 'category',
      label: 'Fundamentals',
      collapsed: false,
      items: [
        'fundamentals/sensors',
        'fundamentals/actuators',
        'fundamentals/control-systems',
        'fundamentals/kinematics',
      ],
    },
    {
      type: 'category',
      label: 'ROS 2 Integration',
      collapsed: true,
      items: [
        'ros2/architecture',
        'ros2/communication',
        'ros2/packages',
      ],
    },
    {
      type: 'category',
      label: 'Advanced Vision Systems',
      collapsed: true,
      items: [
        'vision/computer-vision',
        'vision/depth-sensing',
        'vision/object-detection',
        'vision/visual-slam',
      ],
    },
    {
      type: 'category',
      label: 'Large Language Models',
      collapsed: true,
      items: [
        'llm/integration',
        'llm/nlp',
        'llm/human-robot-interaction',
      ],
    },
    {
      type: 'category',
      label: 'Reinforcement Learning',
      collapsed: true,
      items: [
        'rl/fundamentals',
        'rl/algorithms',
        'rl/simulation',
        'rl/training',
      ],
    },
    {
      type: 'category',
      label: 'Real-World Projects',
      collapsed: true,
      items: [
        'projects/line-follower',
        'projects/robotic-arm',
        'projects/autonomous-drone',
        'projects/humanoid-robot',
      ],
    },
  ],
};

module.exports = sidebars;
```

### 3. Landing Page Structure (src/pages/index.js)

The landing page should include these sections in order:

1. **Hero Section**
   - Robot image on LEFT
   - Text content on RIGHT:
     - Heading: "Physical AI & Humanoid Robotics"
     - Paragraph: "Learn to control physical androids using ROS 2, advanced vision systems, large language models, and reinforcement learning with this free, open-source textbook."
     - Button: "Start Learning" (scrolls to book content section)

2. **What's Inside Section**
   - Small text above heading: "What's Inside the Book"
   - Main heading: "What's Inside the Book"
   - Paragraph: "Everything you need to master robotics from fundamentals to advanced applications"
   - 3-4 feature cards with icons:
     - ROS 2 Integration
     - Advanced Vision Systems
     - Large Language Models
     - Reinforcement Learning

3. **CTA Section**
   - Small text above heading: "Start Your Journey Today"
   - Main heading: "Ready to Start Your Robotics Journey?"
   - Paragraph: "Access comprehensive documentation, interactive examples, and step-by-step guides to master robotics concepts and build amazing projects."
   - Button: "Start Learning Now"

4. **Book Content Section** (Target of scroll navigation)
   - Top buttons:
     - "Personalized Mode"
     - "English / اردو" (Language toggle)
   - Book chapter cards with content structure

### 4. package.json (Dependencies)

```json
{
  "name": "robobook-docs",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "docusaurus": "docusaurus",
    "start": "docusaurus start",
    "build": "docusaurus build",
    "swizzle": "docusaurus swizzle",
    "deploy": "docusaurus deploy",
    "clear": "docusaurus clear",
    "serve": "docusaurus serve",
    "write-translations": "docusaurus write-translations",
    "write-heading-ids": "docusaurus write-heading-ids"
  },
  "dependencies": {
    "@docusaurus/core": "^3.0.0",
    "@docusaurus/preset-classic": "^3.0.0",
    "@mdx-js/react": "^3.0.0",
    "clsx": "^2.0.0",
    "prism-react-renderer": "^2.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@docusaurus/module-type-aliases": "^3.0.0",
    "@docusaurus/types": "^3.0.0"
  },
  "engines": {
    "node": ">=18.0"
  }
}
```

## Asset Management Rules

### Static Assets Directory Structure

```
static/
├── img/
│   ├── robobook-logo.svg          # REQUIRED: Stacked layers icon (user's logo)
│   ├── humanoid-robot.jpg         # REQUIRED: Hero section robot image
│   ├── robotics-icon-1.svg        # Feature card icons
│   ├── robotics-icon-2.svg
│   ├── robotics-icon-3.svg
│   ├── robotics-icon-4.svg
│   ├── favicon.ico
│   └── og-image.png               # For social media sharing
├── files/
│   └── sample-code.zip            # Downloadable files
└── fonts/                         # Custom fonts if needed
```

### CRITICAL: NO Default Docusaurus Assets

**NEVER include:**
- ❌ Docusaurus dinosaur logo
- ❌ Default placeholder images
- ❌ Default blue theme colors (handled by UI skill)

**ALWAYS verify:**
- ✅ User's stacked layers icon logo is in `static/img/`
- ✅ Humanoid robot image for hero section
- ✅ Feature card icons (ROS 2, Vision, LLM, RL)
- ✅ Custom favicon is provided
- ✅ All image paths in config point to user's assets

## Navbar Structure Requirements

### Left Side (in order):
1. **Logo + Brand Name**
   - Stacked layers icon (robobook-logo.svg)
   - "RoboBook" text next to icon
2. **Book Button**
   - Text: "Book"
   - Action: Scroll to book content section or navigate to /docs

### Right Side (in order):
1. **Search Bar**
   - Search functionality for documentation
2. **Sign In Button**
   - Link to authentication page
3. **Sign Up Button**
   - Link to registration page
   - Special styling class for UI skill
4. **Language Toggle**
   - "English / اردو" dropdown
5. **Theme Toggle**
   - Light/Dark mode switch button

## Documentation Page Requirements

### Top Bar Buttons (on all docs pages)
Located at the top of the documentation content area:

1. **Personalized Mode Button**
   - Icon: Document/file icon
   - Text: "Personalized Mode"
   - Functionality: Enable personalized learning experience

2. **Language Toggle Button**
   - Icon: Translation/language icon
   - Text: "English / اردو"
   - Functionality: Switch between English and Urdu

These buttons should appear:
- Above the main documentation content
- Below the navbar
- Centered or right-aligned
- With proper spacing from content

## Build Process & Deployment

### Local Development
```bash
# Install dependencies
npm install

# Start development server
npm start
# Opens http://localhost:3000

# Clear cache (if issues occur)
npm run clear
```

### Production Build
```bash
# Build for production
npm run build
# Creates optimized static files in build/

# Test production build locally
npm run serve
# Opens http://localhost:3000
```

### Deployment Options

**1. GitHub Pages**
```javascript
// In docusaurus.config.js
module.exports = {
  url: 'https://your-username.github.io',
  baseUrl: '/robobook-docs/',
  organizationName: 'your-username',
  projectName: 'robobook-docs',
  deploymentBranch: 'gh-pages',
};
```
```bash
# Deploy
GIT_USER=your-username npm run deploy
```

**2. Netlify**
```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**3. Vercel**
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "docusaurus"
}
```

## Plugin Integration Examples

### Adding Search (Algolia)
```bash
# Already included in preset-classic
# Just configure in docusaurus.config.js
```

### Adding Google Analytics
```javascript
// In docusaurus.config.js presets
gtag: {
  trackingID: 'G-XXXXXXXXXX',
  anonymizeIP: true,
},
```

### Adding Image Optimization
```bash
npm install @docusaurus/plugin-ideal-image
```
```javascript
// In docusaurus.config.js plugins array
[
  '@docusaurus/plugin-ideal-image',
  {
    quality: 70,
    max: 1030,
    min: 640,
    steps: 2,
  },
],
```

## SSR/SSG Safety & Best Practices

### Component Swizzling (Advanced Customization)
```bash
# List swizzleable components
npm run swizzle @docusaurus/theme-classic -- --list

# Swizzle a component (e.g., Footer)
npm run swizzle @docusaurus/theme-classic Footer -- --eject
# Creates: src/theme/Footer/index.js
```

### Safe Component Patterns
```javascript
// GOOD: Check for browser environment
if (typeof window !== 'undefined') {
  // Browser-only code
}

// GOOD: Use useEffect for client-side code
import { useEffect } from 'react';

function MyComponent() {
  useEffect(() => {
    // Client-side only code
  }, []);
}

// BAD: Direct window access in module scope
const userAgent = window.navigator.userAgent; // ❌ Breaks SSR
```

## Performance Optimization

### 1. Image Optimization
```markdown
<!-- Use optimized images -->
![Robot](./img/robot.jpg "Robot Description")

<!-- Lazy loading -->
![Robot](./img/robot.jpg "Robot" {loading="lazy"})
```

### 2. Code Splitting
```javascript
// Dynamic imports for heavy components
import React, { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function MyPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
}
```

### 3. Build Performance
```javascript
// In docusaurus.config.js
module.exports = {
  future: {
    experimental_faster: true, // Experimental faster builds
  },
  
  onBrokenLinks: 'throw', // Catch broken links early
  onBrokenMarkdownLinks: 'warn',
};
```

## Troubleshooting Common Issues

### Build Errors

**Error: "Module not found"**
```bash
# Clear cache and reinstall
npm run clear
rm -rf node_modules package-lock.json
npm install
```

**Error: "Docs link to non-existent doc"**
```bash
# Check sidebar.js and verify all doc IDs exist
# Ensure file names match doc IDs
```

**Error: "Plugin conflict"**
```bash
# Check plugin versions in package.json
# Ensure all plugins are compatible with Docusaurus version
```

### Routing Issues

**Custom pages not loading**
```javascript
// Verify file is in src/pages/
// Check file extension (.js, .jsx, .md, .mdx)
// Verify export syntax:
export default function MyPage() { ... }
```

## Workflow When Setting Up

1. **Initialize Docusaurus**
   ```bash
   npx create-docusaurus@latest robobook-docs classic
   cd robobook-docs
   ```

2. **Configure docusaurus.config.js**
   - Set title: "RoboBook"
   - Set tagline: "Physical AI & Humanoid Robotics"
   - Configure navbar with user's logo and structure
   - Add language support (en, ur)
   - Set dark mode as default
   - Add plugins if needed

3. **Set Up File Structure**
   - Create docs/ folder structure matching content requirements
   - Organize content by category (Fundamentals, ROS 2, Vision, LLM, RL, Projects)
   - Create sidebars.js with proper hierarchy

4. **Create Landing Page (src/pages/index.js)**
   - Hero section (image left, text right)
   - What's Inside section with feature cards
   - CTA section
   - Book content section with top buttons

5. **Add User Assets**
   - Copy user's stacked layers logo to static/img/
   - Copy humanoid robot image for hero
   - Copy feature card icons
   - Update all references in config

6. **Configure Routing & Navigation**
   - Set up sidebar structure
   - Ensure "Book" button navigates correctly
   - Add scroll-to-section functionality
   - Test all navigation links

7. **Add Documentation Top Buttons**
   - Implement "Personalized Mode" button
   - Implement "English / اردو" language toggle
   - Position above documentation content

8. **Test Build**
   ```bash
   npm run build
   npm run serve
   ```

9. **Deploy** (if requested)
   - Choose deployment platform
   - Configure deployment settings
   - Test production build

## Critical Rules for Architecture Skill

- ✅ ALWAYS use proper Docusaurus file structure
- ✅ ALWAYS configure docusaurus.config.js completely
- ✅ ALWAYS create sidebars.js for navigation
- ✅ ALWAYS use user's provided stacked layers logo (NEVER defaults)
- ✅ ALWAYS include humanoid robot image in hero section
- ✅ ALWAYS implement navbar structure: logo + "Book" on left, search + auth + language + theme on right
- ✅ ALWAYS add "Personalized Mode" and "English / اردو" buttons at top of docs pages
- ✅ ALWAYS create landing page with hero (image left, text right)
- ✅ ALWAYS include What's Inside section with 3-4 feature cards
- ✅ ALWAYS include CTA section before book content
- ✅ ALWAYS set dark mode as default
- ✅ ALWAYS add English and Urdu language support
- ✅ ALWAYS test build before delivering
- ✅ Ensure SSR/SSG compatibility
- ✅ Optimize for performance
- ❌ **NEVER include default Docusaurus branding**
- ❌ **NEVER use placeholder images**
- ❌ **NEVER keep default blue theme**
- ❌ NEVER ignore build warnings
- ❌ NEVER use browser APIs in SSR context without checks
- ❌ NEVER handle CSS styling (use UI skill for that)

## Quality Checklist for Architecture

Before delivering, verify:
- [ ] Docusaurus structure is properly set up (docs/, blog/, src/)
- [ ] docusaurus.config.js is complete and configured
- [ ] sidebars.js reflects proper documentation structure (7 main categories)
- [ ] **User's stacked layers logo is in static/img/ and referenced in config**
- [ ] **Humanoid robot image is in static/img/ for hero section**
- [ ] **Navbar has correct structure: logo + "Book" (left), search + auth + language + theme (right)**
- [ ] **Landing page has hero section with image left, text right**
- [ ] **Landing page has What's Inside section with feature cards**
- [ ] **Landing page has CTA section**
- [ ] **"Personalized Mode" and "English / اردو" buttons on docs pages**
- [ ] Language support configured (en, ur)
- [ ] Dark mode is set as default
- [ ] All navigation links work
- [ ] Build completes without errors: `npm run build`
- [ ] Production build works: `npm run serve`
- [ ] All plugins are properly configured
- [ ] NO default Docusaurus branding visible
- [ ] Asset paths are correct

## Notes

This skill focuses PURELY on technical architecture and configuration. It does NOT handle:
- CSS styling or colors
- Visual design or hover effects
- Component appearance
- Typography styling
- Layout design

For those tasks, use the **robobook-docusaurus-ui** skill.

**Architecture Best Practices:**
1. **Maintainability**: Keep config files clean and well-documented
2. **Scalability**: Structure docs for easy expansion (7 main content categories)
3. **Performance**: Optimize build and load times
4. **Stability**: Ensure SSR/SSG compatibility
5. **Standards**: Follow Docusaurus best practices
6. **User Experience**: Proper navigation structure with clear hierarchy
7. **Internationalization**: Support multiple languages (English/Urdu)