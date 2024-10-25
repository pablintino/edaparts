#
# MIT License
#
# Copyright (c) 2020 Pablo Rodriguez Nava, @pablintino
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


import base64
import binascii
import logging

from edaparts.models import FootprintReference, LibraryReference
from edaparts.models.internal.internal_models import (
    StorableLibraryResourceType,
    StorageStatus,
)
from edaparts.services import storage_service
from edaparts.services.exceptions import (
    ResourceAlreadyExistsApiError,
    ResourceNotFoundApiError,
    InvalidFootprintApiError,
    InvalidSymbolApiError,
    InvalidStorableTypeError,
)
from edaparts.utils import parse_olefile_library, LibType
from edaparts.utils.helpers import BraceMessage as __l

__logger = logging.getLogger(__name__)


def __validate_storable_type(storable_type):
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


def __get_model_for_storable_type(storable_type):
    __validate_storable_type(storable_type)
    return (
        FootprintReference
        if storable_type == StorableLibraryResourceType.FOOTPRINT
        else LibraryReference
    )


def __get_library(expected_type, encoded_data):
    # Encoded data is mandatory in order to parse the binary Altium lib
    if not encoded_data:
        raise __get_error_for_type(expected_type)("Encoded library data not provided")

    try:
        # Parse the given data
        decoded_data = base64.b64decode(encoded_data)
        lib = parse_olefile_library(decoded_data)

        # Be sure that the encoded data is of the expected type
        if (
            expected_type == StorableLibraryResourceType.SYMBOL
            and lib.lib_type != LibType.SCH
        ) or (
            expected_type == StorableLibraryResourceType.FOOTPRINT
            and lib.lib_type != LibType.PCB
        ):
            raise __get_error_for_type(expected_type)(
                "The given encoded data is not of the expected type. {expected_type="
                + (
                    LibType.SCH.value
                    if expected_type == StorableLibraryResourceType.SYMBOL
                    else LibType.PCB.value
                )
                + ", actual_type="
                + lib.lib_type.value
                + "}"
            )

        return lib
    except binascii.Error:
        raise __get_error_for_type(expected_type)(
            "Invalid base64 encoded data. Incorrect padding"
        )
    except IOError as err:
        raise __get_error_for_type(expected_type)(
            f"The given Altium file is corrupt",
            err.args[0] if len(err.args) > 0 else None,
        )


def __update_model_reference(storable_type, model, new_reference):
    actual_entity = (
        db.session.query(LibraryReference.id)
        .filter_by(symbol_path=model.get_file_path(), symbol_ref=new_reference)
        .scalar()
        if storable_type == StorableLibraryResourceType.SYMBOL
        else db.session.query(FootprintReference.id)
        .filter_by(footprint_path=model.get_file_path(), footprint_ref=new_reference)
        .scalar()
    )

    if actual_entity:
        raise ResourceAlreadyExistsApiError(
            "Cannot create the requested component cause it already exists",
            conflicting_id=actual_entity.id,
        )

    model.set_reference(new_reference)
    db.session.add(model)
    db.session.commit()


def update_object_data(storable_type, model_id, encoded_data):
    model = __get_model_for_storable_type(storable_type).query.get(model_id)
    if not model:
        raise ResourceNotFoundApiError("Storable object not found", missing_id=model_id)

    # If the model has already been stored and its content is the same just skip updating
    if (
        model.get_storage_status() is StorageStatus.STORED
        and encoded_data == storage_service.get_encoded_file_from_repo(model)
    ):
        __logger.debug(
            "Given new storable object data has the same content as the current one. Skipping..."
        )
        return

    lib = __get_library(storable_type, encoded_data)

    # If a reference was provided it should be a valid one
    if model.get_reference() and not lib.part_exists(model.get_reference()):
        __get_error_for_type(storable_type)(
            "The provided reference was not found in the given library"
        )

    if model.get_reference() and lib.part_exists(model.get_reference()):
        # Simple update of the library, no database changes needed
        __logger.debug(
            __l(
                "Updating storable object data without reference update. [storable_type={0}, reference={1}, model_id={2}]",
                storable_type.value,
                model.get_reference(),
                model_id,
            )
        )
    elif lib.count == 1:
        # Update reference and if success change data in repo
        new_reference = lib.parts[next(iter(lib.parts.keys()))].name
        __logger.debug(
            __l(
                "Updating storable object data and reference [storable_type={0}, new_reference={1}, old_reference={2}, model_id={3}]",
                storable_type.value,
                new_reference,
                model.get_reference(),
                model_id,
            )
        )
        __update_model_reference(storable_type, model, new_reference)
    else:
        # Cannot update the library file
        raise __get_error_for_type(storable_type)(
            "Ambiguous library update. Provide a reference"
        )

    # Reset storage status
    model.set_storage_status(StorageStatus.NOT_STORED)
    db.session.add(model)
    db.session.commit()

    # Signal background process to store the storable object
    # todo: DATA PARSING AND HANDLING
    # rq_helpers.launch_storage_task(storable_type, model.id, encoded_data)


def create_storable_library_object(
    storable_type, reference_name, storable_path, description, encoded_data
):
    __validate_storable_type(storable_type)

    # Parse storable object from encoded data and check its content
    lib = __get_library(storable_type, encoded_data)

    # Verify that the body contains enough information
    if not reference_name:
        # Try to obtain the reference from the library data
        if lib.count != 1:
            raise __get_error_for_type(storable_type)(
                "More than one part in the given library. Provide a reference"
            )

        reference_name = lib.parts[next(iter(lib.parts.keys()))].name

    # If check that the given reference exists
    if not lib.part_exists(reference_name):
        raise __get_error_for_type(storable_type)(
            "The given reference does not exist in the given library "
        )

    # If no description is provided try to populate it from library data
    if not description:
        description = lib.parts[reference_name].description

    __logger.debug(
        __l(
            "Creating a new storable object [storable_type={0}, reference_name={1}, storable_path={2}, description={3}]",
            storable_type.value,
            reference_name,
            storable_path,
            description,
        )
    )

    exists_id = (
        db.session.query(LibraryReference.id)
        .filter_by(symbol_path=storable_path, symbol_ref=reference_name)
        .scalar()
        if storable_type == StorableLibraryResourceType.SYMBOL
        else db.session.query(FootprintReference.id)
        .filter_by(footprint_path=storable_path, footprint_ref=reference_name)
        .scalar()
    )

    if exists_id:
        raise ResourceAlreadyExistsApiError(
            "Cannot create the requested storable object cause it already exists",
            conflicting_id=exists_id,
        )

    # Create a model based on the storable object type
    model = (
        FootprintReference(
            footprint_path=storable_path,
            footprint_ref=reference_name,
            description=description,
        )
        if storable_type == StorableLibraryResourceType.FOOTPRINT
        else LibraryReference(
            symbol_path=storable_path,
            symbol_ref=reference_name,
            description=description,
        )
    )

    # Ensure that storage status at creation time is set to NOT_STORED
    model.set_storage_status(StorageStatus.NOT_STORED)

    db.session.add(model)
    db.session.commit()
    __logger.debug(__l("Storable object created [id={0}]", model.id))

    # Signal background process to store the object
    # todo: DATA PARSING AND HANDLING
    # rq_helpers.launch_storage_task(storable_type, model.id, encoded_data)

    return model


def get_storable_model(storable_type, model_id):
    __logger.debug(
        __l(
            "Retrieving a storable object [storable_type={0}, model_id={1}]",
            storable_type.value,
            model_id,
        )
    )
    model = __get_model_for_storable_type(storable_type).query.get(model_id)
    if not model:
        raise ResourceNotFoundApiError("Storable object not found", missing_id=model_id)

    return model


def get_storable_objects(storable_type, page_number, page_size):
    __logger.debug(
        __l(
            "Querying all storable objects [storable_type={0}, page_number={1}, page_size={2}]",
            storable_type.value,
            page_number,
            page_size,
        )
    )

    model_type = __get_model_for_storable_type(storable_type)
    objects_page = model_type.query.order_by(model_type.id.desc()).paginate(
        page=page_number, per_page=page_size
    )

    return objects_page
