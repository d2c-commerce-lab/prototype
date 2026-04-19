from backend.db.connection import check_db_connection

def test_postgresql_connection() -> None:
    assert check_db_connection() is True