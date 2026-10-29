import os
import unittest

os.environ.setdefault("SECRET_KEY", "test-only-secret")
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SOCKETIO_ASYNC_MODE"] = "threading"

from app import app, socketio
from models import Group, Message, User, db


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def register(self, username="alice", email="alice@example.test", password="correct-horse"):
        return self.client.post(
            "/register",
            json={"username": username, "email": email, "password": password},
        )

    def login(self, email="alice@example.test", password="correct-horse"):
        return self.client.post("/login", json={"email": email, "password": password})

    def test_registration_hashes_password_and_login_succeeds(self):
        self.assertEqual(self.register().status_code, 201)

        with app.app_context():
            user = User.query.filter_by(email="alice@example.test").one()
            self.assertNotEqual(user.password, "correct-horse")
            self.assertGreater(len(user.password), 60)

        self.assertEqual(self.login().status_code, 200)

    def test_legacy_plaintext_password_is_upgraded_after_login(self):
        with app.app_context():
            db.session.add(
                User(username="legacy", email="legacy@example.test", password="legacy-pass")
            )
            db.session.commit()

        response = self.login(email="legacy@example.test", password="legacy-pass")
        self.assertEqual(response.status_code, 200)

        with app.app_context():
            user = User.query.filter_by(email="legacy@example.test").one()
            self.assertNotEqual(user.password, "legacy-pass")
            self.assertTrue(user.password.startswith(("scrypt:", "pbkdf2:")))

    def test_socket_message_uses_authenticated_session_identity(self):
        self.assertEqual(self.register().status_code, 201)
        self.assertEqual(self.login().status_code, 200)

        with app.app_context():
            group = Group(name="general")
            db.session.add(group)
            db.session.commit()
            group_id = group.id
            user_id = User.query.filter_by(email="alice@example.test").one().id

        socket_client = socketio.test_client(app, flask_test_client=self.client)
        self.assertTrue(socket_client.is_connected())
        socket_client.emit(
            "send_message",
            {"content": "hello", "group_id": group_id, "user_id": user_id + 999},
        )
        socket_client.disconnect()

        with app.app_context():
            message = Message.query.one()
            self.assertEqual(message.user_id, user_id)


if __name__ == "__main__":
    unittest.main()
