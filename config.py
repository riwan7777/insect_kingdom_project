import os

# Values can be overridden with environment variables in production
# (e.g. on Render/Heroku). Local defaults match the original project
# so nothing breaks for local MySQL development.
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "Rizwan@123"),
    "database": os.environ.get("DB_NAME", "insect_store"),
}

SECRET_KEY = os.environ.get("SECRET_KEY", "insect_kingdom_secret_key_change_this")
