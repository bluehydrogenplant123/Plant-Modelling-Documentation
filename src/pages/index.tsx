import {useEffect, type ReactNode} from 'react';
import Head from '@docusaurus/Head';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

export default function Home(): ReactNode {
  const {
    siteConfig: {baseUrl},
  } = useDocusaurusContext();
  const docsPath = `${baseUrl}docs`;

  useEffect(() => {
    window.location.replace(docsPath);
  }, [docsPath]);

  return (
    <Layout title="Documentation">
      <Head>
        <meta httpEquiv="refresh" content={`0; url=${docsPath}`} />
        <link rel="canonical" href={docsPath} />
      </Head>
      <main className="container margin-vert--xl">
        <h1>Redirecting to Documentation</h1>
        <p>
          If the page does not open automatically, continue to{' '}
          <a href={docsPath}>Documentation</a>.
        </p>
      </main>
    </Layout>
  );
}
