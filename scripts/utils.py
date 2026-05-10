# from decimal import Decimal
import json
from pathlib import Path
from typing import Any, Iterable

from pydantic import BaseModel, TypeAdapter


# class DecimalEncoder(json.JSONEncoder):
#     def default(self, obj):  # type: ignore
#         if isinstance(obj, Decimal):
#             return str(obj)
#         return super().default(obj)


def save_list_to_json_file(out_file: Path, obj_list: Iterable[BaseModel], mode_type: type) -> None:
    adapter: TypeAdapter[Iterable[Any]] = TypeAdapter(Iterable[mode_type]) # type: ignore
    obj_json = adapter.dump_json(obj_list, indent=4)
    with out_file.open("wb") as f:
        f.write(obj_json)


def save_obj_to_json_file(out_file: Path, obj: BaseModel) -> None:
    obj_json = obj.model_dump_json(indent=4)
    with out_file.open("w") as f:
        f.write(obj_json)


def load_from_json_file(file: Path) -> list[dict[str, Any]] | dict[str, Any]:
    with file.open("r") as f:
        return json.load(f)
