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


from models.metadata import metadata_utils
import logging

__logger = logging.getLogger(__name__)

# Stores components metadata to present it to api consumers
__component_metadata = {}
__polymorphic_identities = {}
__common_component_metadata = {}


def get_component_metadata():
    items = []
    for comp_name, comp_type in __component_metadata.items():
        items.append(comp_type)
    return items


def are_fields_valid(fields):
    global __common_component_metadata
    global __component_metadata

    type_filter = fields.get('type', None)
    model_metadata = __common_component_metadata
    if type_filter:
        component_descriptor = __component_metadata.get(type_filter, None)
        if not component_descriptor:
            return False, 'Invalid query component type'
        else:
            model_metadata = component_descriptor

    for field in fields:
        if not model_metadata.get_field(field):
            return False, field
    return True, ''


def get_polymorphic_identity(identity):
    if identity in __polymorphic_identities:
        return __polymorphic_identities[identity]
    return None


def __init():
    global __component_metadata
    global __polymorphic_identities
    global __common_component_metadata
    __component_metadata = metadata_utils.get_component_metadata()
    __polymorphic_identities = metadata_utils.get_poymorphic_component_models()
    __common_component_metadata = metadata_utils.get_common_component_metadata()


# Initialize service instance
__init()
