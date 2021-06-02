import os
import base64
from pathlib import Path

from cryptography.fernet import Fernet

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def encrypt_with_password(data, password):
    assert type(data) == bytes
    assert type(password) == bytes
    salt = b'-!\xdc5J\xf1\xc6\xfa\x85\xa4>z\xfd\x82s\xfc'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    return f.encrypt(data)


def decrypt_with_password(data, password):
    assert type(data) == bytes
    assert type(password) == bytes
    salt = b'-!\xdc5J\xf1\xc6\xfa\x85\xa4>z\xfd\x82s\xfc'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    return f.decrypt(data)


def test_password_enc():
    password = os.urandom(16)
    data = os.urandom(4096)

    e = encrypt_with_password(data, password)
    d = decrypt_with_password(e, password)

    assert e != data
    assert d == data
    print("Symetrical password encryption works!")


##### ASYM #####


def read_private(filename=Path("../../private_image_encryption_key.pem")):
    with open(filename, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key


def read_public(filename=Path("openface_data/public_image_encryption_key.pem")):
    # TODO maybe do something like this
    # https://stackoverflow.com/questions/3701404/how-can-i-list-all-commits-that-changed-a-specific-file
    # or hash of the key or something
    with open(filename, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key


def encrypt_file(file, delete=True):
    file = Path(file)
    data = file.read_bytes()

    temp_password = os.urandom(32)

    # encrypt the data using the temp password and save it
    enc_data = encrypt_with_password(data, temp_password)
    enc_file = Path(str(file) + ".enc")
    enc_file.write_bytes(enc_data)

    public_key = read_public()
    enc_password = public_key.encrypt(
        temp_password,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))
    pwd_file = Path(str(enc_file) + ".pwd")
    pwd_file.write_bytes(enc_password)

    if delete:
        file.unlink()

    return enc_file


def decrypt_file(file, delete=True):
    file = Path(file)
    enc_data = file.read_bytes()
    pwd_file = Path(str(file) + ".pwd")
    enc_pwd = pwd_file.read_bytes()

    private_key = read_private()
    password = private_key.decrypt(
        enc_pwd,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))

    data = decrypt_with_password(enc_data, password)
    dec_file = Path(str(file)[:-4])
    dec_file.write_bytes(data)

    if delete:
        file.unlink()

    return dec_file


if __name__ == "__main__":
    test_password_enc()
