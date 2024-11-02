import typing

from fastapi import APIRouter, UploadFile, Form, BackgroundTasks, HTTPException
from fastapi.params import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

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

router = APIRouter(prefix="/symbols", tags=["symbols"])


@router.post("/uploads/create")
async def create_upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    reference: typing.Optional[str] = Form(None),
    description: typing.Optional[str] = Form(None),
    path: str = Form(),
    cad_type: LibraryTypeEnum = Form(),
    db: AsyncSession = Depends(get_db),
) -> SymbolQueryDto:
    try:
        with TempCopiedFile(file.file) as disk_file:
            library_model = await edaparts.services.storable_objects_service.create_storable_library_object(
                db,
                background_tasks,
                StorableObjectRequest(
                    filename=disk_file.path,
                    path=path,
                    file_type=StorableLibraryResourceType.SYMBOL,
                    cad_type=LibraryTypeEnum.to_model(cad_type),
                    reference=reference,
                    description=description,
                ),
            )
            return SymbolQueryDto.from_model(library_model)
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
) -> SymbolQueryDto:
    try:
        with TempCopiedFile(file.file) as disk_file:
            library_model = (
                await edaparts.services.storable_objects_service.update_object_data(
                    db,
                    background_tasks,
                    StorableObjectDataUpdateRequest(
                        model_id=model_id,
                        filename=disk_file.path,
                        file_type=StorableLibraryResourceType.SYMBOL,
                        reference=reference,
                    ),
                )
            )
            return SymbolQueryDto.from_model(library_model)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.get("/{model_id}")
async def get_symbol(
    model_id: int,
    db: AsyncSession = Depends(get_db),
) -> SymbolQueryDto:
    try:
        symbol = await edaparts.services.storable_objects_service.get_storable_model(
            db, StorableLibraryResourceType.SYMBOL, model_id
        )
        return SymbolQueryDto.from_model(symbol)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.get("")
async def list_symbols(
    db: AsyncSession = Depends(get_db),
    page_n: typing.Annotated[int | None, Query(gt=0)] = 1,
    page_size: typing.Annotated[int | None, Query(gt=0)] = 20,
) -> SymbolListResultDto:
    try:
        results, total_count = (
            await edaparts.services.storable_objects_service.get_storable_objects(
                db, StorableLibraryResourceType.SYMBOL, page_n, page_size
            )
        )
        return SymbolListResultDto(
            page_size=page_size,
            page_number=page_n,
            total_elements=total_count,
            elements=[SymbolQueryDto.from_model(m) for m in results],
        )
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )
