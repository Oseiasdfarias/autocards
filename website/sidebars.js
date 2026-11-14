// @ts-check
/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docs: [
    'intro',
    'install',
    'getting-started',
    {type: 'category', label: 'Using AutoCards', collapsed: false,
      items: ['generators', 'rules', 'review-queue', 'services-and-costs', 'import-export', 'log-and-quality']},
    {type: 'category', label: 'Help', collapsed: false,
      items: ['troubleshooting', 'privacy', 'faq']},
    'development',
    'changelog',
  ],
};
export default sidebars;
