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


import dataclasses
import logging
import os.path
import pathlib
import re
import shutil
import typing

import filelock
from fastapi import BackgroundTasks
from sqlalchemy import select, update, func, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import edaparts.utils.models_parser
from edaparts.app.config import Config
from edaparts.models import FootprintReference, LibraryReference
from edaparts.models.internal.internal_models import (
    CadType,
    CreateUpdateDataStorableTask,
    BaseStorableTask,
    DeleteStorableTask,
    StorableObjectCreateReuseRequest,
    StorableObjectUpdateRequest,
)
from edaparts.models.internal.internal_models import (
    StorableLibraryResourceType,
    StorageStatus,
    StorableObjectRequest,
    StorableObjectDataUpdateRequest,
)
from edaparts.services import database
from edaparts.services.exceptions import ApiError
from edaparts.services.exceptions import (
    ResourceAlreadyExistsApiError,
    ResourceNotFoundApiError,
    InvalidFootprintApiError,
    InvalidSymbolApiError,
    InvalidStorableTypeError,
)
from edaparts.utils.files import hash_sha256
from edaparts.utils.helpers import BraceMessage as __l
from edaparts.utils.sqlalchemy import query_page

__logger = logging.getLogger(__name__)

__STORABLE_DIR_PATH_FOOTPRINTS = "footprints"
__STORABLE_DIR_PATH_SYMBOLS = "symbols"
__storable_base_dirs: dict[CadType, dict[StorableLibraryResourceType, pathlib.Path]] = {
    CadType.KICAD: {
        StorableLibraryResourceType.FOOTPRINT: pathlib.Path(
            str(CadType.KICAD.value)
        ).joinpath(__STORABLE_DIR_PATH_FOOTPRINTS),
        StorableLibraryResourceType.SYMBOL: pathlib.Path(
            str(CadType.KICAD.value)
        ).joinpath(__STORABLE_DIR_PATH_SYMBOLS),
    },
    CadType.ALTIUM: {
        StorableLibraryResourceType.FOOTPRINT: pathlib.Path(
            str(CadType.ALTIUM.value)
        ).joinpath(__STORABLE_DIR_PATH_FOOTPRINTS),
        StorableLibraryResourceType.SYMBOL: pathlib.Path(
            str(CadType.ALTIUM.value)
        ).joinpath(__STORABLE_DIR_PATH_SYMBOLS),
    },
}


def __validate_input_path(
    path: str, cad_type: CadType, file_type: StorableLibraryResourceType
):
    extensions_matrix = {
        cad_type.KICAD: {
            StorableLibraryResourceType.FOOTPRINT: "kicad_mod",
            StorableLibraryResourceType.SYMBOL: "kicad_sym",
        },
        cad_type.ALTIUM: {
            StorableLibraryResourceType.FOOTPRINT: "pcblib",
            StorableLibraryResourceType.SYMBOL: "schlib",
        },
    }

    if os.path.isabs(path):
        raise ApiError(f"the given path {path} must be relative", http_code=400)

    if path.lower().startswith(
        (__STORABLE_DIR_PATH_FOOTPRINTS, __STORABLE_DIR_PATH_SYMBOLS)
    ):
        prefix = path.split(os.path.sep)
        raise ApiError(
            f"the given path {path} must not start by the reserved prefix: {prefix[0]}",
            http_code=400,
        )

    if (
        cad_type == CadType.KICAD
        and file_type == StorableLibraryResourceType.FOOTPRINT
        and not os.path.dirname(path).endswith(".pretty")
    ):
        raise ApiError(
            f"KiCAD footprint files must be stored in a directory suffixed with `.pretty`",
            http_code=400,
        )
    expected_extension = extensions_matrix[cad_type][file_type]
    if not path.lower().endswith(f".{expected_extension}"):
        raise ApiError(
            f"the given path {path} must end with .{expected_extension}", http_code=400
        )


async def __validate_kicad_footprint_duplication(
    db: AsyncSession, path: str, reference: str, model_id: int = None
):
    parent_dir = os.path.dirname(path)
    query = select(FootprintReference).filter(
        FootprintReference.path.startswith(parent_dir),
        FootprintReference.cad_type == CadType.KICAD,
        FootprintReference.reference == reference,
    )
    if model_id is not None:
        query = query.filter(FootprintReference.id != model_id)
    existing_footprint = (await db.scalars(query)).first()
    if existing_footprint:
        raise ResourceAlreadyExistsApiError(
            f"the given footprint duplicates the already existing one",
            conflicting_id=existing_footprint.id,
        )


def __validate_storable_type(storable_type: StorableLibraryResourceType):
    if storable_type not in (
        StorableLibraryResourceType.FOOTPRINT,
        StorableLibraryResourceType.SYMBOL,
    ):
        raise InvalidStorableTypeError(
            __l(
                "The given storable type was not expected [storable_type={0}]",
                storable_type.value,
            )
        )


def __get_error_for_type(storable_type):
    __validate_storable_type(storable_type)
    return (
        InvalidFootprintApiError
        if storable_type == StorableLibraryResourceType.FOOTPRINT
        else InvalidSymbolApiError
    )


def __get_model_for_storable_type(
    storable_type,
) -> typing.Type[FootprintReference | LibraryReference]:
    __validate_storable_type(storable_type)
    return (
        FootprintReference
        if storable_type == StorableLibraryResourceType.FOOTPRINT
        else LibraryReference
    )


def __get_library(
    file: pathlib.Path, cad_type: CadType, expected_type: StorableLibraryResourceType
):
    try:
        # Parse the given data
        lib = edaparts.utils.models_parser.parse_file(file, cad_type)
        # Be sure that the encoded data is of the expected type
        if expected_type != lib.library_type:
            raise __get_error_for_type(expected_type)(
                "The given library is not of the expected type. {expected_type="
                + str(expected_type.value)
                + ", file_type="
                + str(lib.library_type.value)
                + "}"
            )
        return lib
    except IOError as err:
        raise __get_error_for_type(expected_type)(
            f"The given Altium file is corrupt",
            err.args[0] if len(err.args) > 0 else None,
        )


async def update_object_data(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    storable_request: StorableObjectDataUpdateRequest,
):
    # For the shake of simplicity do not allow to change the path
    # If the path can be changed we should manage that the change is valid for
    # all the references to the same path, and update all of them to point to that path

    model = await db.get(
        __get_model_for_storable_type(storable_request.file_type),
        storable_request.model_id,
    )
    if not model:
        raise ResourceNotFoundApiError(
            "Storable object not found", missing_id=storable_request.model_id
        )

    # Skip if the model reference and file are identical
    target_file = __get_target_object_path(
        model.cad_type, storable_request.file_type, model.path
    )
    if (
        model.storage_status == StorageStatus.STORED
        and (
            storable_request.reference is None
            or model.reference == storable_request.reference
        )
        and target_file.exists()
        and hash_sha256(target_file) == hash_sha256(storable_request.filename)
    ):
        __logger.debug(
            "Given new storable object data has the same content and reference as the current one. Skipping..."
        )
        return model

    lib = __get_library(
        storable_request.filename, model.cad_type, storable_request.file_type
    )

    # If a reference was provided it should be a valid one
    if storable_request.reference and not lib.is_present(storable_request.reference):
        raise __get_error_for_type(storable_request.file_type)(
            "The provided reference was not found in the given library"
        )
    elif (
        storable_request.reference is None
        and model.reference
        and not lib.is_present(model.reference)
    ):
        raise __get_error_for_type(storable_request.file_type)(
            "no reference provided for the file update and the existing one is not present in the given library"
        )
    if storable_request.reference is not None:
        await __validate_storable_not_exists(
            db,
            model.path,
            storable_request.reference,
            storable_request.file_type,
            model.cad_type,
            model_id=model.id,
        )

    # Reset storage status
    model.storage_status = StorageStatus.NOT_STORED
    db.add(model)
    await db.commit()

    # Signal background process to store the storable object
    background_tasks.add_task(
        _object_store_task,
        CreateUpdateDataStorableTask(
            model_id=model.id,
            filename=storable_request.filename,
            path=model.path,
            file_type=storable_request.file_type,
            cad_type=model.cad_type,
            # NOTICE: References are changed inside the task to ensure reference checks are done with the file lock
            reference=storable_request.reference or model.reference,
        ),
    )
    return model


async def update_object_metadata(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    model_id: int,
    storable_request: StorableObjectUpdateRequest,
):
    model = await db.get(
        __get_model_for_storable_type(storable_request.file_type),
        model_id,
    )
    if not model:
        raise ResourceNotFoundApiError("Storable object not found", missing_id=model_id)

    # No changes
    if (not storable_request.reference and not storable_request.description) or (
        storable_request.reference == model.reference
        and storable_request.description == model.description
    ):
        return model

    if storable_request.reference and storable_request.reference != model.reference:
        if model.storage_status != StorageStatus.STORED:
            raise __get_error_for_type(storable_request.file_type)(
                "cannot update the reference cause the path is not yet stored",
            )
        __validate_kicad_reference_change(
            storable_request.file_type, storable_request.cad_type
        )
        await __validate_storable_not_exists(
            db,
            model.path,
            storable_request.reference,
            storable_request.file_type,
            model.cad_type,
            model_id=model.id,
        )
        # Parse storable object from encoded data and check its content
        local_path = __get_target_object_path(
            storable_request.cad_type, storable_request.file_type, model.path
        )
        lib = __get_library(
            local_path,
            storable_request.cad_type,
            storable_request.file_type,
        )
        # If check that the given reference exists
        if not lib.is_present(storable_request.reference):
            raise __get_error_for_type(storable_request.file_type)(
                "The given reference does not exist in the given library "
            )

        # Reset storage status
        model.storage_status = StorageStatus.NOT_STORED

    if (
        storable_request.description is not None
        and storable_request.description != model.description
    ):
        model.description = storable_request.description

    db.add(model)
    await db.commit()

    # Signal background process to store the storable object
    if storable_request.reference != model.reference:
        background_tasks.add_task(
            _object_store_task,
            CreateUpdateDataStorableTask(
                model_id=model.id,
                path=model.path,
                file_type=storable_request.file_type,
                cad_type=model.cad_type,
                # NOTICE: References are changed inside the task to ensure reference checks are done with the file lock
                reference=storable_request.reference,
            ),
        )
    return model


def __validate_kicad_reference_change(
    file_type: StorableLibraryResourceType, cad_type: CadType
):
    if cad_type == CadType.KICAD and file_type == StorableLibraryResourceType.FOOTPRINT:
        raise ApiError(
            "KiCAD footprints do not support multiple references per file",
            http_code=400,
        )


async def create_storable_library_object(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    storable_request: StorableObjectRequest,
) -> FootprintReference | LibraryReference:
    __validate_storable_type(storable_request.file_type)
    __validate_input_path(
        storable_request.path, storable_request.cad_type, storable_request.file_type
    )

    # Parse storable object from encoded data and check its content
    lib = __get_library(
        storable_request.filename,
        storable_request.cad_type,
        storable_request.file_type,
    )

    # Verify that the body contains enough information
    if not storable_request.reference:
        # Try to obtain the reference from the library data
        if lib.count != 1:
            raise __get_error_for_type(storable_request.file_type)(
                "More than one part in the given library. Provide a reference"
            )

        storable_request = dataclasses.replace(
            storable_request, reference=lib.models[next(iter(lib.models.keys()))].name
        )

    # If check that the given reference exists
    if not lib.is_present(storable_request.reference):
        raise __get_error_for_type(storable_request.file_type)(
            "The given reference does not exist in the given library "
        )

    # If no description is provided try to populate it from library data
    if not storable_request.description:
        storable_request = dataclasses.replace(
            storable_request,
            description=lib.models[storable_request.reference].description,
        )

    __logger.debug(
        __l(
            "Creating a new storable object [file_type={0}, reference_name={1}, storable_path={2}, description={3}]",
            storable_request.file_type,
            storable_request.reference,
            storable_request.path,
            storable_request.description,
        )
    )

    await __validate_storable_not_exists(
        db,
        storable_request.path,
        storable_request.reference,
        storable_request.file_type,
        storable_request.cad_type,
    )

    # Create a model based on the storable object type
    model = __get_model_for_storable_type(storable_request.file_type)(
        path=storable_request.path,
        reference=storable_request.reference,
        # Ensure that storage status at creation time is set to NOT_STORED
        storage_status=StorageStatus.NOT_STORED,
        description=storable_request.description,
        cad_type=storable_request.cad_type,
        alias=__get_model_alias(storable_request),
    )

    db.add(model)
    await db.commit()
    __logger.debug(__l("Storable object created [id={0}]", model.id))

    # Signal background process to store the object
    background_tasks.add_task(
        _object_store_task,
        CreateUpdateDataStorableTask(
            model_id=model.id,
            filename=storable_request.filename,
            path=model.path,
            file_type=storable_request.file_type,
            cad_type=model.cad_type,
            reference=model.reference,
        ),
    )

    return model


async def create_storable_library_object_from_existing_file(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    storable_request: StorableObjectCreateReuseRequest,
) -> FootprintReference | LibraryReference:
    __validate_storable_type(storable_request.file_type)
    __validate_input_path(
        storable_request.path, storable_request.cad_type, storable_request.file_type
    )
    __validate_kicad_reference_change(
        storable_request.file_type, storable_request.cad_type
    )

    path_references = list(
        (
            await db.scalars(
                select(
                    __get_model_for_storable_type(storable_request.file_type)
                ).filter_by(
                    cad_type=storable_request.cad_type, path=storable_request.path
                )
            )
        ).fetchall()
    )
    if not path_references:
        raise ApiError(
            f"the given path {storable_request.path} does not exist", http_code=400
        )

    if any((ref.reference == storable_request.reference for ref in path_references)):
        raise ApiError(
            f"the given reference {storable_request.reference} already exists for {storable_request.path}",
            http_code=400,
        )

    if not any((ref.storage_status == StorageStatus.STORED for ref in path_references)):
        raise ApiError(
            f"the given path {storable_request.path} is not yet fully stored",
            http_code=400,
        )

    # Parse storable object from encoded data and check its content
    local_path = __get_target_object_path(
        storable_request.cad_type, storable_request.file_type, storable_request.path
    )
    lib = __get_library(
        local_path,
        storable_request.cad_type,
        storable_request.file_type,
    )
    # Check the given reference exists
    if not lib.is_present(storable_request.reference):
        raise __get_error_for_type(storable_request.file_type)(
            "The given reference does not exist in the given library "
        )

    # If no description is provided try to populate it from library data
    if not storable_request.description:
        storable_request = dataclasses.replace(
            storable_request,
            description=lib.models[storable_request.reference].description,
        )

    __logger.debug(
        __l(
            "Creating a new storable object [file_type={0}, reference_name={1}, storable_path={2}, description={3}]",
            storable_request.file_type,
            storable_request.reference,
            storable_request.path,
            storable_request.description,
        )
    )

    await __validate_storable_not_exists(
        db,
        storable_request.path,
        storable_request.reference,
        storable_request.file_type,
        storable_request.cad_type,
    )

    # Create a model based on the storable object type
    model = __get_model_for_storable_type(storable_request.file_type)(
        path=storable_request.path,
        reference=storable_request.reference,
        # Ensure that storage status at creation time is set to NOT_STORED
        storage_status=StorageStatus.NOT_STORED,
        description=storable_request.description,
        cad_type=storable_request.cad_type,
        alias=path_references[0].alias,
    )

    db.add(model)
    await db.commit()
    __logger.debug(__l("Storable object created [id={0}]", model.id))

    # Signal background process to store the object
    background_tasks.add_task(
        _object_store_task,
        CreateUpdateDataStorableTask(
            model_id=model.id,
            path=model.path,
            file_type=storable_request.file_type,
            cad_type=model.cad_type,
            reference=model.reference,
        ),
    )

    return model


async def delete_object(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    storable_type: StorableLibraryResourceType,
    model_id: int,
):
    model = await db.get(
        __get_model_for_storable_type(storable_type),
        model_id,
    )
    if model:
        background_tasks.add_task(
            _object_store_task,
            DeleteStorableTask(
                model_id=model.id,
                path=model.path,
                file_type=storable_type,
                cad_type=model.cad_type,
            ),
        )


def __get_model_alias(storable_request: StorableObjectRequest) -> typing.Optional[str]:
    if storable_request.cad_type != CadType.KICAD:
        return None

    if storable_request.file_type == StorableLibraryResourceType.FOOTPRINT:
        lib_path_name = (
            os.path.basename(os.path.dirname(storable_request.path))
            .lower()
            .replace(".pretty", "")
        )
    else:
        lib_path_name = storable_request.path.lower().rsplit(".", maxsplit=1)[0]

    sanitized_name = re.sub("[^0-9a-z]+", "_", lib_path_name).strip("_").upper()
    return f"EDAPARTS_{sanitized_name}"


async def _object_store_task(storable_task: BaseStorableTask):
    async with database.sessionmanager.session() as session:
        error = None
        try:
            if isinstance(storable_task, CreateUpdateDataStorableTask):
                await __task_store_file(session, storable_task)
            elif isinstance(storable_task, DeleteStorableTask):
                await __task_delete_model(session, storable_task)
        except SQLAlchemyError as err:
            error = err
            __logger.critical(
                __l(
                    "SQLAlchemyError error [model_id={0}, storable_task={1}]",
                    storable_task.model_id,
                    storable_task,
                ),
                exc_info=True,
            )
        except ApiError as err:
            # Internal error that doesn't mean the task is failing, the payload may be wrong,
            # and we should pass the message to the user
            error = err
            __logger.debug(err.msg)
        finally:
            # Remove the temporal file
            if (
                isinstance(storable_task, CreateUpdateDataStorableTask)
                and storable_task.filename
            ):
                os.remove(storable_task.filename)

        if error:
            # Update the state to signal something failed
            await __store_file_set_state(
                session,
                storable_task.model_id,
                storable_task.file_type,
                StorageStatus.STORAGE_FAILED,
                error_description=str(error),
            )


def __get_target_object_path(
    cad_type: CadType, file_type: StorableLibraryResourceType, path: str
) -> pathlib.Path:
    return pathlib.Path(Config.MODELS_BASE_DIR).joinpath(
        __storable_base_dirs[cad_type][file_type], path
    )


async def __task_delete_model(
    session: AsyncSession,
    storable_task: DeleteStorableTask,
):
    await __store_file_set_state(
        session,
        storable_task.model_id,
        storable_task.file_type,
        StorageStatus.DELETING,
    )
    with __get_file_lock(storable_task):
        target_file = __get_target_object_path(
            storable_task.cad_type, storable_task.file_type, storable_task.path
        )

        # Delete the file only if we are deleting the last reference to it
        other_references = await __get_stored_references_for_id(session, storable_task)
        if not other_references and target_file.exists():
            target_file.unlink()

        model_type = __get_model_for_storable_type(storable_task.file_type)
        await session.execute(
            delete(model_type).where(model_type.id == storable_task.model_id)
        )
        await session.commit()


async def __task_store_file(
    session: AsyncSession,
    storable_task: CreateUpdateDataStorableTask,
):
    target_file = __get_target_object_path(
        storable_task.cad_type, storable_task.file_type, storable_task.path
    )
    if not target_file.parent.exists():
        target_file.parent.mkdir(parents=True)

    await __store_file_set_state(
        session,
        storable_task.model_id,
        storable_task.file_type,
        StorageStatus.STORING,
    )
    with __get_file_lock(storable_task):
        await __store_file_validate(session, storable_task)

        model_type = __get_model_for_storable_type(storable_task.file_type)
        current_reference = (
            await session.scalars(
                select(model_type.reference).filter(
                    model_type.id == storable_task.model_id
                )
            )
        ).one()
        if current_reference != storable_task.reference:
            await __validate_storable_not_exists(
                session,
                storable_task.path,
                storable_task.reference,
                storable_task.file_type,
                storable_task.cad_type,
                model_id=storable_task.model_id,
            )
            await session.execute(
                update(model_type)
                .where(model_type.id == storable_task.model_id)
                .values(reference=storable_task.reference)
            )

        # Checks done, copy the content if available
        if storable_task.filename:
            shutil.copy(storable_task.filename, target_file)

        # Update the state
        await __store_file_set_state(
            session,
            storable_task.model_id,
            storable_task.file_type,
            StorageStatus.STORED,
        )


def __get_file_lock(
    storable_task: BaseStorableTask,
) -> filelock.BaseFileLock:
    lock_path = pathlib.Path(Config.LOCKS_DIR).joinpath(
        __storable_base_dirs[storable_task.cad_type][storable_task.file_type],
        storable_task.path + ".lock",
    )
    lock_path_dir = lock_path.parent
    if not lock_path_dir.exists():
        lock_path_dir.mkdir(parents=True)
    return filelock.FileLock(lock_path, timeout=30)


async def __store_file_validate(
    session: AsyncSession, storable_task: CreateUpdateDataStorableTask
):
    if not storable_task.filename:
        # Tasks that don't push a file don't require to validate
        # that the new payload has all the already existing references
        return
    if (
        storable_task.cad_type == CadType.KICAD
        and storable_task.file_type == StorableLibraryResourceType.FOOTPRINT
    ):
        # KiCAD footprints do not have a single file lib, each file contains one single footprint.
        # As we warranty at input time that each file has the specified reference and that
        # there is not duplication in the references the regular check to multi-model files do not
        # make sense
        return

    # Parse the library again with the lock to avoid race conditions
    library = __get_library(
        storable_task.filename, storable_task.cad_type, storable_task.file_type
    )
    references_list = (await __get_stored_references_for_id(session, storable_task)) + [
        storable_task.reference
    ]
    # The reference in the task may be the existing one if no changes to it are needed
    # or the new one if we need to update it. In any case, both needs to be present.
    for reference in references_list:
        if not library.is_present(reference):
            raise ApiError(
                f"update to {storable_task.filename} will remove an existing reference {reference}"
            )


async def __get_stored_references_for_id(
    db: AsyncSession, storable_task: BaseStorableTask
) -> [str]:
    # Get all stored references but the one we are creating
    model_type = __get_model_for_storable_type(storable_task.file_type)
    return list(
        (
            await db.scalars(
                select(model_type.reference).filter(
                    model_type.path == storable_task.path,
                    model_type.cad_type == storable_task.cad_type,
                    model_type.id != storable_task.model_id,
                    model_type.storage_status == StorageStatus.STORED,
                )
            )
        ).all()
    )


async def __validate_storable_not_exists(
    db: AsyncSession,
    storable_path: str,
    reference_name: str,
    file_type: StorableLibraryResourceType,
    cad_type: CadType,
    model_id: int = None,
):
    if file_type == StorableLibraryResourceType.FOOTPRINT and cad_type == CadType.KICAD:
        await __validate_kicad_footprint_duplication(
            db, storable_path, reference_name, model_id=model_id
        )
        # Do not do the regular checks as in KiCAD footprints each file only has a single footprint
        return

    model_type = __get_model_for_storable_type(file_type)
    query = select(model_type).filter(
        model_type.path == storable_path, model_type.reference == reference_name
    )
    query = query.filter(model_type.id != model_id) if model_id is not None else query
    exists_model = (await db.scalars(query)).first()
    if exists_model:
        raise ResourceAlreadyExistsApiError(
            "Cannot create the requested storable object cause it already exists",
            conflicting_id=exists_model.id,
        )


async def __store_file_set_state(
    session: AsyncSession,
    model_id: int,
    file_type: StorableLibraryResourceType,
    status: StorageStatus,
    error_description: str = None,
):
    model_type = __get_model_for_storable_type(file_type)
    try:
        await session.execute(
            update(model_type)
            .where(model_type.id == model_id)
            .values(storage_status=status, storage_error=error_description)
        )
        await session.commit()
    except SQLAlchemyError as err:
        __logger.error(
            __l(
                "unexpected error saving symbol reference state [model_id={0}, file_type={1}, status={2}, error_description={3}, err={4}]",
                model_id,
                file_type,
                status,
                error_description,
                str(err),
            )
        )


async def get_storable_model(
    session: AsyncSession, storable_type: StorableLibraryResourceType, model_id: int
) -> FootprintReference | LibraryReference:
    __logger.debug(
        __l(
            "Retrieving a storable object [storable_type={0}, model_id={1}]",
            storable_type.value,
            model_id,
        )
    )
    model = await session.get(__get_model_for_storable_type(storable_type), model_id)
    if not model:
        raise ResourceNotFoundApiError("Storable object not found", missing_id=model_id)

    return model


async def get_storable_model_data_path(
    session: AsyncSession, storable_type: StorableLibraryResourceType, model_id: int
) -> pathlib.Path:
    __logger.debug(
        __l(
            "Retrieving a storable object path [storable_type={0}, model_id={1}]",
            storable_type.value,
            model_id,
        )
    )
    model = await session.get(__get_model_for_storable_type(storable_type), model_id)
    if not model:
        raise ResourceNotFoundApiError("Storable object not found", missing_id=model_id)

    return __get_target_object_path(model.cad_type, storable_type, model.path)


async def get_storable_objects(
    db: AsyncSession, storable_type: StorableLibraryResourceType, page_number, page_size
) -> typing.Tuple[list[FootprintReference | LibraryReference], int]:
    __logger.debug(
        __l(
            "Querying all storable objects [storable_type={0}, page_number={1}, page_size={2}]",
            storable_type.value,
            page_number,
            page_size,
        )
    )
    return await query_page(db, select(__get_model_for_storable_type(storable_type)))
