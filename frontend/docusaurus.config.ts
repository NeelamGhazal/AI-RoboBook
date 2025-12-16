import { themes as prismThemes } from 'prism-react-renderer';

/** @type {import('@docusaurus/types').DocusaurusConfig} */
module.exports = {
  title: 'RoboBook',
  tagline: 'Physical AI & Humanoid Robotics Curriculum',
  favicon: '/img/robobook-logo.png',

  // ✅ Cloudflare Pages URL (safe default)
  url: 'https://ai-robobook.pages.dev',

  // ✅ IMPORTANT: Cloudflare Pages needs /
  baseUrl: '/',

  // GitHub info (still fine to keep)
  organizationName: 'NeelamGhazal',
  projectName: 'AI-RoboBook',

  // ✅ IGNORE broken links for now
  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  markdown: {
    mermaid: true,
    mdx1Compat: {
      comments: false,
      admonitions: false,
      headingIds: false,
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: '/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  themeConfig: {
    image: 'img/robotics-arm.png',
    navbar: {
      title: 'RoboBook',
      logo: {
        alt: 'RoboBook Logo',
        src: 'img/robobook-logo.png',
      },
      items: [],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Modules',
          items: [
            { label: 'Module 1: ROS 2', to: '/docs/module1/chapter1' },
            { label: 'Module 2: Gazebo/Unity', to: '/docs/module2/chapter1' },
            { label: 'Module 3: Isaac', to: '/docs/module3/chapter1' },
            { label: 'Module 4: VLA', to: '/docs/module4/chapter1' },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/NeelamGhazal/AI-RoboBook',
            },
          ],
        },
        {
          title: 'More',
          items: [
            { label: 'Documentation', to: '/docs/intro' },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} RoboBook.`,
    },
    prism: {
      theme: prismThemes.vsDark,
      darkTheme: prismThemes.vsDark,
      additionalLanguages: ['python', 'cpp', 'yaml', 'bash'],
    },
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: false,
      respectPrefersColorScheme: false,
    },
    mermaid: {
      theme: { light: 'default', dark: 'dark' },
    },
  },

  themes: ['@docusaurus/theme-mermaid'],

  plugins: [
    [
      require.resolve('@docusaurus/plugin-ideal-image'),
      {
        quality: 85,
        max: 2000,
        min: 500,
      },
    ],
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      {
        hashed: true,
        language: ['en'],
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
      },
    ],
  ],
};
