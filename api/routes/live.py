import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from daq_core.runtime import live_bus


router = APIRouter(
    prefix="/ws",
    tags=["live"],
)


@router.websocket("/samples")
async def stream_samples(websocket: WebSocket):
    await websocket.accept()

    subscriber = live_bus.subscribe()

    try:
        while True:
            try:
                sample = await asyncio.to_thread(
                    subscriber.consume,
                    1.0,
                )

                await websocket.send_json(sample.to_dict())

            except TimeoutError:
                await websocket.send_json({
                    "type": "heartbeat"
                })

    except WebSocketDisconnect:
        pass



@router.websocket("/samples/{sensor_id}")
async def stream_sensor_samples(websocket: WebSocket, sensor_id: str):
    await websocket.accept()

    subscriber = live_bus.subscribe()

    try:
        while True:
            try:
                sample = await asyncio.to_thread(
                    subscriber.consume,
                    1.0,
                )

                if sample.sensor_id != sensor_id:
                    continue

                await websocket.send_json(sample.to_dict())

            except TimeoutError:
                await websocket.send_json({
                    "type": "heartbeat"
                })

    except WebSocketDisconnect:
        pass




def update_stats(stats: dict, value: float) -> dict:
    stats["count"] += 1
    stats["min"] = value if stats["min"] is None else min(stats["min"], value)
    stats["max"] = value if stats["max"] is None else max(stats["max"], value)
    stats["sum"] += value
    stats["avg"] = stats["sum"] / stats["count"]

    return stats

@router.websocket("/statistics/{sensor_id}")
async def stream_sensor_statistics(websocket: WebSocket, sensor_id: str):
    await websocket.accept()

    subscriber = live_bus.subscribe()

    stats = {
        "sensor_id": sensor_id,
        "count": 0,
        "min": None,
        "max": None,
        "sum": 0.0,
        "avg": None,
    }

    try:
        while True:
            try:
                sample = await asyncio.to_thread(
                    subscriber.consume,
                    1.0,
                )

                if sample.sensor_id != sensor_id:
                    continue

                stats = update_stats(stats, sample.value)

                await websocket.send_json({
                    "sensor_id": stats["sensor_id"],
                    "count": stats["count"],
                    "min": stats["min"],
                    "max": stats["max"],
                    "avg": stats["avg"],
                })

            except TimeoutError:
                await websocket.send_json({
                    "type": "heartbeat"
                })

    except WebSocketDisconnect:
        pass