# OpenAI role helpers


def ai(message):
    return {
        'role': 'assistant',
        'message': message,
    }


def human(message, name=None):
    return {
        'role': 'human',
        'message': message,
    }


def system(message):
    return {
        'role': 'system',
        'message': message,
    }


def create_named_human(name):
    return lambda message: human(message, name=name)
