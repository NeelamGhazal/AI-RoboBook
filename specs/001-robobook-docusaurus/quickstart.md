# Quickstart: RoboBook Docusaurus Setup

**Feature**: 001-robobook-docusaurus
**Date**: 2025-12-13
**Estimated Time**: 30 minutes

## Prerequisites

- Node.js 18+ and npm 9+
- Git 2.30+
- Docker Desktop (for testing code examples)
- GitHub account with repository access
- 5GB free disk space

## Setup Steps

### 1. Initialize Docusaurus Project (5 minutes)

```bash
# Clone repository
git clone https://github.com/{org}/phyai-humanoid-textbook.git
cd phyai-humanoid-textbook

# Create Docusaurus site
npx create-docusaurus@latest . classic --typescript

# Install dependencies
npm install

# Install additional plugins
npm install --save @docusaurus/theme-mermaid
npm install --save @docusaurus/plugin-google-gtag
npm install --save @easyops-cn/docusaurus-search-local
npm install --save @docusaurus/plugin-ideal-image
```

### 2. Configure RoboBook Theme (10 minutes)

Edit `docusaurus.config.ts`:

```typescript
import {themes as prismThemes} from 'prism-react-renderer';

const config: Config = {
  title: 'RoboBook',
  tagline: 'Physical AI & Humanoid Robotics Textbook',
  url: 'https://{org}.github.io',
  baseUrl: '/phyai-humanoid-textbook/',
  organizationName: '{org}',
  projectName: 'phyai-humanoid-textbook',

  themes: ['@docusaurus/theme-mermaid'],
  markdown: {
    mermaid: true,
  },

  themeConfig: {
    colorMode: {
      defaultMode: 'dark',
      respectPrefersColorScheme: false,
    },
    navbar: {
      title: 'RoboBook',
      logo: {
        alt: 'RoboBook Logo',
        src: 'img/robobook-logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Modules',
        },
        {
          href: 'https://github.com/{org}/phyai-humanoid-textbook',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    prism: {
      theme: prismThemes.vsDark,
      additionalLanguages: ['python', 'cpp', 'yaml', 'xml'],
    },
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

  plugins: [
    ['@docusaurus/plugin-google-gtag', {
      trackingID: 'G-XXXXXXXXXX',
      anonymizeIP: true,
    }],
    [require.resolve('@easyops-cn/docusaurus-search-local'), {
      hashed: true,
      language: ['en'],
      highlightSearchTermsOnTargetPage: true,
    }],
    ['@docusaurus/plugin-ideal-image', {
      quality: 85,
      max: 2000,
      min: 500,
      disableInDev: false,
    }],
  ],
};
```

Edit `src/css/custom.css`:

```css
:root {
  /* RoboBook Colors */
  --ifm-color-primary: #00d4ff;
  --ifm-color-primary-dark: #0ea5e9;
  --ifm-color-primary-darker: #0284c7;
  --ifm-color-primary-darkest: #0369a1;
  --ifm-color-primary-light: #38bdf8;
  --ifm-color-primary-lighter: #7dd3fc;
  --ifm-color-primary-lightest: #bae6fd;

  --ifm-background-color: #0f1729;
  --ifm-background-surface-color: #1a1f3a;

  /* Typography */
  --ifm-heading-font-size-h1: 3.5rem;
  --ifm-heading-font-size-h2: 2.5rem;
  --ifm-heading-font-size-h3: 1.75rem;
  --ifm-font-size-base: 1rem;

  /* Spacing (8px grid) */
  --ifm-spacing-horizontal: 8px;
  --ifm-spacing-vertical: 8px;
}

/* Glassmorphism cards */
.card {
  background: rgba(26, 31, 58, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
}

/* Hover effects */
.card:hover {
  transform: scale(1.02);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
  transition: all 0.3s ease;
  cursor: pointer;
}

/* Code theme customization */
.token.keyword { color: #00d4ff; }
.token.string { color: #0ea5e9; }
.token.comment { color: #64748b; }
```

### 3. Setup Monorepo Structure (5 minutes)

```bash
# Create directories
mkdir -p docs/module1 docs/module2 docs/module3 docs/module4 docs/supporting
mkdir -p examples/module1 examples/module2 examples/module3 examples/module4
mkdir -p static/img static/diagrams

# Configure Git LFS for large images
echo "*.png filter=lfs diff=lfs merge=lfs -text" > .gitattributes
echo "*.jpg filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
git lfs install
```

### 4. Setup Docker Test Environment (5 minutes)

Create `examples/Dockerfile`:

```dockerfile
FROM osrf/ros:humble-desktop-full-jammy

WORKDIR /workspace

# Install Python dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Copy examples
COPY . /workspace

# Source ROS 2
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

CMD ["/bin/bash"]
```

Build Docker image:

```bash
cd examples
docker build -t robobook-ros2-humble .
cd ..
```

### 5. Configure GitHub Actions Deployment (5 minutes)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true
      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Build website
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: build

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

Enable GitHub Pages in repository settings:
- Go to Settings > Pages
- Source: GitHub Actions

### 6. Verify Setup

```bash
# Start development server
npm start

# In browser, navigate to http://localhost:3000
# Verify:
# - Dark mode enabled by default
# - RoboBook colors visible (cyan accents on dark navy)
# - Navigation working
# - Search box present

# Build production version
npm run build

# Serve production build
npm run serve

# Verify build artifacts in /build directory
```

## Next Steps

1. Create first module: `docs/module1/intro.md`
2. Add content following data-model.md specifications
3. Test code examples in Docker container
4. Commit and push to trigger deployment
5. Verify live site at `https://{org}.github.io/phyai-humanoid-textbook/`

## Troubleshooting

### Build fails with "Module not found"
- **Solution**: Run `npm ci` to reinstall dependencies
- **Prevention**: Don't manually edit `package-lock.json`

### Docker container won't start
- **Solution**: Ensure Docker Desktop is running, check image exists with `docker images`
- **Prevention**: Build image before running: `docker build -t robobook-ros2-humble examples/`

### GitHub Pages shows 404
- **Solution**: Check `baseUrl` in `docusaurus.config.ts` matches repo name
- **Prevention**: Use `/{repo-name}/` format for baseUrl

### Search not working in development
- **Solution**: Local search only works in production build (`npm run build` + `npm run serve`)
- **Prevention**: Test search in production mode before deploying

## Reference

- Docusaurus Documentation: https://docusaurus.io/docs
- Research Document: `specs/001-robobook-docusaurus/research.md`
- Data Model: `specs/001-robobook-docusaurus/data-model.md`
- Build Validation: `specs/001-robobook-docusaurus/contracts/build-validation.yaml`
