from apps.api.backend.db.connection import check_db_connection

if __name__ == "__main__":
    ok = check_db_connection()
    print("DB connection:", "OK" if ok else "FAILED")