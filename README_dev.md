# DEV README


redis://username:password@localhost:6380/0

## DOCKER

```bash
sudo docker compose down -v  # Stops and removes containers, networks, and all named and anonymous volumes defined in your compose.yaml file
sudo docker compose up -d --force-recreate --remove-orphans
sudo docker exec -it redis_container redis-cli
sudo docker compose up --build --watch  store
sudo docker compose up --watch  store
sudo docker compose logs -f db # connect to cervise logs


```

## ALEMBIC

```sh
alembic init -t async migration
```

```py
# Измененный код migration/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from database import Base, DATABASE_URL
from models import User, Comment, Post, Profile

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
# остальной код оставляем без изменений 
```

```sh
alembic revision --autogenerate -m "Initial revision"
```

```py

# Совет: Всегда указывайте create_type=False для колонок с ENUM, чтобы избежать конфликтов при повторных миграциях.

sa.Column('gender', sa.Enum('MALE', 'FEMALE', name='genderenum', create_type=False), nullable=False)

# Чтобы Alembic корректно удалял типы ENUM при откате миграций, нужно расширить метод downgrade следующим образом:

def downgrade() -> None:
    # Удаление таблиц
    op.drop_table('comments')
    op.drop_table('posts')
    op.drop_table('users')
    op.drop_table('profiles')

    # Удаление типов ENUM
    op.execute('DROP TYPE IF EXISTS ratingenum')
    op.execute('DROP TYPE IF EXISTS genderenum')
    op.execute('DROP TYPE IF EXISTS professionenum')
    op.execute('DROP TYPE IF EXISTS statuspost')

```

```sh
alembic upgrade head

# Выполнение миграции до конкретного ID
alembic upgrade d97a9824423b

# Откат на одну версию назад
alembic downgrade -1
# Откат до конкретной миграции
alembic downgrade d97a9824423b
```