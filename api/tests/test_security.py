import os
import pytest
from sqlmodel import Session, create_engine, SQLModel, select
from app import main
from app.crypto import encrypt_password, decrypt_password, is_encrypted

def test_encryption_decryption():
    pw = "secret_password"
    encrypted = encrypt_password(pw)
    assert encrypted != pw
    assert is_encrypted(encrypted)
    assert decrypt_password(encrypted) == pw

def test_migration(tmp_path):
    # Setup a temporary database for testing migration
    db_file = tmp_path / "test_migration.db"
    test_engine = create_engine(f"sqlite:///{db_file}")
    SQLModel.metadata.create_all(test_engine)

    # Add a camera with plaintext password
    with Session(test_engine) as session:
        cam = main.Camera(name="Test Cam", ip="1.2.3.4", password="plaintext_pw")
        session.add(cam)
        session.commit()

    # Mock the global engine in main.py for startup migration test
    original_engine = main.engine
    main.engine = test_engine

    try:
        # Run startup which includes migration
        main.startup()

        # Verify password is now encrypted
        with Session(test_engine) as session:
            cam = session.exec(select(main.Camera).where(main.Camera.ip == "1.2.3.4")).one()
            assert cam.password != "plaintext_pw"
            assert is_encrypted(cam.password)
            assert decrypt_password(cam.password) == "plaintext_pw"
    finally:
        main.engine = original_engine

def test_worker_decryption():
    # Verify worker can decrypt what API encrypts
    # In this test environment, they share the same key mechanism
    pw = "worker_secret"
    encrypted = encrypt_password(pw)

    from worker.crypto import decrypt_password as worker_decrypt
    assert worker_decrypt(encrypted) == pw
