# ChatLab

**Chat Experiments, Simplified**

💬🔬

ChatLab is a Python package that makes it easy to experiment with OpenAI's chat models. It provides a simple interface for chatting with the models and a way to register functions that can be called from the chat model.

Best yet, it's interactive in the notebook!

⚠️ NOTE: The following docs are for `main`. Check out [chatlab.dev](https://chatlab.dev) for the docs for the most recent release. 

## Introduction

```python
import chatlab
import random

def flip_a_coin():
    '''Returns heads or tails'''
    return random.choice(['heads', 'tails'])

chat = chatlab.Chat()
chat.register(flip_a_coin)

await chat("Please flip a coin for me")
```

<details style="background:#DDE6ED;color:#27374D;padding:.5rem 1rem;borderRadius:5px">
<summary>&nbsp;𝑓&nbsp; Ran `flip_a_coin`
</summary>
<br />

Input:

```json
{}
```

Output:

```json
"tails"
```

</details>

```markdown
It landed on tails!
```

In the notebook, text will stream into a Markdown output and function inputs and outputs are a nice collapsible display, like with ChatGPT Plugins.

TODO: Include GIF/mp4 of this in action

### Installation

```bash
pip install chatlab
```

### Configuration

You'll need to set your `OPENAI_API_KEY` environment variable. You can find your API key on your [OpenAI account page](https://platform.openai.com/account/api-keys). I recommend setting it in an `.env` file when working locally.

On hosted environments like Noteable, set it in your Secrets to keep it safe from prying LLM eyes.

## What can `Chat`s enable _you_ to do?

💬

Where `Chat`s take it next level is with _Chat Functions_. You can

-   declare a function
-   register the function in your `Chat`
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

chat = chatlab.Chat()

# Register our function
chat.register(what_time, WhatTime)
```

After that, we can call `chat` with direct strings (which are turned into user messages) or using simple message makers from `chatlab` named `user` and `system`.

```python
await chat("What time is it?")
```

<details style="background:#DDE6ED;color:#27374D;padding:.5rem 1rem;borderRadius:5px">
<summary>&nbsp;𝑓&nbsp; Ran `what_time`
</summary>
<br />

Input:

```json
{}
```

Output:

```json
"11:19 AM"
```

</details>

```markdown
The current time is 11:19 AM.
```

## Interface

The `chatlab` package exports

### `Chat`

The `Chat` class is the main way to chat using OpenAI's models. It keeps a history of your chat in `Chat.messages`.

#### `Chat.submit`

`submit` is how you send all the currently built up messages over to OpenAI. Markdown output will display responses from the `assistant`.

```python
await chat.submit('What would a parent who says "I have to play zone defense" mean? ')
# Markdown response inline
chat.messages
```

```js
[{'role': 'user',
  'content': 'What does a parent of three kids mean by "I have to play zone defense"?'},
 {'role': 'assistant',
  'content': 'When a parent of three kids says "I have to play zone defense," it means that they...
```

#### `Chat.register`

You can register functions with `Chat.register` to make them available to the chat model. The function's docstring becomes the description of the function while the schema is derived from the `pydantic.BaseModel` passed in.

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

chat.register(what_time, WhatTime)
```

#### `Chat.messages`

The raw messages sent and received to OpenAI. If you hit a token limit, you can remove old messages from the list to make room for more.

```python
chat.messages = chat.messages[-100:]
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

We use `ruff` and `mypy`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
