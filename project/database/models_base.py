from decimal import Decimal
from typing import Any
import uuid

from sqlalchemy import DateTime, func, inspect
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


from typing_extensions import Annotated


intpk = Annotated[int, mapped_column(primary_key=True)]
timestamp = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False),
]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class MBase(AsyncAttrs, DeclarativeBase):
    id: Mapped[intpk]
    # created_at: Mapped[timestamp]

    def to_dict(self, exclude_none: bool = False) -> dict[Any, Any]:
        """
        Преобразует объект модели в словарь.

        Args:
            exclude_none (bool): Исключать ли None значения из результата

        Returns:
            dict: Словарь с данными объекта
        """

        result = {}

        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)

            # Преобразование специальных типов данных
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)

            # Добавляем значение в результат
            if not exclude_none or value is not None:
                result[column.key] = value

        return result  # type: ignore