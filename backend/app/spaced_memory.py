import os
import sys
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Ensure we can import mysql_storage from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mysql_storage import mysql_storage

def initialize_database(seed: bool = True):
    # Tables are initialized by init_learning_db.py
    # We just ensure the memory_progress table has the necessary columns for SM-2 algorithm
    conn = mysql_storage.get_connection()
    if not conn:
        print("Database connection failed during initialization.")
        return

    try:
        with conn.cursor() as cursor:
            # Check if columns exist
            cursor.execute("SHOW COLUMNS FROM memory_progress LIKE 'ease_factor'")
            if not cursor.fetchone():
                print("Adding SM-2 columns to memory_progress...")
                cursor.execute("ALTER TABLE memory_progress ADD COLUMN ease_factor FLOAT DEFAULT 2.5")
                cursor.execute("ALTER TABLE memory_progress ADD COLUMN interval_days INT DEFAULT 0")
                cursor.execute("ALTER TABLE memory_progress ADD COLUMN repetition INT DEFAULT 0")
                cursor.execute("ALTER TABLE memory_progress ADD COLUMN last_score INT DEFAULT 0")
            
            # Create review_logs table if not exists (User's schema didn't include it, but we need it for history)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_logs (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                word_id INT NOT NULL,
                review_date DATE NOT NULL,
                score INT NOT NULL,
                response_time_ms INT,
                interaction_type VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_date (user_id, review_date)
            )
            """)
            conn.commit()
    except Exception as e:
        print(f"Error updating schema: {e}")

class SpacedRepetitionScheduler:
    def __init__(self):
        pass

    def _get_conn(self):
        return mysql_storage.get_connection()

    def _calculate_next_interval(self, ease_factor: float, repetition: int, score: int):
        if score < 3:
            new_repetition = 0
            new_interval = 0
            new_ease_factor = max(1.3, ease_factor - 0.2)
        else:
            new_repetition = repetition + 1
            if new_repetition == 1:
                new_interval = 1
            elif new_repetition == 2:
                new_interval = 6
            else:
                new_interval = math.ceil(ease_factor * repetition)
            q = 5 - score
            ef_change = 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)
            new_ease_factor = max(1.3, ease_factor + ef_change)
        return new_interval, new_ease_factor, new_repetition

    def record_review(self, user_id: int, word_id: int, score: int,
                     interaction_type: str = 'choice', response_time_ms: Optional[int] = None):
        conn = self._get_conn()
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                today = datetime.now().date()
                cursor.execute("""SELECT ease_factor, interval_days, repetition 
                               FROM memory_progress WHERE user_id=%s AND word_id=%s""", (user_id, word_id))
                record = cursor.fetchone()
                
                if record:
                    # Existing record
                    # Handle None values if columns were just added
                    ef = record['ease_factor'] if record['ease_factor'] is not None else 2.5
                    repetition = record['repetition'] if record['repetition'] is not None else 0
                    
                    new_interval, new_ef, new_rep = self._calculate_next_interval(float(ef), int(repetition), score)
                    next_review = today + timedelta(days=new_interval)
                    
                    cursor.execute("""UPDATE memory_progress SET
                                    ease_factor=%s, interval_days=%s, repetition=%s, next_review=%s,
                                    last_reviewed=%s, last_score=%s, review_count=review_count+1,
                                    memory_strength = memory_strength * 0.9 + (%s/5.0)*0.1
                                    WHERE user_id=%s AND word_id=%s""",
                                (new_ef, new_interval, new_rep, next_review, datetime.now(), score,
                                 score, user_id, word_id))
                else:
                    # New record
                    new_interval, new_ef, new_rep = self._calculate_next_interval(2.5, 0, score)
                    next_review = today + timedelta(days=new_interval)
                    
                    cursor.execute("""INSERT INTO memory_progress
                                   (user_id, word_id, ease_factor, interval_days, repetition, next_review,
                                    last_reviewed, last_score, review_count, memory_strength)
                                   VALUES (%s, %s, 2.5, 0, 0, %s, %s, %s, 1, %s)""",
                                (user_id, word_id, next_review, datetime.now(), score, score/5.0))

                # Log review
                cursor.execute("""INSERT INTO review_logs (user_id, word_id, review_date, score, response_time_ms, interaction_type)
                               VALUES (%s, %s, %s, %s, %s, %s)""",
                            (user_id, word_id, today, score, response_time_ms, interaction_type))
                
                conn.commit()
        except Exception as e:
            print(f"Error recording review: {e}")
            if conn:
                conn.rollback()

    def get_today_review_queue(self, user_id: int, limit: int = 20) -> List[Dict]:
        conn = self._get_conn()
        if not conn:
            return []

        try:
            with conn.cursor() as cursor:
                today = datetime.now()
                
                # 1. Fetch due reviews
                # Use DATE(next_review) <= CURDATE() logic
                cursor.execute("""SELECT w.*, mp.*, mp.word_id as word_id 
                               FROM memory_progress mp
                               JOIN words w ON mp.word_id = w.id
                               WHERE mp.user_id=%s AND (mp.next_review <= %s OR mp.next_review IS NULL)
                               ORDER BY mp.next_review ASC
                               LIMIT %s""", (user_id, today, limit))
                due_words = cursor.fetchall()
                
                results = [dict(row) for row in due_words]
                
                # 2. If not enough, fetch new words from Day 1 (day_id=1)
                if len(results) < limit:
                    remaining = limit - len(results)
                    # Get words from day 1 that are not in memory_progress for this user
                    cursor.execute("""
                        SELECT w.* 
                        FROM day_words dw
                        JOIN words w ON dw.word_id = w.id
                        LEFT JOIN memory_progress mp ON w.id = mp.word_id AND mp.user_id = %s
                        WHERE dw.day_id = 1 AND mp.id IS NULL
                        ORDER BY dw.word_order ASC
                        LIMIT %s
                    """, (user_id, remaining))
                    new_words = cursor.fetchall()
                    
                    for w in new_words:
                        w['is_new'] = True
                        results.append(dict(w))
                
                # Rename 'id' to 'word_id' for consistency if needed, or handle in API
                # In 'words' table, PK is 'id'. In 'memory_progress', 'word_id' is FK.
                # The join result has 'id' from words.
                for r in results:
                    if 'id' in r and 'word_id' not in r:
                        r['word_id'] = r['id']
                    elif 'word_id' in r:
                        # Ensure word_id is set correctly
                        pass
                
                return results
        except Exception as e:
            print(f"Error fetching review queue: {e}")
            return []

    def add_new_words_to_user(self, user_id: int, word_ids: List[int]):
        # In this new logic, get_today_review_queue automatically fetches new words from day_words.
        # But if explicit addition is needed (e.g. from API), we can insert them into memory_progress
        conn = self._get_conn()
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                today = datetime.now()
                for wid in word_ids:
                    # Insert with initial state
                    cursor.execute("""INSERT IGNORE INTO memory_progress
                                   (user_id, word_id, ease_factor, interval_days, repetition, next_review, memory_strength)
                                   VALUES (%s, %s, 2.5, 0, 0, %s, 0.0)""", (user_id, wid, today))
                conn.commit()
        except Exception as e:
            print(f"Error adding new words: {e}")
            if conn:
                conn.rollback()

    def get_user_progress(self, user_id: int) -> Dict:
        conn = self._get_conn()
        if not conn:
            return {}

        try:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT COUNT(*) as total_words,
                                      SUM(CASE WHEN memory_strength > 0.8 THEN 1 ELSE 0 END) as mastered_words,
                                      SUM(CASE WHEN next_review <= NOW() THEN 1 ELSE 0 END) as due_words,
                                      AVG(memory_strength) as avg_memory_strength
                               FROM memory_progress WHERE user_id=%s""", (user_id,))
                stats = cursor.fetchone() or {}
                
                cursor.execute("""SELECT DATE(review_date) as day, COUNT(*) as review_count, AVG(score) as avg_score
                               FROM review_logs WHERE user_id=%s AND review_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                               GROUP BY DATE(review_date) ORDER BY day DESC""", (user_id,))
                stats['recent_activity'] = cursor.fetchall()
                
                return stats
        except Exception as e:
            print(f"Error getting progress: {e}")
            return {}

    def get_new_word_ids(self, user_id: int, count: int) -> List[int]:
        # Fetch from Day 1 words
        conn = self._get_conn()
        if not conn:
            return []
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT w.id 
                    FROM day_words dw
                    JOIN words w ON dw.word_id = w.id
                    LEFT JOIN memory_progress mp ON w.id = mp.word_id AND mp.user_id = %s
                    WHERE dw.day_id = 1 AND mp.id IS NULL
                    ORDER BY dw.word_order ASC
                    LIMIT %s
                """, (user_id, count))
                rows = [r['id'] for r in cursor.fetchall()]
                return rows
        except Exception as e:
            print(f"Error getting new word ids: {e}")
            return []
