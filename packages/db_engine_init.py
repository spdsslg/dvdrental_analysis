from sqlalchemy import create_engine, URL
import os

#this function establishes the way we will talk with the db
def get_engine():
    """
    Create a SQLAlchemy Engine for PostgreSQL.

    If `db_url` is provided, it is used directly. Otherwise, the connection URL is
    built from environment variables PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE,
    falling back to sensible defaults.

    Parameters
    ----------
    db_url : str or None, optional
        Full SQLAlchemy URL like
        ``postgresql+psycopg2://user:pass@host:port/db``.
        If provided, environment variables are ignored.
    driver : {"psycopg2", "psycopg"}, optional
        PostgreSQL DBAPI driver to use. Default is "psycopg2".

    Returns
    -------
    sqlalchemy.engine.Engine
        A live Engine you can `.connect()` with.

    Raises
    ------
    sqlalchemy.exc.NoSuchModuleError
        If the requested driver is not installed.
    """


    url = URL.create(
        "postgresql+psycopg2",
        username = os.getenv("PGUSER", "postgres"),
        password = os.getenv("PGPASSWORD", "postgres"),
        host = os.getenv("PGHOST", "localhost"),
        port = int(os.getenv("PGPORT", "5432")),
        database = os.getenv("PGDATABASE", "dvdrental")
    )

    return create_engine(url, pool_pre_ping=True)
    