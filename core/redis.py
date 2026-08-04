from fastapi import Request


async def get_redis(request: Request): #works in routes coz: FastAPI automatically injects the current request object when it sees
    return request.app.state.redis