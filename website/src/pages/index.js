import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Translate, {translate} from '@docusaurus/Translate';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';

const FEATURES = [
  {
    title: translate({id: 'home.f1.title', message: 'Runs by itself, every day'}),
    text: translate({id: 'home.f1.text', message: 'Each generator makes its daily quota when your profile opens, in the background. Missed days never pile up.'}),
  },
  {
    title: translate({id: 'home.f2.title', message: 'Protects your reviews and your wallet'}),
    text: translate({id: 'home.f2.text', message: 'Starts small, pauses when overdue reviews pile up, and stops at a monthly spending cap you choose.'}),
  },
  {
    title: translate({id: 'home.f3.title', message: 'A prompt you can actually edit'}),
    text: translate({id: 'home.f3.text', message: 'Role, topic, level, front, back, what to avoid, examples: toggle, reorder or add fields, with a live preview.'}),
  },
  {
    title: translate({id: 'home.f4.title', message: 'Audio with the voice you pick'}),
    text: translate({id: 'home.f4.text', message: 'Free Microsoft Edge voices, OpenAI or ElevenLabs. If audio fails, the card still goes in.'}),
  },
  {
    title: translate({id: 'home.f5.title', message: 'You stay in control'}),
    text: translate({id: 'home.f5.text', message: 'Turn on the review queue to accept, edit or discard every card before it reaches your study.'}),
  },
  {
    title: translate({id: 'home.f6.title', message: 'Nothing to install'}),
    text: translate({id: 'home.f6.text', message: 'Only what ships with Anki. Bring any OpenAI-compatible service, or run a free local model with Ollama.'}),
  },
];

export default function Home() {
  return (
    <Layout
      title={translate({id: 'home.meta.title', message: 'AI flashcards for Anki, every day'})}
      description={translate({id: 'home.meta.description', message: 'AutoCards is an Anki add-on that writes new flashcards for you every day with AI.'})}>
      <header className={clsx('hero', styles.hero)}>
        <div className="container">
          <img src={require('@site/static/img/logo.svg').default} alt="" className={styles.logo} />
          <Heading as="h1" className="hero__title">AutoCards</Heading>
          <p className="hero__subtitle">
            <Translate id="home.tagline">New Anki flashcards every day, written by AI, on their own.</Translate>
          </p>
          <div className={styles.buttons}>
            <Link className="button button--primary button--lg" to="/docs/getting-started">
              <Translate id="home.cta.start">Get started</Translate>
            </Link>
            <Link className="button button--secondary button--lg" to="/docs/intro">
              <Translate id="home.cta.what">What is AutoCards?</Translate>
            </Link>
          </div>
        </div>
      </header>
      <main className="container margin-vert--xl">
        <div className="row">
          {FEATURES.map((f) => (
            <div key={f.title} className={clsx('col col--4', styles.feature)}>
              <Heading as="h3">{f.title}</Heading>
              <p>{f.text}</p>
            </div>
          ))}
        </div>
      </main>
    </Layout>
  );
}
