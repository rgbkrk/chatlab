import React, { FunctionComponent } from "react";

type DocProps = {
    jsonData: {
        methods: {
            name: string;
            description: string;
            parameters: {
                name: string;
                default: string | number | boolean | null;
                annotation: string | null;
            }[];
            returns: string | null;
        }[];
        parent_classes: string[];
    };
};

export const Documentation: FunctionComponent<DocProps> = ({ jsonData }) => {
    return (
        <div>
            <h1>Class Chat</h1>
            <p>Parent classes: {jsonData.parent_classes.join(", ")}</p>
            {jsonData.methods.map((method, idx) => {
                return (
                    <div key={idx}>
                        <h2>{method.name}</h2>
                        <p>{method.description}</p>
                        <h3>Parameters</h3>
                        <ul>
                            {method.parameters.map((param, idx) => {
                                return (
                                    <li key={idx}>
                                        <strong>{param.name}</strong>:{" "}
                                        {param.annotation || "Not specified"}{" "}
                                        {param.default &&
                                            `(default: ${param.default})`}
                                    </li>
                                );
                            })}
                        </ul>
                        <p>Returns: {method.returns || "Not specified"}</p>
                    </div>
                );
            })}
        </div>
    );
};

export default Documentation;
