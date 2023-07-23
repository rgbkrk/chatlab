import clsx from "clsx";
import React from "react";

import styles from "./styles.module.css";

type Props = {
  count: number | string;
  type: "input" | "output";
};

const ExecutionCount: React.FC<Props> = ({ count, type }) => {
  // If count is not a number, return a [ ]
  let counterText = "[ ]:";
  if (typeof count === "number" || typeof count === "string") {
    counterText = `[${count}]:`;
  }

  const executionCountClass = clsx(styles.executionCount, {
    [styles.executionCountInput]: type === "input",
    [styles.executionCountOutput]: type === "output",
  });

  return <div className={executionCountClass}>{counterText}</div>;
};

export default ExecutionCount;
