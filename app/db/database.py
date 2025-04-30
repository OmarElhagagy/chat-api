import asyncpg
from asyncpg.pool import Pool
from typing import Optional
from ..core.config import settings

class Database:
    pool: Optional[Pool] = None

    async def connect(self):
        """create a connection pool to the postgres db"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=5,
                max_size=20
            )
            # Initialize tables if not exist
            await self._init_tables()

    async def disconnect(self):
        """Close all the connections in the pool"""
        if self.pool:
            await self.pool.close()

    async def _init_tables(self):
        """Create tables and sequence if they do not exist"""
        print(f"Pool status: {self.pool}")
        async with self.pool.acquire() as connection:
            await connection.execute("""
            CREATE SEQUENCE IF NOT EXISTS users_id_seq;
            CREATE SEQUENCE IF NOT EXISTS rooms_id_seq;
            CREATE SEQUENCE IF NOT EXISTS messages_id_seq;

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY DEFAULT nextval('users_id_seq'),
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(200) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY DEFAULT nextval('rooms_id_seq'),
                name VARCHAR(100) NOT NULL,
                created_by INTEGER REFERENCES users(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY DEFAULT nextval('messages_id_seq'),
                room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id),
                content TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_messages_room_id ON messages(room_id);
            CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
            CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
            """)

db = Database()
