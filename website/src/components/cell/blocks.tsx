import React from "react";
import styles from "./styles.module.css";
import clsx from "clsx";

import ExecutionCount from "./execution-count";

type Props = {
  count: number | string;
  children: React.ReactNode;
  type: "input" | "output";
};

const Block = ({ count, children, type }) => {
  const contentWrapperClass = clsx(styles.cellContentWrapper, {
    // We rely on the fact that the <CodeBlock /> component already has
    // padding, so we don't add any here.
    // [styles.cellContentWrapperInput]: type === "input",
    [styles.cellContentWrapperOutput]: type === "output",
  });

  return (
    <div className={styles.cellWrapper}>
      <ExecutionCount count={count} type={type} />
      <div className={contentWrapperClass}>{children}</div>
    </div>
  );
};

export const InputBlock = (props) => <Block type="input" {...props} />;
export const OutputBlock = (props) => <Block type="output" {...props} />;

export default Block;
