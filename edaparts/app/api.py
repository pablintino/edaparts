#
# MIT License
#
# Copyright (c) 2024 Pablo Rodriguez Nava, @pablintino
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
import os
import shutil
import typing
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.applications import Request
from starlette.responses import JSONResponse

from edaparts.app.config import config
from edaparts.services.database import sessionmanager
from edaparts.services.exceptions import ApiError


def exception_handler_api_error(_: Request, exc: Exception) -> JSONResponse:
    api_err = typing.cast(ApiError, exc)
    data, err_code = api_err.format_api_data()
    return JSONResponse(data, status_code=err_code)


def init_app():
    sessionmanager.init(config.DB_CONNECTION_STRING, echo=config.DB_ECHO)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        # Remove the existing locks
        if os.path.exists(config.LOCKS_DIR):
            shutil.rmtree(config.LOCKS_DIR)

        yield
        if sessionmanager._engine is not None:
            await sessionmanager.close()

    api = FastAPI(title="FastAPI server", lifespan=lifespan)

    import edaparts.routers.routers

    api.include_router(edaparts.routers.routers.router)
    api.add_exception_handler(ApiError, exception_handler_api_error)
    return api
