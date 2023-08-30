---
title: Setting API Keys
description: How to set your API keys for OpenAI and ChatLab
sidebar_position: 2
---

# Setting API Keys

Since ChatLab builds upon OpenAI's Chat Models and Function Calling, you must sign up with [OpenAI](https://platform.openai.com/) and get an API key. You can find your API key on your [OpenAI account page](https://platform.openai.com/account/api-keys). Once you have your key, set it to the `OPENAI_API_KEY` environment variable.

## Jupyter

Before launching JupyterLab (or the classic notebook), set the `OPENAI_API_KEY` environment variable.

```bash
export OPENAI_API_KEY=<your key>
jupyter lab
```

As an alternative, you can use the [dotenv](https://pypi.org/project/python-dotenv/) package to load the environment variable from a `.env` file.

```bash
pip install python-dotenv
```

Create a `.env` file in the same directory as your notebook and add the following line.

```bash
OPENAI_API_KEY=<your key>
```

## Noteable

Navigate to your [Secrets](https://app.noteable.io/r/secrets) page, click "Create a Secret" and add your key.

![](/img/noteable_secrets_ui.png)

Name: `OPENAI_API_KEY`
Value: `<your key>`

The "Private" option provides the secrets to only you when executing. "Space" level secrets will be available to all your collaborators in the space.

## Colab, Kaggle, and other cloud notebooks

### Just `getpass`

This is the most secure way to set your API key that works with all notebooks. It will prompt you for your key every time you run a notebook. This is the recommended way to set your API key if other methods do not work.

```python
import os
from getpass import getpass
os.environ['OPENAI_API_KEY'] = getpass('Enter your OpenAI API Key: ')
```

### The `%env` magic

This options is insecure, but easy. It will leave your key in the notebook for others to see. This is **not** recommended for sharing notebooks.

:::danger

If you absolutely, positively have to, you can set the `OPENAI_API_KEY` environment variable in the notebook with the `%env` magic.

```python
%env OPENAI_API_KEY=<your key>
```

:::

Good luck!
