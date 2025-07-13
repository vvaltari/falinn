def make_user_payload(override: dict = {}, exclude: list = []) -> dict:
    payload = {
        'name': 'Test User',
        'last_name': 'Test User',
        'email': 'test@example.com',
        'password': 'string',
    }

    for key in override:
        payload[key] = override[key]

    for item in exclude:
        payload.pop(item, None)

    return payload

def make_sign_in_payload(username: str = 'random@mail.com', password: str = 'randompass', exclude: list = []) -> dict:
    payload = {
        'username': username,
        'password': password,
    }

    for item in exclude:
        payload.pop(item, None)

    return payload