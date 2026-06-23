import React, {type ReactNode, useCallback} from 'react';
import clsx from 'clsx';
import useBaseUrl from '@docusaurus/useBaseUrl';

type Props = {
  readonly className?: string;
  readonly label?: string;
  readonly mobile?: boolean;
};

const workflowFileName = 'ai-codeexplanation-maintenance-workflow.md';

export default function WorkflowDownloadNavbarItem({
  className,
  label = 'Download',
  mobile = false,
}: Props): ReactNode {
  const workflowUrl = useBaseUrl(
    '/capstone-assets/CodeExplanation/ai-codeexplanation-maintenance-workflow.md',
  );

  const handleDownload = useCallback(async () => {
    try {
      const response = await fetch(workflowUrl);
      if (!response.ok) {
        throw new Error(`Unable to download workflow: ${response.status}`);
      }

      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');

      link.href = objectUrl;
      link.download = workflowFileName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(objectUrl);
    } catch {
      window.location.assign(workflowUrl);
    }
  }, [workflowUrl]);

  const button = (
    <button
      type="button"
      className={clsx(
        mobile ? 'menu__link' : 'navbar__item navbar__link',
        className,
      )}
      onClick={handleDownload}>
      {label}
    </button>
  );

  return mobile ? <li className="menu__list-item">{button}</li> : button;
}
