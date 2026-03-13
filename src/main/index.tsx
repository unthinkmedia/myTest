import React from 'react';
import { makeStyles, tokens, Text } from '@fluentui/react-components';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    padding: '48px',
  },
  card: {
    textAlign: 'center',
    maxWidth: '480px',
  },
  heading: {
    marginBottom: '8px',
  },
  subtitle: {
    color: tokens.colorNeutralForeground3,
  },
});

const MainPage: React.FC = () => {
  const styles = useStyles();

  return (
    <div className={styles.root}>
      <div className={styles.card}>
        <Text as="h1" size={800} weight="semibold" block className={styles.heading}>
          Experiment Ready
        </Text>
        <Text size={400} className={styles.subtitle} block>
          This is your main version. Start building here or ask to &quot;make a variation&quot;.
        </Text>
      </div>
    </div>
  );
};

export default MainPage;
