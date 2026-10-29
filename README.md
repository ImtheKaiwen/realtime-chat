# Real-Time Chat Prototype

A Flask and Socket.IO chat prototype with registration, login, channels, group messages, and a responsive browser interface. SQLAlchemy stores users, groups, and messages in SQLite by default or in a database configured through `DATABASE_URL`.

## Features

- Account registration and session-based login
- Channel creation and group conversations
- Real-time Socket.IO messages
- Flask templates with JavaScript and CSS assets
- SQLite development storage with optional external database configuration

## Local setup

Create and activate a Python virtual environment, then install the declared dependencies:

```bash
python -m venv .venv
pip install -r requirements.txt
```

Set a strong, unique `SECRET_KEY`. Optionally set `DATABASE_URL`; otherwise Flask-SQLAlchemy uses `instance/site.db`.
`SOCKETIO_ASYNC_MODE` may be set to `threading` for local development; when omitted, Flask-SocketIO selects an available async backend.

PowerShell example:

```powershell
$env:SECRET_KEY = "replace-with-a-random-secret"
python app.py
```

Open `http://localhost:5000` after the server starts.

Run the authentication and Socket.IO identity tests with:

```bash
python -m unittest discover -s tests
```

## Security notes

- New passwords are stored with Werkzeug password hashing.
- Legacy plaintext password rows are upgraded to a hash after the first successful login.
- Socket.IO uses same-origin checks and derives the sender identity from the authenticated session.
- Runtime databases, caches, virtual environments, and `.env` files are ignored.
- A previously tracked SQLite database was removed from the current branch, but it remains in earlier Git history. Treat any real data it contained as previously exposed and rotate affected credentials if applicable.

Changing the password column from 60 to 255 characters requires a database migration for an existing database that enforces column lengths. Fresh local databases are created with the updated schema.

## Project structure

```text
.
├── app.py            # Flask and Socket.IO application
├── config.py         # Environment-driven configuration
├── models.py         # SQLAlchemy models and password helpers
├── routes.py         # HTTP routes
├── templates/        # Page templates
├── static/           # Browser JavaScript and CSS
└── requirements.txt
```

## Status

This is a learning prototype, not a production-ready chat service. Its automated coverage is limited to core authentication and Socket.IO identity checks, and it has no CSRF protection, rate limiting, migration framework, or documented operational monitoring. Review those areas before any public deployment.

No license file is currently included in this repository.
