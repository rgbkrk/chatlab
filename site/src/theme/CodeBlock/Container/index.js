import React from "react";
import clsx from "clsx";
import { ThemeClassNames, usePrismTheme } from "@docusaurus/theme-common";
import { getPrismCssVariables } from "@docusaurus/theme-common/internal";
import styles from "./styles.module.css";
export default function CodeBlockContainer({ as: As, ...props }) {
  const prismTheme = usePrismTheme();
  let prismCssVariables = getPrismCssVariables(prismTheme);

  let className = clsx(
    props.className,
    styles.codeBlockContainer,
    ThemeClassNames.common.codeBlock
  );

  // HACK: Detect if this is an output block, and if so, remove the inline styles
  if (props.className.includes("chatlab-cell-output")) {
    // We want output to render without:
    // - The inline style for background color added to the element
    // - The inline style for color added to the element
    // - The box shadow
    prismCssVariables = {};
    className = clsx(
      props.className,
      styles.outputBlockContainer,
      ThemeClassNames.common.codeBlock
    );
  }

  return (
    <As
      // Polymorphic components are hard to type, without `oneOf` generics
      {...props}
      style={prismCssVariables}
      className={className}
    />
  );
}
