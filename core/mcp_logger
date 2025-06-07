import sqlite3
import threading
import time
from datetime import datetime
import os


class MCPLogger:
    def __init__(self, db_path='vision_logs.db'):
        self.db_path = os.path.abspath(db_path)
        self.conn = None
        self.lock = threading.Lock()
        print(f"[Logger Init] Using database at: {self.db_path}")
        self.initialize_database()

    def initialize_database(self):
        """Initialize database connection and tables"""
        with self.lock:
            try:
                self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS vision_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL,
                        agent_type TEXT,
                        data_type TEXT,
                        content TEXT,
                        confidence REAL,
                        additional_info TEXT
                    )
                ''')
                self.conn.commit()
                print("[Logger Init] Database initialized successfully.")
            except Exception as e:
                print(f"[Logger Init] Database initialization error: {str(e)}")
                raise

    def insert_message(self, msg):
        """Insert a generic message into the database"""
        print(f"[Logger] insert_message() called with: {msg}")
        if not msg or "data" not in msg:
            print("[Logger Warning] Skipping empty or invalid message.")
            return

        if self.lock.acquire(timeout=2):
            try:
                agent_type = msg.get("agent", "unknown")
                data = msg.get("data", {})

                if agent_type == "barcode":
                    content = data.get("code", "")
                    data_type = "barcode"
                    additional_info = f"{data.get('product', '')}|{data.get('brand', '')}"
                elif agent_type == "document":
                    content = data.get("text", "")[:500]
                    data_type = "document"
                    additional_info = str(len(content))
                elif agent_type == "object":
                    content = ",".join(data.get("objects", []))[:200]
                    data_type = "object"
                    additional_info = str(len(data.get("objects", [])))
                elif agent_type == "emotion":
                    content = data.get("top_emotion", "")
                    data_type = "emotion"
                    additional_info = str(data.get("confidence", 0))
                else:
                    content = str(data)[:200]
                    data_type = "other"
                    additional_info = ""

                self.conn.execute('''
                    INSERT INTO vision_logs
                    (timestamp, agent_type, data_type, content, confidence, additional_info)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    msg.get("timestamp", time.time()),
                    agent_type,
                    data_type,
                    content,
                    data.get("confidence", 0),
                    additional_info
                ))
                self.conn.commit()
                print("[Logger] Message inserted into DB.")
            except Exception as e:
                print(f"[Logger Error] Database insert error: {str(e)}")
                try:
                    self.conn.close()
                except Exception as close_error:
                    print(f"[Logger Error] DB close failed: {str(close_error)}")
                self.initialize_database()
                print("[Logger] DB connection reinitialized.")
            finally:
                self.lock.release()
        else:
            print("[Logger Error] Lock acquisition failed (possible deadlock).")

    def log_error(self, error_msg):
        """Log system errors to database"""
        if self.lock.acquire(timeout=2):
            try:
                self.conn.execute('''
                    INSERT INTO vision_logs
                    (timestamp, agent_type, data_type, content)
                    VALUES (?, ?, ?, ?)
                ''', (
                    time.time(),
                    "system",
                    "error",
                    str(error_msg)[:500]
                ))
                self.conn.commit()
                print(f"[Logger] Error logged: {error_msg}")
            except Exception as e:
                print(f"[Logger Error] Error logging failed: {str(e)}")
            finally:
                self.lock.release()
        else:
            print("[Logger Error] Lock acquisition failed while logging error.")

    def close_connection(self):
        """Safely close database connection"""
        with self.lock:
            try:
                if self.conn:
                    self.conn.close()
                    print("[Logger] Database connection closed.")
            except Exception as e:
                print(f"[Logger Error] Error closing database: {str(e)}")

    close = close_connection  # Alias for backward compatibility
