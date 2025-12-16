// @ts-nocheck

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Introduction',
      items: ['intro'],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 1: ROS 2 Fundamentals',
      items: [
        'module1/chapter1',
        'module1/chapter2',
        'module1/chapter3',
        'module1/chapter4',
        'module1/chapter5'
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 2: Simulation (Gazebo/Unity)',
      items: [
        'module2/chapter1',
        'module2/chapter2',
        'module2/chapter3',
        'module2/chapter4',
        'module2/chapter5'
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 3: Isaac (VSLAM/Nav2)',
      items: [
        'module3/chapter1',
        'module3/chapter2',
        'module3/chapter3',
        'module3/chapter4',
        'module3/chapter5'
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 4: Voice Control & LLM Integration',
      items: [
        'module4/chapter1',
        'module4/chapter2',
        'module4/chapter3',
        'module4/chapter4',
        'module4/chapter5'
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Supporting Documentation',
      items: [
        'supporting/hardware',
        'supporting/installation',
        'supporting/troubleshooting',
        'supporting/glossary',
        'supporting/resources'
      ],
      collapsed: true,
    }
  ],
};

module.exports = sidebars;