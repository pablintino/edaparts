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
import pathlib


class Config:
    DB_CONNECTION_STRING = os.getenv(
        "DB_CONNECTION_STRING",
        "postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}".format(
            DB_USER=os.getenv("DB_USER", "postgres"),
            DB_PASSWORD=os.getenv("DB_PASSWORD", "postgres"),
            DB_HOST=os.getenv("DB_HOST", "postgres"),
            DB_NAME=os.getenv("DB_NAME", "edaparts"),
        ),
    )
    DB_ECHO = os.getenv("DB_ECHO", "False").lower() in ("true", "1", "t")

    MODELS_BASE_DIR = os.getenv("MODELS_BASE_DIR", "/var/lib/edaparts/library")
    LOCKS_DIR = os.getenv(
        "LOCKS_DIR", str(pathlib.Path(MODELS_BASE_DIR).parent.joinpath("locks"))
    )


config = Config
