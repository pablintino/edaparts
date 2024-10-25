from contextlib import asynccontextmanager
from fastapi import FastAPI

from edaparts.app.config import config
from edaparts.services.database import sessionmanager, get_db


def init_app(init_db=True):
    lifespan = None

    if init_db:
        sessionmanager.init(config.DB_CONFIG)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await sessionmanager.init_models()
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()

    api = FastAPI(title="FastAPI server", lifespan=lifespan)

    import edaparts.routers.routers

    api.include_router(edaparts.routers.routers.router)
    return api
