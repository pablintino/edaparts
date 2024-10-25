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

from datetime import datetime

from models.metadata.metadata_parser import metadata_parser
from services.exceptions import InvalidComponentTypeError, InvalidComponentFieldsError


def __calculate_not_present_mandatory(component_metadata, raw_component, pk_provided):
    return [
        req.name
        for req in list(
            filter(
                lambda x: x.is_mandatory
                and not x.is_pk
                and x.name not in raw_component
                or x.is_pk
                and pk_provided
                and x.name not in raw_component,
                component_metadata.fields.values(),
            )
        )
    ]


def __map_fields_type(raw_fields, fields_metadata):
    invalid_type_fields = []
    mapped_fields = {}
    for k, v in raw_fields.items():

        if v is None:
            mapped_fields[k] = v
        elif fields_metadata[k].data_type is type(v):
            mapped_fields[k] = v
        elif fields_metadata[k].data_type is int and type(v) is str:
            mapped_fields[k] = int(v)
        elif fields_metadata[k].data_type is float and type(v) is str:
            mapped_fields[k] = float(v)
        elif fields_metadata[k].data_type is bool and type(v) is str:
            return v == "True"
        elif fields_metadata[k].data_type is datetime and type(v) is str:
            mapped_fields[k] = datetime.fromisoformat(v)
        else:
            invalid_type_fields.append(k)
    if len(invalid_type_fields) > 0:
        raise InvalidComponentFieldsError(
            "The provided component data types has errors",
            unexpected_types=invalid_type_fields,
        )

    return mapped_fields


def __validate(raw_component, component_metadata, pk_provided, ignore_mandatory):
    # Calculate fields that are present in the provided component but are not part of the model
    unrecognised_fields = [
        ureq
        for ureq in raw_component
        if ureq not in component_metadata.fields and (ureq != "type")
    ]

    # Calculate fields that the model claims as mandatory but are not provided in the component
    # Only if ignore_mandatory is false (typically done for already created components that are going to be updated)
    not_present_mandatory = (
        __calculate_not_present_mandatory(
            component_metadata, raw_component, pk_provided
        )
        if not ignore_mandatory
        else []
    )

    # If mandatory fields are not provided or there are unrecognised fields just raise a validation error
    if len(unrecognised_fields) > 0 or len(not_present_mandatory) > 0:
        raise InvalidComponentFieldsError(
            "The provided component data is invalid",
            unrecognised_fields=unrecognised_fields,
            mandatory_missing=not_present_mandatory,
        )


def map_validate_raw(
    raw_component, pk_provided=False, ignore_mandatory=False, force_type=None
):
    component_type = raw_component.get("type", None) if not force_type else force_type
    if component_type and not metadata_parser.model_exists_by_name(component_type):
        raise InvalidComponentTypeError(
            "Component type " + component_type + " not recognised"
        )
    elif not component_type:
        raise InvalidComponentTypeError("Component type not provided")

    component_metadata = metadata_parser.get_model_metadata_by_name(component_type)

    # Validate invalid or unexpected fields
    __validate(raw_component, component_metadata, pk_provided, ignore_mandatory)

    return __map_fields_type(raw_component, component_metadata.fields)


def map_validate_raw_to_model(raw_component, pk_provided=False):

    mapped_fields = map_validate_raw(raw_component, pk_provided=pk_provided)

    # Call to raw_component.get('type', None) is safe here since raw was already validated
    mapped_model = metadata_parser.get_model_by_name(raw_component.get("type", None))(
        **mapped_fields
    )
    return mapped_model


def map_model_to_raw(model):
    mapped_fields = {}
    if model:
        for k, v in metadata_parser.get_model_metadata_by_name(
            model.type
        ).fields.items():
            if k in model.__dict__:
                value = model.__dict__[k]
                value_type = type(value)
                if (
                    value_type is str
                    or value_type is float
                    or value_type is int
                    or value_type is bool
                ):
                    mapped_fields[k] = value
                elif value_type is datetime:
                    mapped_fields[k] = value.isoformat()
        return mapped_fields

    return None
