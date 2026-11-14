// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'AutoCards',
  tagline: 'New Anki flashcards every day, written by AI, on their own.',
  favicon: 'img/logo.svg',

  future: {v4: true},

  url: 'https://oseiasdfarias.github.io',
  baseUrl: '/autocards/',
  organizationName: 'Oseiasdfarias',
  projectName: 'autocards',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  markdown: {hooks: {onBrokenMarkdownLinks: 'throw'}},

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'pt-BR'],
    localeConfigs: {
      en: {label: 'English', htmlLang: 'en'},
      'pt-BR': {label: 'Português (Brasil)', htmlLang: 'pt-BR'},
    },
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/Oseiasdfarias/autocards/edit/develop/website/',
        },
        blog: false,
        theme: {customCss: './src/css/custom.css'},
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {respectPrefersColorScheme: true},
      navbar: {
        title: 'AutoCards',
        logo: {alt: 'AutoCards', src: 'img/logo.svg'},
        items: [
          {type: 'docSidebar', sidebarId: 'docs', position: 'left', label: 'Docs'},
          {to: '/docs/changelog', label: 'Changelog', position: 'left'},
          {type: 'localeDropdown', position: 'right'},
          {href: 'https://github.com/Oseiasdfarias/autocards', label: 'GitHub', position: 'right'},
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {label: 'Getting started', to: '/docs/getting-started'},
              {label: 'Rules', to: '/docs/rules'},
              {label: 'Troubleshooting', to: '/docs/troubleshooting'},
            ],
          },
          {
            title: 'Project',
            items: [
              {label: 'GitHub', href: 'https://github.com/Oseiasdfarias/autocards'},
              {label: 'Issues', href: 'https://github.com/Oseiasdfarias/autocards/issues'},
            ],
          },
        ],
        copyright: `AutoCards · AGPL-3.0`,
      },
      prism: {theme: prismThemes.github, darkTheme: prismThemes.dracula},
    }),
};

export default config;
