def load_users(hcy, name=None):
    _user = {}
    with open(hcy, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            key_value = line.split(": ")
            key, value = (key_value[0], key_value[1]) if len(key_value) > 1 else (key_value[0], "")
            if name and name != key:
                continue
            _user[key] = value.strip('\n')
    return _user.items()
