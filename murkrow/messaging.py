# OpenAI role helpers


def assistant(message):
    return {
        'role': 'assistant',
        'content': message,
    }


def user(message):
    return {
        'role': 'user',
        'content': message,
    }


def system(message):
    return {
        'role': 'system',
        'content': message,
    }


# Aliases
def narrate(message):
    return system(message)


def human(message):
    return user(message)


def ai(message):
    return assistant(message)
