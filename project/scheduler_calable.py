from datetime import datetime
from project.broker import broker

def tick(task_id: str, optional_mes: str | None):
    
    mess = f', optional mesage: {optional_mes},' if optional_mes else ""

    print(f"Hello, task id: {task_id}{mess} the time is", datetime.now())



async def test_service_orders(msg: str) -> None:
    async with broker as br:
        await br.publish(msg, list="test-servise-orders")


async def set_order_canceled_service_reqvest(order_id: int) -> None:
    async with broker as br:
        await br.publish(order_id, list="cancel-order")
