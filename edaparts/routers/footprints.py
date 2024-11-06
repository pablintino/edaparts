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


import typing

from fastapi import APIRouter, UploadFile, Form, BackgroundTasks
from fastapi.params import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse, Response

import edaparts.services.storable_objects_service
from dtos.footprints_dtos import FootprintListResultDto, FootprintQueryDto
from edaparts.dtos.libraries_dtos import (
    LibraryTypeEnum,
    CommonObjectFromExistingCreateDto,
    CommonObjectUpdateDto,
)
from edaparts.models.internal.internal_models import (
    StorableLibraryResourceType,
    StorableObjectRequest,
    StorableObjectDataUpdateRequest,
)
from edaparts.services.database import get_db
from edaparts.utils.files import TempCopiedFile

router = APIRouter(prefix="/footprints", tags=["footprints"])


@router.post("/uploads/create")
async def create_upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    reference: typing.Optional[str] = Form(None),
    description: typing.Optional[str] = Form(None),
    path: str = Form(),
    cad_type: LibraryTypeEnum = Form(),
    db: AsyncSession = Depends(get_db),
) -> FootprintQueryDto:
    with TempCopiedFile(file.file) as disk_file:
        library_model = await edaparts.services.storable_objects_service.create_storable_library_object(
            db,
            background_tasks,
            StorableObjectRequest(
                filename=disk_file.path,
                path=path,
                file_type=StorableLibraryResourceType.FOOTPRINT,
                cad_type=LibraryTypeEnum.to_model(cad_type),
                reference=reference,
                description=description,
            ),
        )
        return FootprintQueryDto.from_model(library_model)


@router.post("")
async def create_from_existing_path(
    background_tasks: BackgroundTasks,
    body: CommonObjectFromExistingCreateDto,
    db: AsyncSession = Depends(get_db),
) -> FootprintQueryDto:
    library_model = await edaparts.services.storable_objects_service.create_storable_library_object_from_existing_file(
        db,
        background_tasks,
        body.to_model(StorableLibraryResourceType.FOOTPRINT),
    )
    return FootprintQueryDto.from_model(library_model)


@router.post("/{model_id}/uploads/update")
async def update_upload_file(
    background_tasks: BackgroundTasks,
    model_id: int,
    file: UploadFile,
    reference: typing.Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
) -> FootprintQueryDto:
    with TempCopiedFile(file.file) as disk_file:
        library_model = (
            await edaparts.services.storable_objects_service.update_object_data(
                db,
                background_tasks,
                StorableObjectDataUpdateRequest(
                    model_id=model_id,
                    filename=disk_file.path,
                    file_type=StorableLibraryResourceType.FOOTPRINT,
                    reference=reference,
                ),
            )
        )
        return FootprintQueryDto.from_model(library_model)


@router.get("/{model_id}/data")
async def get_footprint_data(
    model_id: int,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    path = (
        await edaparts.services.storable_objects_service.get_storable_model_data_path(
            db, StorableLibraryResourceType.FOOTPRINT, model_id
        )
    )
    return FileResponse(path=path)


@router.get("/{model_id}")
async def get_footprint(
    model_id: int,
    db: AsyncSession = Depends(get_db),
) -> FootprintQueryDto:
    symbol = await edaparts.services.storable_objects_service.get_storable_model(
        db, StorableLibraryResourceType.FOOTPRINT, model_id
    )
    return FootprintQueryDto.from_model(symbol)


@router.put("/{model_id}")
async def update_footprint(
    background_tasks: BackgroundTasks,
    model_id: int,
    body: CommonObjectUpdateDto,
    db: AsyncSession = Depends(get_db),
) -> FootprintQueryDto:
    result = await edaparts.services.storable_objects_service.update_object_metadata(
        db,
        background_tasks,
        model_id,
        body.to_model(StorableLibraryResourceType.FOOTPRINT),
    )
    return FootprintQueryDto.from_model(result)


@router.put("/{model_id}")
async def update_footprint(
    background_tasks: BackgroundTasks,
    model_id: int,
    body: CommonObjectUpdateDto,
    db: AsyncSession = Depends(get_db),
) -> FootprintQueryDto:
    result = await edaparts.services.storable_objects_service.update_object_metadata(
        db,
        background_tasks,
        model_id,
        body.to_model(StorableLibraryResourceType.FOOTPRINT),
    )
    return FootprintQueryDto.from_model(result)


@router.delete("/{model_id}", status_code=204, response_class=Response)
async def delete_footprint(
    background_tasks: BackgroundTasks,
    model_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    await edaparts.services.storable_objects_service.delete_object(
        db, background_tasks, StorableLibraryResourceType.FOOTPRINT, model_id
    )


@router.get("")
async def list_footprints(
    db: AsyncSession = Depends(get_db),
    page_n: typing.Annotated[int | None, Query(gt=0)] = 1,
    page_size: typing.Annotated[int | None, Query(gt=0)] = 20,
) -> FootprintListResultDto:
    results, total_count = (
        await edaparts.services.storable_objects_service.get_storable_objects(
            db, StorableLibraryResourceType.FOOTPRINT, page_n, page_size
        )
    )
    return FootprintListResultDto(
        page_size=page_size,
        page_number=page_n,
        total_elements=total_count,
        elements=[FootprintQueryDto.from_model(m) for m in results],
    )
