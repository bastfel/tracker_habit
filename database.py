import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# ==========================================
# НАСТРОЙКИ ПОДКЛЮЧЕНИЯ
# ==========================================
# Если у вас другой пароль, измените его здесь (или через export DB_PASSWORD)
DB_CONFIG = {
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}
DB_NAME = os.getenv("DB_NAME", "tracker_db") # Название базы данных

# ==========================================
# ФУНКЦИИ
# ==========================================

def setup_database():
    """
    Проверяет, существует ли база данных. Если нет — создает её.
    Также создает таблицу tasks.
    """
    # 1. Подключаемся к системной БД 'postgres', чтобы создать нашу БД
    try:
        conn = psycopg2.connect(dbname="postgres", **DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Проверяем, есть ли БД
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"[INFO] База данных '{DB_NAME}' успешно создана.")
        else:
            print(f"[INFO] База данных '{DB_NAME}' уже существует.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Ошибка при создании БД: {e}")
        return

    # 2. Подключаемся уже к нашей БД и создаем таблицу
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'new',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("[INFO] Таблица 'tasks' готова к работе.")
    except Exception as e:
        print(f"[ERROR] Ошибка при создании таблицы: {e}")


def get_connection():
    """Возвращает подключение к нашей БД (tracker_db)."""
    return psycopg2.connect(dbname=DB_NAME, **DB_CONFIG)


def get_all_tasks():
    """Возвращает список кортежей (id, title, status, created_at)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, status, created_at FROM tasks ORDER BY id;")
            return cur.fetchall()


def add_task(title):
    """Добавляет задачу, возвращает её id."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id;", (title,))
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id


def delete_task(task_id):
    """Удаляет задачу по id. Возвращает True, если удалено."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
            deleted = cur.rowcount
        conn.commit()
        return deleted > 0


def update_task_status(task_id, status):
    """Обновляет статус задачи. Возвращает True, если обновлено."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tasks SET status = %s WHERE id = %s;", (status, task_id))
            updated = cur.rowcount
        conn.commit()
        return updated > 0
