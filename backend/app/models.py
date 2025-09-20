from __future__ import annotations

import os
import re
from typing import Optional, Tuple

from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy database instance
db = SQLAlchemy()


def _parse_mysql_connection_from_db_file(file_path: str) -> Optional[Tuple[str, str, str, str, Optional[int]]]:
    """
    Attempt to parse a mysql CLI string from db_connection.txt and extract connection parts.

    Supported format example:
      mysql -uUSER -pPASSWORD -hHOST -PPORT DBNAME
      mysql -uUSER -pPASSWORD DBNAME
    Returns tuple: (user, password, host, database, port) or None if not parseable.
    """
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception:
        return None

    # Extract -u and -p, optional -h and -P, and final token as database
    user_match = re.search(r"-u(\S+)", content)
    pass_match = re.search(r"-p(\S+)", content)
    host_match = re.search(r"-h(\S+)", content)
    port_match = re.search(r"-P(\d+)", content)

    # DB name is typically the last non-flag token
    tokens = content.split()
    dbname = None
    for tok in reversed(tokens):
        if tok.startswith("-"):
            continue
        # skip 'mysql' if it appears last
        if tok.lower() == "mysql":
            continue
        dbname = tok
        break

    if not (user_match and pass_match and dbname):
        return None

    user = user_match.group(1)
    password = pass_match.group(1)
    host = host_match.group(1) if host_match else "localhost"
    port = int(port_match.group(1)) if port_match else None
    return user, password, host, dbname, port


def build_mysql_uri_from_env_or_file() -> str:
    """
    Builds a SQLAlchemy MySQL URI from environment variables or from db_connection.txt.
    Environment variables:
      - MYSQL_URL (full SQLAlchemy URL, takes precedence if present)
      - MYSQL_USER
      - MYSQL_PASSWORD
      - MYSQL_DB
      - MYSQL_HOST (default: localhost)
      - MYSQL_PORT (default: 3306)

    If env vars are insufficient, attempts to parse db_connection.txt located at:
      ../../music-center-student-registration-87320-87330/music_center_student_database/db_connection.txt
    """
    # 1) Full URL if provided
    mysql_url = os.getenv("MYSQL_URL")
    if mysql_url:
        return mysql_url

    # 2) Build from discrete env parts
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DB")
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")

    if user and password and database:
        # Use PyMySQL dialect explicitly
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"

    # 3) Fallback to db_connection.txt (read-only safe)
    # The sibling workspace typically holds db_connection.txt
    # Project root: /home/kavia/workspace/code-generation/
    # Current backend root: music-center-student-registration-87320-87331/backend
    # Database container root: music-center-student-registration-87320-87330/music_center_student_database
    candidate_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "music-center-student-registration-87320-87330",
            "music_center_student_database",
            "db_connection.txt",
        )
    )
    parsed = _parse_mysql_connection_from_db_file(candidate_path)
    if parsed:
        p_user, p_pass, p_host, p_db, p_port = parsed
        p_port = p_port or 3306
        return f"mysql+pymysql://{p_user}:{p_pass}@{p_host}:{p_port}/{p_db}?charset=utf8mb4"

    # 4) Final fallback: raise descriptive error
    raise RuntimeError(
        "Unable to construct MySQL connection URI. Please set MYSQL_URL or MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB "
        "and optional MYSQL_HOST, MYSQL_PORT in environment, or ensure db_connection.txt is available."
    )


# Student model
class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    instrument = db.Column(db.String(80), nullable=True)
    experience_level = db.Column(db.String(50), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "instrument": self.instrument,
            "experience_level": self.experience_level,
        }
