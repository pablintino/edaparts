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


from flask import request
from marshmallow import ValidationError

from dtos.footprints_dtos import FootprintIdsComponentReferencesDto, FootprintDto, FootprintComponentReferencesDto
from dtos.schemas.footprint_schemas import FootprintSchema, FootprintsComponentReferencesSchema, \
    FootprintIdsComponentReferencesSchema
from rest_layer import rest_layer_utils
from rest_layer.base_api_resource import BaseApiResource
from services import component_service, storage_service
from services.exceptions import ApiError, InvalidRequestError


class FootprintComponentReferenceResource(BaseApiResource):
    def post(self, id):
        try:
            footprints_ids = FootprintIdsComponentReferencesSchema().load(data=request.json).footprint_ids
            actual_ids = component_service.create_footprints_relation(id, footprints_ids)
            return FootprintIdsComponentReferencesSchema().dump(
                FootprintIdsComponentReferencesDto.from_model(actual_ids)), 200
        except ValidationError as error:
            return {"errors": error.messages}, 400
        except ApiError as error:
            self.logger().debug(error)
            return error.format_api_data()

    def get(self, id):
        try:
            retrieve_all = rest_layer_utils.is_all_data_request_flag()
            retrieve_encoded_data = rest_layer_utils.is_encoded_data_request_flag()

            # Protection against full requests requested as an "id only" request
            if retrieve_encoded_data and not retrieve_all:
                raise InvalidRequestError('Cannot retrieve encoded metadata for a non full request')

            footprints_data = component_service.get_component_footprint_relations(id, retrieve_all)
            if not retrieve_all:
                resp = FootprintIdsComponentReferencesSchema().dump(
                    FootprintIdsComponentReferencesDto.from_model(footprints_data))
            else:
                dtos = []
                for footprint_data in footprints_data:
                    encoded_data = storage_service.get_encoded_file_from_repo(
                        footprint_data) if retrieve_encoded_data else None
                    dtos.append(FootprintSchema().dump(FootprintDto.from_model(footprint_data, encoded_data)))
                resp = FootprintsComponentReferencesSchema().dump(FootprintComponentReferencesDto.from_model(dtos))

            return resp, 200
        except ApiError as error:
            self.logger().debug(error)
            return error.format_api_data()
