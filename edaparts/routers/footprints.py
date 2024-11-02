import typing

from fastapi import APIRouter, UploadFile, Form, BackgroundTasks, HTTPException
from fastapi.params import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dtos.footprints_dtos import FootprintListResultDto, FootprintQueryDto
from dtos.symbols_dtos import SymbolQueryDto, SymbolListResultDto
from edaparts.dtos.libraries_dtos import LibraryTypeEnum
from edaparts.models.internal.internal_models import (
    StorableLibraryResourceType,
    StorableObjectRequest,
    StorableObjectDataUpdateRequest,
)
from edaparts.services.database import get_db
import edaparts.services.storable_objects_service
from edaparts.utils.files import TempCopiedFile
from edaparts.services.exceptions import ApiError

router = APIRouter(prefix="/footprints", tags=["components", "footprints"])


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
    try:
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
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.post("/{model_id}/uploads/update")
async def update_upload_file(
    background_tasks: BackgroundTasks,
    model_id: int,
    file: UploadFile,
    reference: typing.Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
) -> FootprintQueryDto:
    try:
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
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.get("/{model_id}")
async def get_footprint(
    model_id: int,
    db: AsyncSession = Depends(get_db),
) -> FootprintQueryDto:
    try:
        symbol = await edaparts.services.storable_objects_service.get_storable_model(
            db, StorableLibraryResourceType.FOOTPRINT, model_id
        )
        return FootprintQueryDto.from_model(symbol)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.get("")
async def list_footprints(
    db: AsyncSession = Depends(get_db),
    page_n: typing.Annotated[int | None, Query(gt=0)] = 1,
    page_size: typing.Annotated[int | None, Query(gt=0)] = 20,
) -> FootprintListResultDto:
    try:
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
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )
