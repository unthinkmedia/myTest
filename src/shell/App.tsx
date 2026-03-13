import React, { useState, useEffect, useMemo } from 'react';
import {
  makeStyles,
  tokens,
  Text,
  Dropdown,
  Option,
  Tab,
  TabList,
} from '@fluentui/react-components';

// ─── Auto-discover main + variations ────────────────────────────
// Eager-glob so Vite bundles them at build time.
const mainModules = import.meta.glob<{ default: React.FC }>(
  '../main/**/*.tsx',
  { eager: true },
);

const variationModules = import.meta.glob<{ default: React.FC }>(
  '../variations/**/*.tsx',
  { eager: true },
);

const flowModules = import.meta.glob<string[]>(
  ['../main/flow.json', '../variations/*/flow.json'],
  { eager: true, import: 'default' },
);

const metaModules = import.meta.glob<{ description?: string }>(
  '../variations/*/meta.json',
  { eager: true, import: 'default' },
);

// ─── Helpers ────────────────────────────────────────────────────

interface ExperimentVersion {
  key: string;          // "main" | variation folder name
  label: string;        // Title-cased display name
  description?: string;
  screens: Record<string, React.FC>; // screen name → component
  flow?: string[];      // ordered screen names (from flow.json)
}

function toTitleCase(slug: string): string {
  return slug
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

function buildVersions(): ExperimentVersion[] {
  const versions: ExperimentVersion[] = [];

  // ── Main ──
  const mainScreens: Record<string, React.FC> = {};
  for (const [path, mod] of Object.entries(mainModules)) {
    const file = path.split('/').pop()!.replace('.tsx', '');
    if (file === 'index') {
      mainScreens['Main'] = mod.default;
    } else {
      mainScreens[file] = mod.default;
    }
  }
  const mainFlow = flowModules['../main/flow.json'] as string[] | undefined;
  versions.push({
    key: 'main',
    label: 'Main',
    screens: mainScreens,
    flow: mainFlow,
  });

  // ── Variations ──
  const variationNames = new Set<string>();
  for (const path of Object.keys(variationModules)) {
    // path looks like: ../variations/compact-toolbar/index.tsx
    const parts = path.replace('../variations/', '').split('/');
    variationNames.add(parts[0]);
  }

  for (const name of variationNames) {
    const screens: Record<string, React.FC> = {};
    const prefix = `../variations/${name}/`;
    for (const [path, mod] of Object.entries(variationModules)) {
      if (!path.startsWith(prefix)) continue;
      const file = path.replace(prefix, '').replace('.tsx', '');
      if (file === 'index') {
        screens['Main'] = mod.default;
      } else {
        screens[file] = mod.default;
      }
    }

    const flowKey = `../variations/${name}/flow.json`;
    const flow = flowModules[flowKey] as string[] | undefined;

    const metaKey = `../variations/${name}/meta.json`;
    const meta = metaModules[metaKey] as { description?: string } | undefined;

    versions.push({
      key: name,
      label: toTitleCase(name),
      description: meta?.description,
      screens,
      flow,
    });
  }

  return versions;
}

// ─── Styles ─────────────────────────────────────────────────────
const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '8px 16px',
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground3,
    flexShrink: 0,
  },
  title: {
    fontWeight: tokens.fontWeightSemibold,
  },
  description: {
    color: tokens.colorNeutralForeground3,
    marginLeft: '4px',
  },
  stepBar: {
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    paddingLeft: '16px',
    flexShrink: 0,
  },
  content: {
    flex: 1,
    overflow: 'auto',
  },
  empty: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    color: tokens.colorNeutralForeground3,
  },
});

// ─── Hash helpers ───────────────────────────────────────────────
function parseHash(): { version?: string; screen?: string } {
  const raw = window.location.hash.replace(/^#\/?/, '');
  if (!raw) return {};
  const [version, screen] = raw.split('/');
  return { version: version || undefined, screen: screen || undefined };
}

function writeHash(version: string, screen?: string) {
  const fragment = screen && screen !== 'Main'
    ? `${version}/${screen}`
    : version;
  window.history.replaceState(null, '', `#${fragment}`);
}

// ─── App ────────────────────────────────────────────────────────
const App: React.FC = () => {
  const styles = useStyles();
  const versions = useMemo(() => buildVersions(), []);

  // Initialise from hash, falling back to first version
  const initialHash = useMemo(() => parseHash(), []);
  const initialVersion =
    versions.find((v) => v.key === initialHash.version)?.key
    ?? versions[0]?.key
    ?? 'main';

  const [activeVersionKey, setActiveVersionKey] = useState(initialVersion);
  const [activeScreen, setActiveScreen] = useState<string>(initialHash.screen ?? 'Main');

  const activeVersion = versions.find((v) => v.key === activeVersionKey) ?? versions[0];

  // Determine screen list: flow.json order, or fallback to discovered screens
  const screenNames = useMemo(() => {
    if (!activeVersion) return [];
    if (activeVersion.flow) return activeVersion.flow;
    const keys = Object.keys(activeVersion.screens);
    return keys;
  }, [activeVersion]);

  // Reset screen when switching versions (but not on initial mount from hash)
  const isInitialMount = React.useRef(true);
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      // On first mount, validate the hash-provided screen exists
      if (!screenNames.includes(activeScreen) && screenNames.length > 0) {
        setActiveScreen(screenNames[0]);
      }
      return;
    }
    if (screenNames.length > 0) {
      setActiveScreen(screenNames[0]);
    }
  }, [activeVersionKey, screenNames]);

  // Sync hash on state changes
  useEffect(() => {
    writeHash(activeVersionKey, activeScreen);
  }, [activeVersionKey, activeScreen]);

  // Respond to browser back/forward
  useEffect(() => {
    const onHashChange = () => {
      const { version, screen } = parseHash();
      if (version && versions.some((v) => v.key === version)) {
        setActiveVersionKey(version);
        if (screen) setActiveScreen(screen);
      }
    };
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, [versions]);

  const ActiveComponent = activeVersion?.screens[activeScreen];
  const showStepTabs = screenNames.length > 1;

  return (
    <div className={styles.root}>
      {/* ── Header bar ── */}
      <div className={styles.header}>
        <Text className={styles.title} size={400}>Playground</Text>

        {versions.length > 1 && (
          <Dropdown
            value={activeVersion?.label ?? 'Main'}
            selectedOptions={[activeVersionKey]}
            onOptionSelect={(_, data) => {
              if (data.optionValue) setActiveVersionKey(data.optionValue);
            }}
            size="small"
          >
            {versions.map((v) => (
              <Option key={v.key} value={v.key} text={v.label}>
                {v.label}
                {v.description && (
                  <Text size={200} className={styles.description}>
                    {' — '}{v.description}
                  </Text>
                )}
              </Option>
            ))}
          </Dropdown>
        )}
      </div>

      {/* ── Step tabs (multi-screen flows) ── */}
      {showStepTabs && (
        <div className={styles.stepBar}>
          <TabList
            selectedValue={activeScreen}
            onTabSelect={(_, data) => setActiveScreen(data.value as string)}
            size="small"
          >
            {screenNames.map((name) => (
              <Tab key={name} value={name}>
                {name}
              </Tab>
            ))}
          </TabList>
        </div>
      )}

      {/* ── Content ── */}
      <div className={styles.content}>
        {ActiveComponent ? (
          <ActiveComponent />
        ) : (
          <Text className={styles.empty} size={400}>
            No screens found. Create src/main/index.tsx to get started.
          </Text>
        )}
      </div>
    </div>
  );
};

export default App;
