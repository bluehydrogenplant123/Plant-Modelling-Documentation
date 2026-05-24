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
        {type: 'doc', id: 'capstone/CodeExplanation/CODE_EXPLANATION_GUIDELINES'},
        {type: 'doc', id: 'capstone/CodeExplanation/code-explanation-index'},
        {type: 'doc', id: 'capstone/CodeExplanation/code-explanation-overview'},
        {type: 'doc', id: 'capstone/CodeExplanation/dashboard-and-canvas'},
        {type: 'doc', id: 'capstone/CodeExplanation/header-bar'},
        {type: 'doc', id: 'capstone/CodeExplanation/time-period-and-economic-flow'},
        {type: 'doc', id: 'capstone/CodeExplanation/run-config-and-computation-start'},
        {type: 'doc', id: 'capstone/CodeExplanation/save-diagram-and-node-cache'},
        {type: 'doc', id: 'capstone/CodeExplanation/custom-edge-and-stream-selection'},
        {type: 'doc', id: 'capstone/CodeExplanation/node-modal-and-variable-inputs'},
        {type: 'doc', id: 'capstone/CodeExplanation/shape-node-and-ports'},
        {type: 'doc', id: 'capstone/CodeExplanation/subnetwork-blueprint-and-instance-flow'},
        {type: 'doc', id: 'capstone/CodeExplanation/backend-data-routes-and-persistence'},
        {type: 'doc', id: 'capstone/CodeExplanation/compute-solver-callback-and-results'},
        {type: 'doc', id: 'capstone/CodeExplanation/translation-and-reverse-translation'},
        {type: 'doc', id: 'capstone/CodeExplanation/excel-import-pipeline'},
        {type: 'doc', id: 'capstone/CodeExplanation/test'},
      ],
    },
  ],
};

export default sidebars;
