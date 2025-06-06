import pytest
from jose import jwt
from src.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)


def test_password_hashing_and_verification():
    """
    Tests that a password can be hashed and then successfully verified.
    Also tests that verification fails for an incorrect password.
    """
    password = "a_strong_password"
    hashed_password = get_password_hash(password)

    # The hash should not be the same as the original password
    assert password != hashed_password

    # Verification should succeed with the correct password
    assert verify_password(password, hashed_password) is True

    # Verification should fail with an incorrect password
    assert verify_password("not_the_right_password", hashed_password) is False


def test_jwt_token_creation_and_decoding():
    """
    Tests that a JWT access token can be created with the correct data
    and then decoded successfully to retrieve that same data.
    """
    username = "testuser"
    data_to_encode = {"sub": username}

    # Create the token
    token = create_access_token(data=data_to_encode)

    assert isinstance(token, str)

    # Decode the token
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    # Check that the decoded data matches the original data
    decoded_username = payload.get("sub")
    assert decoded_username == username

    # Check that an expiration time was added
    assert "exp" in payload