import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Installation',
      collapsible: true,
      collapsed: false,
      items: [
        {type: 'doc', id: 'capstone/Installation/HYPRONET_INSTALLATION_GUIDE'},
        {type: 'doc', id: 'capstone/Installation/STARTUP_GUIDE'},
      ],
    },
    {
      type: 'category',
      label: 'CodeExplanation',
      collapsible: true,
      collapsed: false,
      items: [
      ],
    },
  ],
};

export default sidebars;
