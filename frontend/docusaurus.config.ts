import {themes as prismThemes} from 'prism-react-renderer';

// With JSDoc @type annotations, IDEs can provide config autocompletion
/** @type {import('@docusaurus/types').DocusaurusConfig} */
module.exports = {
  title: 'RoboBook',
  tagline: 'Physical AI & Humanoid Robotics Curriculum',
  favicon: '/img/robobook-logo.png',

  // Set the production url of your site here
  url: 'https://phyai-humanoid-textbook.github.io',
  // Set the /<base>/ pathname under which your site is served
  // For GitHub Pages: /<username>.github.io/<project-name>/
  baseUrl: '/phyai-humanoid-textbook/',

  // GitHub pages deployment config.
  organizationName: 'phyai-humanoid-textbook',
  projectName: 'phyai-humanoid-textbook.github.io',

  onBrokenLinks: 'throw',

  markdown: {
    mermaid: true,
    mdx1Compat: {
      comments: false,
      admonitions: false,
      headingIds: false,
    },
  },

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/phyai-humanoid-textbook/phyai-humanoid-textbook/edit/main/',
        },
        blog: false, // Optional: disable the blog plugin
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
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
              {
                label: 'Module 1: ROS 2',
                to: '/docs/module1/chapter1',
              },
              {
                label: 'Module 2: Gazebo/Unity',
                to: '/docs/module2/chapter1',
              },
              {
                label: 'Module 3: Isaac',
                to: '/docs/module3/chapter1',
              },
              {
                label: 'Module 4: VLA',
                to: '/docs/module4/chapter1',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/phyai-humanoid-textbook',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Documentation',
                to: '/docs/intro',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} RoboBook. Licensed under Creative Commons BY-SA 4.0.`,
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
    }),

  themes: [
    '@docusaurus/theme-mermaid',
  ],

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
      require.resolve('@docusaurus/plugin-google-gtag'),
      {
        trackingID: 'GA-TRACKING-ID-PLACEHOLDER',
        anonymizeIP: true,
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