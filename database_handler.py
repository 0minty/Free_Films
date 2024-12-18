from library import *


async def base():
    async with aiosqlite.connect('base.db') as conn:
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            state TEXT
        )
        ''')
        await conn.commit()


async def start_base(user_id):
    async with aiosqlite.connect('base.db') as conn:
        await conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        await conn.commit()


async def check_user_id(user_id):
    async with aiosqlite.connect('base.db') as conn:
        cursor = await conn.cursor()
        await cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        result = await cursor.fetchone()
        return result
