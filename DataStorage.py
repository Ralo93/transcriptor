import sqlite3
from datetime import datetime

class DataStorage:
    def __init__(self, db_name="transcriptions.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                transcription TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_frequencies (
                transcription_id INTEGER,
                word TEXT,
                frequency INTEGER,
                FOREIGN KEY(transcription_id) REFERENCES transcriptions(id)
            )
        ''')
        self.connection.commit()

    def save_transcription(self, transcription, word_frequencies):
        timestamp = datetime.now().isoformat()
        self.cursor.execute('''
            INSERT INTO transcriptions (timestamp, transcription)
            VALUES (?, ?)
        ''', (timestamp, transcription))
        transcription_id = self.cursor.lastrowid

        for word, frequency in word_frequencies.items():
            self.cursor.execute('''
                INSERT INTO word_frequencies (transcription_id, word, frequency)
                VALUES (?, ?, ?)
            ''', (transcription_id, word, frequency))

        self.connection.commit()

    def get_word_frequencies(self):
        self.cursor.execute('''
            SELECT word, SUM(frequency) as total_frequency
            FROM word_frequencies
            GROUP BY word
            ORDER BY total_frequency DESC
        ''')
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()
