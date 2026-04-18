import logging
from psycopg2.extras import execute_values
import psycopg2
from config import Config

logger = logging.getLogger(__name__)


class DatabaseLoader:
    def __init__(self):
        self.config = Config()
        self.dsn = self.config.dsn
        self.database = self.config.database
        self.schema = self.config.schema
        self.table_name = self.config.table_name

        self._conn = None

    @property
    def create_table_sql(self):

        columns_datatype_map = self.config.table_columns_datatype_map

        columns_list = "\n".join(
            [
                f"{column_name} {datatype},"
                for column_name, datatype in columns_datatype_map.items()
            ]
        )

        primary_keys = ",".join(self.config.primary_key)
        return f"""
            CREATE TABLE IF NOT EXISTS  {self.database}.{self.schema}.{self.table_name} (
                {columns_list}
                PRIMARY KEY ({primary_keys})
            );
        """

    @property
    def insert_sql(self):
        columns = ",".join(self.config.table_columns_datatype_map.keys())
        return f"""
            INSERT INTO {self.database}.{self.schema}.{self.table_name} ({columns})
            VALUES %s
            ON CONFLICT DO NOTHING;
        """

    def connect(self):
        self._conn = psycopg2.connect(self.dsn)
        logger.info("Connected to PostgreSQL.")

    def disconnect(self):
        if self._conn and not self._conn.closed:
            self._conn.close()
            logger.info("Disconnected from PostgreSQL.")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False

    def ensure_table(self):
        with self._conn.cursor() as cur:
            cur.execute(self.create_table_sql)
        self._conn.commit()
        logger.debug("Table '%s' is ready.", self.table_name)

    @staticmethod
    def _to_rows(record: dict) -> list[tuple]:
        return [
            (
                record["id"],
                record["mail"],
                record["name"],
                leg["departure"],
                leg["destination"],
                leg["start_timestamp"],
                leg["end_timestamp"],
            )
            for leg in record["trip"]
        ]

    def load(self, records: list[dict]) -> int:
        if not records:
            logger.warning("load() called with an empty list — nothing to insert.")
            return 0

        rows = []
        for record in records:
            try:
                rows.extend(self._to_rows(record))
            except (KeyError, TypeError) as e:
                logger.error("Skipping malformed record %s: %s", record.get("id"), e)

        if not rows:
            logger.warning("No valid rows to insert after filtering.")
            return 0

        with self._conn.cursor() as cur:
            execute_values(cur, self.insert_sql, rows)
            inserted = cur.rowcount
        self._conn.commit()

        logger.info(
            "Inserted %d/%d rows into '%s'.", inserted, len(rows), self.table_name
        )
        return inserted
