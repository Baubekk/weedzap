from fastapi import FastAPI, WebSocket


def websocket_middleware(app: FastAPI, handler):
    original_router_add_api_websocket_route = app.router.add_api_websocket_route

    def patched_add_api_websocket_route(path, endpoint, **kwargs):
        async def wrapped_endpoint(websocket: WebSocket, *args, **kwargs_):
            await handler(websocket)
            return await endpoint(websocket, *args, **kwargs_)
        return original_router_add_api_websocket_route(path, wrapped_endpoint, **kwargs)

    app.router.add_api_websocket_route = patched_add_api_websocket_route