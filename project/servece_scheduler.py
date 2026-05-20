from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
from apscheduler import SchedulerRole


from project.scheduler import async_scheduler # type: ignore


# async_scheduler.role = SchedulerRole.worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_scheduler as scheduler:
        await scheduler.run_until_stopped()
    
    yield



# async def main():
#     async with async_scheduler as sched:
#         await sched.run_until_stopped()


# asyncio.run(main())

async def root() -> Response:
    return PlainTextResponse("Hello, world!")


app = FastAPI(lifespan=lifespan)
app.add_api_route("/", root)
