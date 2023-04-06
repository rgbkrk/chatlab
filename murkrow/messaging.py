# OpenAI role helpers


def assistant(message):
    return {
        'role': 'assistant',
        'message': message,
    }


def user(message):
    return {
        'role': 'user',
        'message': message,
    }


def system(message):
    return {
        'role': 'system',
        'message': message,
    }


# Aliases
def narrate(message):
    return system(message)


def human(message):
    return user(message)


def ai(message):
    return assistant(message)
