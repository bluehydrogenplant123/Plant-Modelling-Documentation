import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Installation',
      collapsible: true,
      collapsed: false,
      items: [
        {type: 'doc', id: 'capstone/SetupInstructions/Installation/HYPRONET_INSTALLATION_GUIDE'},
        {type: 'doc', id: 'capstone/SetupInstructions/Installation/STARTUP_GUIDE'},
      ],
    },
    {
      type: 'category',
      label: 'CodeExplanation',
      collapsible: true,
      collapsed: false,
      items: [
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/CODE_EXPLANATION_GUIDELINES'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/code-explanation-index'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/code-explanation-overview'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/dashboard-and-canvas'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/header-bar'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/time-period-and-economic-flow'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/run-config-and-computation-start'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/save-diagram-and-node-cache'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/custom-edge-and-stream-selection'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/node-modal-and-variable-inputs'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/shape-node-and-ports'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/subnetwork-blueprint-and-instance-flow'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/backend-data-routes-and-persistence'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/compute-solver-callback-and-results'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/translation-and-reverse-translation'},
        {type: 'doc', id: 'capstone/SetupInstructions/CodeExplanation/excel-import-pipeline'},
      ],
    },

  ],
};

export default sidebars;
