"""
Base Repository class with connection pooling and common database operations.
All repository classes inherit from this to avoid code duplication.
"""

import sqlite3
import threading
from queue import Queue
from typing import Optional, List, Dict, Any, Tuple

DB_NAME = 'focus_tracker.db'


class ConnectionPool:
    """Thread-safe connection pool for SQLite database."""
    
    def __init__(self, db_name: str = DB_NAME, pool_size: int = 5):
        self.db_name = db_name
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._initialized = False
        
    def initialize(self):
        """Initialize the connection pool with fresh connections."""
        if self._initialized:
            return
            
        with self.lock:
            if not self._initialized:
                for _ in range(self.pool_size):
                    conn = self._create_connection()
                    if conn:
                        self.pool.put(conn)
                self._initialized = True
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a single database connection."""
        try:
            conn = sqlite3.connect(self.db_name, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None
    
    def get_connection(self) -> Optional[sqlite3.Connection]:
        """Get a connection from the pool."""
        try:
            conn = self.pool.get_nowait()
            if conn:
                return conn
        except:
            pass
        
        # If pool is empty, create a new connection
        return self._create_connection()
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return a connection to the pool."""
        if conn:
            try:
                self.pool.put_nowait(conn)
            except:
                conn.close()
    
    def close_all(self):
        """Close all connections in the pool."""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                if conn:
                    conn.close()
            except:
                pass


# Global connection pool instance
_connection_pool = ConnectionPool(DB_NAME)


class BaseRepository:
    """
    Base repository class providing common database operations and connection management.
    All specific repositories inherit from this class.
    """
    
    @staticmethod
    def get_connection() -> Optional[sqlite3.Connection]:
        """Get a database connection from the pool."""
        return _connection_pool.get_connection()
    
    @staticmethod
    def return_connection(conn: sqlite3.Connection):
        """Return a connection to the pool."""
        _connection_pool.return_connection(conn)
    
    @staticmethod
    def initialize_pool(pool_size: int = 5):
        """Initialize the connection pool with given size."""
        _connection_pool.pool_size = pool_size
        _connection_pool.initialize()
    
    @staticmethod
    def close_pool():
        """Close all connections in the pool."""
        _connection_pool.close_all()
    
    @staticmethod
    def execute_query(
        query: str,
        params: Tuple = (),
        fetch_one: bool = False,
        fetch_all: bool = False,
        commit: bool = False
    ) -> Any:
        """
        Execute a database query with proper connection management.
        
        Args:
            query: SQL query string
            params: Query parameters (for parameterized queries)
            fetch_one: If True, return single row
            fetch_all: If True, return all rows
            commit: If True, commit changes to database
        
        Returns:
            Query result based on fetch_* parameters, or None on error
        """
        conn = BaseRepository.get_connection()
        if not conn:
            return None if fetch_all else ([] if fetch_all else None)
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            result = None
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            elif commit:
                result = cursor.lastrowid
            
            if commit:
                conn.commit()
            
            return result
            
        except sqlite3.Error as e:
            print(f"Database query error: {e}")
            return None if fetch_all else ([] if fetch_all else None)
        finally:
            BaseRepository.return_connection(conn)
    
    @staticmethod
    def execute_transaction(
        operations: List[Tuple[str, Tuple]],
        description: str = ""
    ) -> bool:
        """
        Execute multiple operations in a single transaction.
        
        Args:
            operations: List of (query, params) tuples
            description: Human-readable description for logging
        
        Returns:
            True if successful, False otherwise
        """
        conn = BaseRepository.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            for query, params in operations:
                cursor.execute(query, params)
            
            conn.commit()
            if description:
                print(f"✅ {description}")
            return True
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Transaction error ({description}): {e}")
            return False
        finally:
            BaseRepository.return_connection(conn)
    
    @staticmethod
    def get_lastrowid(query: str, params: Tuple = ()) -> Optional[int]:
        """
        Execute INSERT query and return the last inserted row ID.
        
        Args:
            query: SQL INSERT query
            params: Query parameters
        
        Returns:
            Last inserted row ID or None
        """
        conn = BaseRepository.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database insert error: {e}")
            return None
        finally:
            BaseRepository.return_connection(conn)


def initialize_database():
    """Initialize the database connection pool. Call this at application startup."""
    BaseRepository.initialize_pool(pool_size=5)
