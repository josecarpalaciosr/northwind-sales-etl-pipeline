"""Inspect the structure and contents of the Northwind source database."""

from pathlib import Path
import sqlite3


# Build paths relative to the project root so the script works
# independently of where the repository is cloned.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "raw" / "northwind.db"


def get_table_names(connection: sqlite3.Connection) -> list[str]:
    """Return the names of all user-defined tables in the database."""

    # sqlite_master is SQLite's internal catalog of database objects.
    # Internal tables starting with sqlite_ are excluded.
    query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
    """

    cursor = connection.execute(query)
    rows = cursor.fetchall()
    
    # Each database row is a tuple such as ("Customers",).
    # Only the table name at position zero is needed.
    return [row[0] for row in rows]


def get_row_count(connection: sqlite3.Connection, table_name: str,) -> int:
    """Return the total number of rows in the specified table."""

    # Table names come from sqlite_master rather than user input.
    query = f'SELECT COUNT(*) FROM "{table_name}";'

    cursor = connection.execute(query)
    row = cursor.fetchone()

    return row[0]

def get_table_columns(connection: sqlite3.Connection,table_name: str,) -> list[tuple]:
    """Return column metadata for the specified table."""

    # PRAGMA table_info returns the name, data type, nullability, (cid, name, type, notnull, default_value, pk)
    # default value, and primary-key status of every column.
    query = f'PRAGMA table_info("{table_name}");'

    cursor = connection.execute(query)

    return cursor.fetchall()

def get_foreign_keys(connection: sqlite3.Connection,table_name: str,) -> list[tuple]:
    """Return foreign-key metadata for the specified table."""

    # PRAGMA foreign_key_list describes relationships declared
    # between the current table and other tables. (id, seq, table, from, to, on_update, on_delete, match)
    query = f'PRAGMA foreign_key_list("{table_name}");'

    cursor = connection.execute(query)

    return cursor.fetchall()

def main() -> None:
    """Inspect the Northwind database and print a summary of its tables."""

    # Fail early instead of allowing SQLite to create an empty database
    # when the expected source file is missing.
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Northwind database not found: {DATABASE_PATH}"
        )

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        table_names = get_table_names(connection)

        print(f"Database: {DATABASE_PATH}")
        print(f"Tables found: {len(table_names)}")

        # Print the number of records available in every business table.
        for table_name in table_names:
            row_count = get_row_count(connection, table_name)
            columns = get_table_columns(connection, table_name)
            foreign_keys = get_foreign_keys(connection, table_name)

            print(f"\n{table_name} ({row_count:,} rows)")

            for column in columns:
                (
                    _column_id,
                    column_name,
                    data_type,
                    not_null,
                    _default_value,
                    primary_key,
                ) = column

                constraints = []

                if primary_key:
                    constraints.append("PRIMARY KEY")

                if not_null:
                    constraints.append("NOT NULL")

                constraint_text = (
                    f" [{', '.join(constraints)}]"
                    if constraints
                    else ""
                )

                print(
                    f"  - {column_name}: {data_type}"
                    f"{constraint_text}"
                )
            if foreign_keys:
                print(
                    f"  Foreign keys ({table_name}): "
                    f"{len(foreign_keys)}"
                )

                for foreign_key in foreign_keys:
                    (
                        _foreign_key_id,
                        _sequence,
                        referenced_table,
                        source_column,
                        referenced_column,
                        _on_update,
                        _on_delete,
                        _match_type,
                    ) = foreign_key

                    print(
                        f"    - {source_column} -> "
                        f"{referenced_table}.{referenced_column}"
                    )

    finally:
        # Always release the database connection, even if an error occurs.
        connection.close()


if __name__ == "__main__":
    main()