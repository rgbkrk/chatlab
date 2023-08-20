# Documentation Plan for Chatlab

## Overview
To provide the best developer experience for Chatlab users, our goal is to create comprehensive, up-to-date, and easily accessible documentation. To achieve this, we will leverage a blend of automated and manual processes, targeting both module-level API reference docs and narrative guides for effective usage.

## Plan Outline
1. **API Reference Documentation Generation**: Implement a system that uses Python's `inspect` module to automate the generation of API reference documentation. The system will extract docstrings, methods, parameters, and default values from the `Chat` class and other relevant classes/functions in the `chatlab` module, excluding non-public methods and deprecated methods. The extracted data will be serialized into a JSON file. 

2. **MDX Integration and Format Improvement**: Leverage Docusaurus's MDX feature to import the generated JSON file and create Markdown files directly, improving the formatting by using monospace fonts on types and parameters. The hashlib object on `Chat` should not be included here. That means that `__process_stream` should not be included but `__call__`, `__init__`, should be included as well as e.g. `clear_history`. Deprecated methods should also not be included.

3. **Existing Documentation Review**: Review the existing narrative documentation in the `website/docs` directory. Identify any deficiencies, outdated information, or areas for potential improvement.

4. **Manual Creation of Narrative Guides**: Develop narrative guides and tutorials that cover common use-cases, provide sample code, and explain more complex concepts in an easy-to-understand manner.

5. **Continued Updates and Maintenance**:  Ensure the process in step 1 is triggered each time the documentation site is built. This ensures that API reference documentation stays up-to-date with any changes in the source code. Regularly review and update narrative guides based on user feedback and changes in package functionality.