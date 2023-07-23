import React from "react";
import clsx from "clsx";
import styles from "./styles.module.css";

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<"svg">>;
  description: JSX.Element;
};

const FeatureList: FeatureItem[] = [
  {
    title: "Ease of Experimentation",
    Svg: require("@site/static/img/streaming_notebook.svg").default,
    description: (
      <>Experiment easily with OpenAI's chat models and your own functions.</>
    ),
  },
  {
    title: "Chat Functions",
    Svg: require("@site/static/img/function_chat.svg").default,
    description: <>Bring the full power of Python to chat.</>,
  },
  {
    title: "Notebook Integration",
    Svg: require("@site/static/img/streaming_notebook.svg").default,
    description: <>Stream chat straight to your notebook.</>,
  },
];

function Feature({ title, Svg, description }: FeatureItem) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
