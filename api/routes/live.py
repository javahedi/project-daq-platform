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