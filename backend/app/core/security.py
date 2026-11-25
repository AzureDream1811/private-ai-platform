from bcrypt import checkpw, gensalt, hashpw


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) <= 0:
        raise ValueError("Password can not be empty")
    
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password cannot be longer than 72 characters")
    
    return str(hashpw(password.encode("utf-8"), salt=gensalt()), "utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
