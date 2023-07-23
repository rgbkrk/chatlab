import React from "react";
import styles from "./styles.module.css";

interface ChatFunctionProps {
  name?: string;
  verbage?: string;
  input?: string;
  output?: string;
  open?: boolean;
  finished?: boolean;
}

const RawFunctionInterface: React.FC<{ title: string; text: string }> = ({
  title,
  text,
}) => (
  <div>
    <div className={styles.rawFunctionInterfaceHeading}>{title}</div>
    <div className={styles.rawFunctionInterface}>{text}</div>
  </div>
);

const ChatFunctionComponent: React.FC<ChatFunctionProps> = ({
  name = "Function",
  verbage = "Ran",
  input,
  output,
  finished = true,
  open = false,
}) => {
  return (
    <details className={styles.chatlabChatDetails} open={open}>
      <summary className={styles.summary}>
        <span className={styles.functionLogo}>𝑓</span>
        <span className={styles.functionVerbage}>{verbage}</span>
        <span className={styles.inlinePre}>{name}</span>
        <span className={styles.inlinePre}>{finished ? "" : "..."}</span>
      </summary>
      <div className={styles.inputOutputDiv}>
        {input && <RawFunctionInterface title="Input:" text={input} />}
        {output && <RawFunctionInterface title="Output:" text={output} />}
      </div>
    </details>
  );
};

export default ChatFunctionComponent;
