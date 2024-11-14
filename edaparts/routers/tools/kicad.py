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


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from edaparts.dtos.kicad_dtos import (
    CategoryQueryDto,
    CategoriesQueryDto,
    EndpointsQueryDto,
    CategoryPartsQueryDto,
    CategoryPartQueryDto,
    PartQueryDto,
)
from edaparts.services.database import get_db
import edaparts.services.kicad

router = APIRouter(prefix="/tools/kicad", tags=["kicad"])


@router.get("/api/v1/categories.json")
async def list_categories() -> CategoriesQueryDto:
    return [
        CategoryQueryDto(id=str(idx), name=cat)
        for idx, cat in enumerate(edaparts.services.kicad.get_components_categories())
    ]


@router.get("/api/v1/")
async def endpoint_check(request: Request) -> EndpointsQueryDto:
    base = str(request.url).rstrip("/")
    return EndpointsQueryDto.build(
        categories=f"{base}/categories.json", parts=f"{base}/parts"
    )


@router.get("/api/v1/parts/category/{category_id}.json")
async def list_category_parts(
    category_id: int, db: AsyncSession = Depends(get_db)
) -> CategoryPartsQueryDto:
    results = await edaparts.services.kicad.get_components_for_category(db, category_id)
    return [CategoryPartQueryDto.from_model(result) for result in results]


@router.get("/api/v1/parts/{part_id}.json")
async def get_part(part_id: int, db: AsyncSession = Depends(get_db)) -> PartQueryDto:
    result = await edaparts.services.kicad.get_component(db, part_id)
    return PartQueryDto.from_model(result)
