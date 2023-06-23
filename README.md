# ChatLab

**Chat Experiments, Simplified**

💬🔬

Chatlab is where chat conversations take shape. It’s your laboratory for experimenting with and crafting intelligent conversations using OpenAI’s chat models.

## Introduction

Welcome to Chatlab, your personal workshop for chat innovation. Are you intrigued by conversational AI? Chatlab empowers developers to mold conversations according to their vision. Whether you are an AI enthusiast, researcher, or developer, Chatlab provides you with the building blocks and tools necessary for crafting intelligent conversations seamlessly. 🧪💬

```python
import chatlab

conversation = chatlab.Conversation()

conversation.submit("How much wood could a")
```

```markdown
woodchuck chuck if a woodchuck could chuck wood?
```

In the notebook, text will stream into a Markdown output.

![image](https://github.com/rgbkrk/chatlab/assets/836375/81b2837c-430c-42eb-ae60-0c3a91ae26b6)

When using chat functions in the notebook\*, you'll get a nice collapsible display of inputs and outputs.

![click](https://github.com/rgbkrk/chatlab/assets/836375/21c6bd4c-cd3b-48b9-812a-2b86a05c20da)

\* Tested in JupyterLab and Noteable

### Installation

```bash
pip install chatlab
```

### Configuration

You'll need to set your `OPENAI_API_KEY` environment variable. You can find your API key on your [OpenAI account page](https://platform.openai.com/account/api-keys). I recommend setting it in an `.env` file when working locally.

On hosted environments like Noteable, set it in your Secrets to keep it safe from prying LLM eyes.

## What can `Conversation`s enable _you_ to do?

<center><img src="https://cdn.donmai.us/original/64/e7/64e78d7968c8317b84a95e152e4a087b.png" height="100" /></center>
<br />

Where `Conversation`s take it next level is with _Chat Functions_. You can

-   declare a function with a schema
-   register the function in your `Conversation`
-   watch as Chat Models call your functions!

You may recall this kind of behavior from [ChatGPT Plugins](https://noteable.io/chatgpt-plugin-for-notebook/). Now, you can take this even further with your own custom code.

As an example, let's give the large language models the ability to tell time.

```python
from datetime import datetime
from pytz import timezone, all_timezones, utc
from typing import Optional
from pydantic import BaseModel

def what_time(tz: Optional[str] = None):
    '''Current time, defaulting to UTC'''
    if tz is None:
        pass
    elif tz in all_timezones:
        tz = timezone(tz)
    else:
        return 'Invalid timezone'

    return datetime.now(tz).strftime('%I:%M %p')

class WhatTime(BaseModel):
    tz: Optional[str] = None
```

Let's break this down.

`what_time` is the function we're going to provide access to. Its docstring forms the `description` for the model while the schema comes from the pydantic `BaseModel` called `WhatTime`.

```python
import chatlab

conversation = chatlab.Conversation()

# Register our function
conversation.register(what_time, WhatTime)

# Pluck the submit off for easy access as chat
chat = conversation.submit
```

After that, we can call `chat` with direct strings (which are turned into user messages) or using simple message makers from `chatlab` named `human`/`user` and `narrate`/`system`.

```python
chat("What time is it?")
```

```markdown
▶ 𝑓 Ran `what_time`

The current time is 11:47 PM.
```

## Interface

The `chatlab` package exports

### `Conversation`

The `Conversation` class is the main way to chat using OpenAI's models. It keeps a history of your chat in `Conversation.messages`.

#### `Conversation.submit`

When you call `submit`, you're sending over messages to the chat model and getting back an updating `Markdown` display live as well as a interactive details area for any function calls.

```python
conversation.submit("What would a parent who says "I have to play zone defense" mean? ")
# Markdown response inline
conversation.messages
```

```js
[{'role': 'user',
  'content': 'What does a parent of three kids mean by "I have to play zone defense"?'},
 {'role': 'assistant',
  'content': 'When a parent of three kids says "I have to play zone defense," it means that they...
```

#### `Conversation.register`

You can register functions with `Conversation.register` to make them available to the chat model. The function's docstring becomes the description of the function while the schema is derived from the `pydantic.BaseModel` passed in.

```python
from pydantic import BaseModel

class WhatTime(BaseModel):
    tz: Optional[str] = None

def what_time(tz: Optional[str] = None):
    '''Current time, defaulting to UTC'''
    if tz is None:
        pass
    elif tz in all_timezones:
        tz = timezone(tz)
    else:
        return 'Invalid timezone'

    return datetime.now(tz).strftime('%I:%M %p')

conversation.register(what_time, WhatTime)
```

#### `Conversation.messages`

The raw messages sent and received to OpenAI. If you hit a token limit, you can remove old messages from the list to make room for more.

```python
conversation.messages = conversation.messages[-100:]
```

### Messaging

#### `human`/`user`

These functions create a message from the user to the chat model.

```python
from chatlab import human

human("How are you?")
```

```json
{ "role": "user", "content": "How are you?" }
```

#### `narrate`/`system`

`system` messages, also called `narrate` in `chatlab`, allow you to steer the model in a direction. You can use these to provide context without being seen by the user. One common use is to include it as initial context for the conversation.

```python
from chatlab import narrate

narrate("You are a large bird")
```

```json
{ "role": "system", "content": "You are a large bird" }
```

## Development

This project uses poetry for dependency management. To get started, clone the repo and run

```bash
poetry install -E dev -E test
```

We use `black`, `isort`, and `mypy`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
