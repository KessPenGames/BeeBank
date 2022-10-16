from mojang import MojangAPI as api


def uuidToUsername(uuid: str):
    if uuid == "BBank":
        return uuid
    return api.get_username(uuid)


def usernameToUuid(username: str):
    if username == "BBank":
        return username
    return api.get_uuid(username)
