import os
import sys
import time
import json
from pathlib import Path

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Monkey patch / instrument services.db to record metrics
import services.db as db_mod

orig_get_db = db_mod.get_db

stats = {
    "connections": 0,
    "connection_time": 0.0,
    "queries": 0,
    "sql_time": 0.0,
}

class InstrumentedCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        t0 = time.perf_counter()
        if params is None:
            res = self._cursor.execute(query)
        else:
            res = self._cursor.execute(query, params)
        dt = time.perf_counter() - t0
        stats["queries"] += 1
        stats["sql_time"] += dt
        return res

    def executemany(self, query, seq_of_params):
        t0 = time.perf_counter()
        res = self._cursor.executemany(query, seq_of_params)
        dt = time.perf_counter() - t0
        stats["queries"] += 1
        stats["sql_time"] += dt
        return res

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchmany(self, size=None):
        return self._cursor.fetchmany(size)

    def close(self):
        self._cursor.close()

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def description(self):
        return self._cursor.description

    @property
    def __getattr__(self, name):
        return getattr(self._cursor, name)

class InstrumentedConnection:
    def __init__(self, conn):
        self._conn = conn

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def cursor(self):
        return InstrumentedCursor(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def execute(self, query, params=None):
        cur = self.cursor()
        cur.execute(query, params)
        return cur

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

def instrumented_get_db():
    t0 = time.perf_counter()
    conn = orig_get_db()
    dt = time.perf_counter() - t0
    stats["connections"] += 1
    stats["connection_time"] += dt
    return InstrumentedConnection(conn)

db_mod.get_db = instrumented_get_db

from app import app

def reset_stats():
    stats["connections"] = 0
    stats["connection_time"] = 0.0
    stats["queries"] = 0
    stats["sql_time"] = 0.0

def measure_endpoint(client, endpoint):
    reset_stats()
    t_start = time.perf_counter()
    response = client.get(endpoint)
    total_time = time.perf_counter() - t_start

    # Estimate serialization time by measuring json dumps of data
    t_ser_0 = time.perf_counter()
    try:
        _ = json.dumps(response.get_json())
    except Exception:
        pass
    ser_time = time.perf_counter() - t_ser_0

    calc_time = max(0.0, total_time - stats["connection_time"] - stats["sql_time"] - ser_time)

    result = {
        "endpoint": endpoint,
        "status_code": response.status_code,
        "total_time_ms": round(total_time * 1000, 2),
        "db_connections": stats["connections"],
        "db_connection_time_ms": round(stats["connection_time"] * 1000, 2),
        "sql_queries": stats["queries"],
        "sql_execution_time_ms": round(stats["sql_time"] * 1000, 2),
        "business_calc_time_ms": round(calc_time * 1000, 2),
        "serialization_time_ms": round(ser_time * 1000, 2),
    }
    return result

def main():
    endpoints = [
        "/api/state",
        "/api/manage/reset/preview",
        "/api/manage/records",
        "/api/manage/uploads",
        "/api/reports/business-report",
    ]

    print("==================================================")
    print("BASELINE PERFORMANCE PROFILING (LOCAL / NEON)")
    print(f"DATABASE_URL: {bool(db_mod.get_database_url())} (is_postgres: {db_mod.is_postgres()})")
    print("==================================================")

    app.config["TESTING"] = True
    with app.test_client() as client:
        results = []
        for ep in endpoints:
            print(f"Measuring {ep} ...", flush=True)
            res = measure_endpoint(client, ep)
            results.append(res)
            print(f"  -> Status: {res['status_code']}")
            print(f"  -> Total: {res['total_time_ms']} ms")
            print(f"  -> DB Connections: {res['db_connections']} ({res['db_connection_time_ms']} ms)")
            print(f"  -> SQL Queries: {res['sql_queries']} ({res['sql_execution_time_ms']} ms)")
            print(f"  -> Business Calc: {res['business_calc_time_ms']} ms")
            print(f"  -> Serialization: {res['serialization_time_ms']} ms")
            print("-" * 50)

    # Save to file
    with open("scripts/baseline_metrics.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nSaved baseline metrics to scripts/baseline_metrics.json")

if __name__ == "__main__":
    main()
