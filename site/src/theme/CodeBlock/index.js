import clsx from "clsx";
import React from "react";

import { InputBlock, OutputBlock } from "@site/src/components/cell";
import CodeBlock from "@theme-original/CodeBlock";

export default function CodeBlockWrapper(props) {
  //
  // This CodeBlockWrapper introduces two new types of markdown code blocks,
  // to mimic Jupyter Notebook frontend cells:
  //
  // - Input Blocks
  // - Output Blocks
  //
  // To use them, simply add the following to your markdown:
  //
  // ```python cell
  // d = {"foo": "bar"}
  // d
  // ```
  //
  // ```json output
  // {
  //   "foo": "bar"
  // }
  // ```
  //

  // Regular Code Blocks
  if (!props.cell && !props.output) {
    return <CodeBlock {...props} />;
  }

  let count = props.count || props.executionCount || props.execution_count;

  // Handle basic plaintext outputs in a friendly way for JSON outputs
  if (props.output) {
    // HACK: Allow the CodeBlockContainer to know this is an output block
    const className = clsx(props.className, "chatlab-cell-output");

    return (
      <OutputBlock count={count}>
        <CodeBlock {...props} className={className} />
      </OutputBlock>
    );
  }

  return (
    <InputBlock count={count}>
      <CodeBlock {...props} />
    </InputBlock>
  );
}
