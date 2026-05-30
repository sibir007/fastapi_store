from contextlib import asynccontextmanager
import time
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware


from project.scheduler_calable import tick
from project.scheduler import async_scheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from datetime import timedelta, datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    task_id = "start_up_test"
    async with async_scheduler as scheduler:
        await scheduler.add_schedule(
            tick,
            DateTrigger(run_time=datetime.now() + timedelta(seconds=10)),
            id=task_id,
            kwargs={"task_id": task_id, "optional_mes": "start up test"},
        )
    
    yield



app = FastAPI(lifespan=lifespan)
from uuid import uuid1

from pydantic import BaseModel


class TaskId(BaseModel):
    id: str


def get_uuid_str():
    return str(uuid1())


@app.post("/api/schedule_once/")
async def schedule_once(seconds_delay: int) -> TaskId:
    task_id = get_uuid_str()
    async with async_scheduler as scheduler:
        await scheduler.add_schedule(
            tick,
            DateTrigger(run_time=datetime.now() + timedelta(seconds=seconds_delay)),
            id=task_id,
            kwargs={"task_id": task_id, "optional_mes": "start up test"},
        )

    return TaskId(id=task_id)


@app.post("/api/schedule_interval/")
async def schedule_interval(seconds_interval: int) -> TaskId:
    task_id = get_uuid_str()
    async with async_scheduler as scheduler:
        await scheduler.add_schedule(
            tick,
            IntervalTrigger(seconds=seconds_interval),
            id=task_id,
            kwargs={"task_id": task_id, "optional_mes": "start up test"},
        )

    return TaskId(id=task_id)


@app.post("/api/remove_schedule/")
async def remove_schedule(task_id: str) -> TaskId:
    async with async_scheduler as scheduler:
        await scheduler.remove_schedule(task_id)

    return TaskId(id=task_id)


@app.post("/api/pause_schedule/")
async def pause_schedule(task_id: str) -> TaskId:
    async with async_scheduler as scheduler:
        await scheduler.pause_schedule(task_id)

    return TaskId(id=task_id)


@app.post("/api/unpause_schedule/")
async def unpause_schedule(task_id: str) -> TaskId:
    async with async_scheduler as scheduler:
        await scheduler.unpause_schedule(task_id)

    return TaskId(id=task_id)


# @broker_router.post("/api/cart/items/" , description="if quantity=0 - delete cart item, if quantity>0 will create (or update if exist) cart item")
# async def add_update_or_delete_cat_item(
#     item: SCartItem,
#     username: Annotated[str, Security(get_token_username, scopes=["items"])],
#     broker: Annotated[RedisBroker, Depends(broker)],
# ) -> SCartItem:

#     return await get_broker_resoult_or_raise_http_exaption(
#         broker,
#         SCartItemIn(**item.model_dump(), username=username),
#         "add-cart-item",
#         SCatrItemBrokerResoult,
#     )


# # @app.delete("/api/cart/items/{id}/")
# async def delete_cart_item(
#     id: int,
#     username: Annotated[str, Security(get_token_username, scopes="items")],
#     broker: Annotated[RedisBroker, Depends(broker)],
# ) -> SCartItem:

#     return await get_broker_resoult_or_raise_http_exaption(
#         broker,
#         SCartItemIn(nom_id=id, quantity=0, username=username),
#         "delete-cart-item",
#         SCatrItemBrokerResoult,
#     )


@app.middleware("http")
async def add_process_time_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start_time = time.perf_counter()
    response: Response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.include_router(broker_router)
