import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secret")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@db:5432/recommendation_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.getenv("REDIS_URL")
    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")