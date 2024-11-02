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


# base app exception
from datetime import datetime


class ApiError(Exception):
    def __init__(self, msg=None, details=None, http_code=500):
        super(ApiError, self).__init__(msg)
        self.msg = str(msg)
        self.details = details
        self.http_code = http_code

    def format_api_data(self):
        data = {"message": self.msg, "timestamp": datetime.now().isoformat()}
        if self.details:
            data["details"] = self.details
        return data, self.http_code

    def __str__(self):
        return "%s[%s]" % (
            type(self).__name__,
            ", ".join("%s=%s" % item for item in vars(self).items()),
        )


class ResourceNotFoundApiError(ApiError):

    def __init__(self, msg=None, details=None, missing_id=None, missing_dici=None):
        super(ResourceNotFoundApiError, self).__init__(msg, details, 404)
        self.missing_id = missing_id
        self.missing_dici = missing_dici

    def format_api_data(self):
        data, code = super(ResourceNotFoundApiError, self).format_api_data()
        if self.missing_id:
            data["missing_id"] = self.missing_id
        if self.missing_dici:
            data["missing_dici"] = self.missing_dici
        return data, code


class ResourceAlreadyExistsApiError(ApiError):
    def __init__(self, msg=None, details=None, conflicting_id=None):
        super(ResourceAlreadyExistsApiError, self).__init__(msg, details, 400)
        self.conflicting_id = conflicting_id

    def format_api_data(self):
        data, code = super(ResourceAlreadyExistsApiError, self).format_api_data()
        if self.conflicting_id:
            data["conflicting_id"] = self.conflicting_id
        return data, code


class ResourceInvalidQuery(ApiError):
    def __init__(self, msg=None, details=None, invalid_fields=None):
        super(ResourceInvalidQuery, self).__init__(msg, details, 400)
        self.invalid_fields = invalid_fields

    def format_api_data(self):
        data, code = super(ResourceInvalidQuery, self).format_api_data()
        if self.invalid_fields:
            data["invalid_fields"] = self.invalid_fields
        return data, code


class InvalidComponentTypeError(ApiError):
    def __init__(self, msg=None, details=None):
        super(InvalidComponentTypeError, self).__init__(msg, details, 400)


class InvalidComponentFieldsError(ApiError):
    def __init__(
        self,
        msg=None,
        details=None,
        unrecognised_fields=None,
        mandatory_missing=None,
        unexpected_types=None,
        reserved_fields=None,
    ):
        super(InvalidComponentFieldsError, self).__init__(msg, details, 400)
        self.unrecognised_fields = unrecognised_fields
        self.mandatory_missing = mandatory_missing
        self.unexpected_types = unexpected_types
        self.reserved_fields = reserved_fields

    def format_api_data(self):
        data, code = super(InvalidComponentFieldsError, self).format_api_data()
        if self.unrecognised_fields:
            data["unrecognised_fields"] = self.unrecognised_fields
        if self.mandatory_missing:
            data["mandatory_missing"] = self.mandatory_missing
        if self.unexpected_types:
            data["unexpected_types"] = self.unexpected_types
        if self.reserved_fields:
            data["reserved_fields"] = self.reserved_fields
        return data, code


class InvalidSymbolApiError(ApiError):
    def __init__(self, msg=None, details=None):
        super(InvalidSymbolApiError, self).__init__(msg, details, 400)


class InvalidFootprintApiError(ApiError):
    def __init__(self, msg=None, details=None):
        super(InvalidFootprintApiError, self).__init__(msg, details, 400)


class InvalidMultipartFileDataError(ApiError):
    def __init__(self, msg=None, details=None):
        super(InvalidMultipartFileDataError, self).__init__(msg, details, 400)


class InvalidStorageStateError(ApiError):
    def __init__(self, msg=None, details=None, entity_id=None, current_state=None):
        super(InvalidStorageStateError, self).__init__(msg, details, 400)
        self.current_state = current_state
        self.entity_id = entity_id

    def format_api_data(self):
        data, code = super(InvalidStorageStateError, self).format_api_data()
        if self.entity_id:
            data["entity_id"] = self.entity_id
        if self.current_state:
            data["current_state"] = self.current_state
        return data, code


class FileNotFoundStorageError(ApiError):
    def __init__(self, msg=None, details=None):
        super(FileNotFoundStorageError, self).__init__(msg, details, 404)


class InvalidStorableTypeError(ApiError):
    def __init__(self, msg=None, details=None):
        super(InvalidStorableTypeError, self).__init__(msg, details, 400)


class InvalidRequestError(ApiError):
    def __init__(self, msg=None, details=None):
        super(InvalidRequestError, self).__init__(msg, details, 400)


class RelationAlreadyExistsError(ApiError):
    def __init__(self, msg=None, details=None):
        super(RelationAlreadyExistsError, self).__init__(msg, details, 400)


class RelationExistsError(ApiError):
    def __init__(self, msg=None, details=None):
        super(RelationExistsError, self).__init__(msg, details, 400)


class SchemaNotAvailableError(ApiError):
    def __init__(self, msg=None, details=None):
        super(SchemaNotAvailableError, self).__init__(msg, details, 500)


class UniqueIdentifierCreationError(ApiError):
    def __init__(self, msg=None, details=None):
        super(UniqueIdentifierCreationError, self).__init__(msg, details, 500)


class RemainingStocksExistError(ApiError):
    def __init__(self, msg=None, details=None):
        super(RemainingStocksExistError, self).__init__(msg, details, 400)


class InvalidMassStockUpdateError(ApiError):
    def __init__(self, msg=None, details=None):
        super(InvalidMassStockUpdateError, self).__init__(msg, details, 400)


class MalformedSearchQueryError(ApiError):
    def __init__(self, msg=None, details=None):
        super(MalformedSearchQueryError, self).__init__(msg, details, 400)


class GenericIntenalApiError(ApiError):
    def __init__(self, msg=None, details=None):
        super(GenericIntenalApiError, self).__init__(msg, details, 500)


class CyclicCategoryDependecy(ApiError):
    def __init__(self, msg=None, details=None):
        super(CyclicCategoryDependecy, self).__init__(msg, details, 400)


class InvalidCategoryRelationError(ApiError):
    def __init__(self, msg=None, details=None):
        super(InvalidCategoryRelationError, self).__init__(msg, details, 400)
