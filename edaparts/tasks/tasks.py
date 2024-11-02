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


import sys

from git import GitError
from sqlalchemy.exc import SQLAlchemyError

from app import create_app, db
from models import FootprintReference, LibraryReference
from models.internal.internal_models import StorableLibraryResourceType, StorageStatus
from services import storage_service, exceptions
import logging

__logger = logging.getLogger(__name__)

app = create_app()
app.app_context().push()


def __save_storage_status(model, status):
    if model:
        try:
            model.set_storage_status(status)
            db.session.add(model)
            db.session.commit()
        except SQLAlchemyError as error:
            __logger.error(f'Error persisting storage status: {error}')
    else:
        __logger.error(f'Cannot persist storage status cause model was not provided')

def __get_model_and_path(storage_resource_type, element_id):
    file_path = None
    model = None
    if storage_resource_type == StorableLibraryResourceType.FOOTPRINT:
        model = FootprintReference.query.get(element_id)
        if not model:
            __logger.warning(f'Element with ID {element_id} not found. Quiting...')
            raise exceptions.ResourceNotFoundApiError('Footprint not found', missing_id=element_id)
        file_path = model.footprint_path
    elif storage_resource_type == StorableLibraryResourceType.SYMBOL:
        model = LibraryReference.query.get(element_id)
        if not model:
            __logger.warning(f'Element with ID {element_id} not found. Quiting...')
            raise exceptions.ResourceNotFoundApiError('Schematic symbol not found', missing_id=element_id)
        file_path = model.symbol_path
    else:
        __logger.error(f'A non supported storage type was passed to storage task {storage_resource_type}')
    return model, file_path


def store_data(storage_resource_type, element_id, encoded_data):
    model = None
    try:
        __logger.debug(f'Begin storing {storage_resource_type.name} with ID {element_id}')
        model, file_path = __get_model_and_path(storage_resource_type, element_id)

        if model and file_path:
            __save_storage_status(model, StorageStatus.STORING)

            storage_service.add_file_to_repo(file_path, encoded_data)

            # Update storage status
            __save_storage_status(model, StorageStatus.STORED)

            __logger.debug(f'Finished storing {storage_resource_type.name} with ID {element_id}')
        else:
            __logger.error(f'Cannot obtain model or file path for element with ID {element_id}')

    except exceptions.ResourceNotFoundApiError as error:
        __logger.error(f'Model to store not found: {error}')
    except (IOError, GitError, SQLAlchemyError) as error:
        __save_storage_status(model, StorageStatus.STORAGE_FAILED)
        __logger.error(f'Unhandled exception: {error}', exc_info=sys.exc_info())
