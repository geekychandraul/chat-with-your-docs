import bcrypt


def hash_password(password):
    # Passwords must be bytes
    password_bytes = password.encode("utf-8")
    # Generate a salt and hash the password in one step
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    # Decode to string for storage in a database (e.g., as a VARCHAR)
    return hashed_bytes.decode("utf-8")


def verify_password(entered_password, stored_hash):
    # Encode entered password to bytes
    entered_password_bytes = entered_password.encode("utf-8")
    # Encode stored hash to bytes
    stored_hash_bytes = stored_hash.encode("utf-8")

    # checkpw handles the salting and hashing automatically and returns True or False
    if bcrypt.checkpw(entered_password_bytes, stored_hash_bytes):
        return True
    else:
        return False
