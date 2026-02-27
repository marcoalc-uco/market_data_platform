"""Database integration tests.

Tests PostgreSQL container directly to verify:
- Database connectivity
- Schema structure (migrations)
- Data persistence
"""

import psycopg2
import psycopg2.extensions
import pytest


class TestDatabaseConnectivity:
    """Test database connection and basic operations."""

    def test_database_connection(
        self, db_connection: psycopg2.extensions.connection
    ) -> None:
        """Test that we can connect to PostgreSQL container."""
        assert db_connection is not None
        assert not db_connection.closed

    def test_can_execute_query(
        self, db_connection: psycopg2.extensions.connection
    ) -> None:
        """Test executing a simple query."""
        cursor = db_connection.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()

        assert result is not None
        assert result[0] == 1


class TestDatabaseSchema:
    """Test database schema created by Alembic migrations."""

    def test_instruments_table_exists(
        self, db_connection: psycopg2.extensions.connection
    ) -> None:
        """Test that instruments table exists."""
        cursor = db_connection.cursor()
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'instruments'
            )
        """
        )
        exists = cursor.fetchone()[0]
        cursor.close()

        assert exists is True

    def test_market_prices_table_exists(
        self, db_connection: psycopg2.extensions.connection
    ) -> None:
        """Test that market_prices table exists."""
        cursor = db_connection.cursor()
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'market_prices'
            )
        """
        )
        exists = cursor.fetchone()[0]
        cursor.close()

        assert exists is True

    def test_instruments_table_structure(
        self, db_connection: psycopg2.extensions.connection
    ) -> None:
        """Test instruments table has expected columns."""
        cursor = db_connection.cursor()
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'instruments'
            ORDER BY ordinal_position
        """
        )
        columns = [row[0] for row in cursor.fetchall()]
        cursor.close()

        expected_columns = [
            "id",
            "symbol",
            "name",
            "instrument_type",
            "exchange",
            "is_active",
            "created_at",
            "updated_at",
        ]
        assert all(col in columns for col in expected_columns)

    def test_market_prices_table_structure(
        self, db_connection: psycopg2.extensions.connection
    ) -> None:
        """Test market_prices table has expected columns."""
        cursor = db_connection.cursor()
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'market_prices'
            ORDER BY ordinal_position
        """
        )
        columns = [row[0] for row in cursor.fetchall()]
        cursor.close()

        expected_columns = [
            "id",
            "instrument_id",
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        assert all(col in columns for col in expected_columns)


class TestDataPersistence:
    """Test that data persists correctly in PostgreSQL."""

    def test_insert_and_query_instrument(
        self, db_connection: psycopg2.extensions.connection
    ) -> None:
        """Test inserting and querying an instrument directly in DB."""
        import uuid

        cursor = db_connection.cursor()

        # Use unique symbol to avoid conflicts
        test_symbol = f"DBTEST_{uuid.uuid4().hex[:8].upper()}"

        # Insert
        cursor.execute(
            """
            INSERT INTO instruments (symbol, name, instrument_type, exchange, is_active)
            VALUES (%s, 'Database Test', 'stock', 'NASDAQ', true)
            RETURNING id, symbol
        """,
            (test_symbol,),
        )
        db_connection.commit()

        result = cursor.fetchone()
        assert result is not None
        instrument_id, symbol = result
        assert symbol == test_symbol

        # Query
        cursor.execute(
            """
            SELECT symbol, name, instrument_type
            FROM instruments
            WHERE id = %s
        """,
            (instrument_id,),
        )

        result = cursor.fetchone()
        cursor.close()

        assert result is not None
        assert result[0] == test_symbol
        assert result[1] == "Database Test"
        assert result[2] == "stock"

    def test_foreign_key_constraint(
        self, db_connection: psycopg2.extensions.connection
    ) -> None:
        """Test that foreign key constraints are enforced."""
        cursor = db_connection.cursor()

        # Try to insert market price with non-existent instrument_id
        with pytest.raises(psycopg2.IntegrityError):
            cursor.execute(
                """
                INSERT INTO market_prices
                (instrument_id, timestamp, open, high, low, close, volume)
                VALUES (99999, NOW(), 100, 105, 99, 103, 1000000)
            """
            )
            db_connection.commit()

        db_connection.rollback()
        cursor.close()
