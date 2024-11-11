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

from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from edaparts.models.components.component_model import ComponentModel
from edaparts.models.inventory.inventory_item_model import InventoryItemModel
from edaparts.models.inventory.inventory_item_property import InventoryItemPropertyModel
from edaparts.models.metadata.metadata_parser import metadata_parser
from edaparts.services.exceptions import MalformedSearchQueryError
from edaparts.utils import helpers
from edaparts.utils.helpers import BraceMessage as __l


def __generate_aggregate_filter_expression(value_col_condition, key_col_condition=None):
    return (
        and_(key_col_condition, value_col_condition)
        if key_col_condition
        else value_col_condition
    )


def __create_numerical_field_filter_expression(
    field_name, operator, filter_v, key_column, value_column
):
    key_col_condition = (
        key_column == field_name if key_column.key != field_name else None
    )
    if operator == "min":
        return __generate_aggregate_filter_expression(
            value_column > filter_v, key_col_condition
        )
    if operator == "max":
        return __generate_aggregate_filter_expression(
            value_column < filter_v, key_col_condition
        )
    if operator == "maxeq":
        return __generate_aggregate_filter_expression(
            value_column <= filter_v, key_col_condition
        )
    if operator == "mineq":
        return __generate_aggregate_filter_expression(
            value_column >= filter_v, key_col_condition
        )
    if operator == "eq":
        return __generate_aggregate_filter_expression(
            value_column == filter_v, key_col_condition
        )

    raise MalformedSearchQueryError(__l("Operator {0} not recognised", operator))


def __create_string_field_filter_expression(
    field_name, operator, filter_v, key_column, value_column
):
    key_col_condition = (
        key_column == field_name if key_column.key != field_name else None
    )
    if operator == "like":
        return __generate_aggregate_filter_expression(
            value_column.like(filter_v), key_col_condition
        )
    if operator == "eq":
        return __generate_aggregate_filter_expression(
            value_column == filter_v, key_col_condition
        )
    if operator == "noteq":
        return __generate_aggregate_filter_expression(
            value_column != filter_v, key_col_condition
        )

    raise MalformedSearchQueryError(__l("Operator {0} not recognised", operator))


def __create_boolean_field_filter_expression(
    field_name, operator, filter_v, key_column, value_column
):
    key_col_condition = (
        key_column == field_name if key_column.key != field_name else None
    )
    if operator == "noteq":
        return __generate_aggregate_filter_expression(
            value_column != filter_v, key_col_condition
        )
    if operator == "eq":
        return __generate_aggregate_filter_expression(
            value_column == filter_v, key_col_condition
        )

    raise MalformedSearchQueryError(__l("Operator {0} not recognised", operator))


def __parse_item_property_filters(search_filters):
    filters = []
    for filter_key, filter_value in {
        k[5:]: v for k, v in search_filters.items() if k.startswith("prop_")
    }.items():
        filter_key_split = filter_key.split("_")
        if len(filter_key_split) < 2:
            raise MalformedSearchQueryError(
                "Item property filter should be only composed by prop_PROPNAME_OPERATOR"
            )

        # For InventoryItemPropertyModel filter the 0 index is the field name and [-1] (last) is the filter operator
        field_name = filter_key[: filter_key.rindex("_")]
        operator = filter_key_split[-1]

        # Check filter type based on values nature. If can be parsed as int it should be a number, if not check
        # if it can be a decimal number (python float). For any other case assume the property is a string.
        if helpers.is_int(filter_value) and "." not in filter_value:
            filter_condition = __create_numerical_field_filter_expression(
                field_name,
                operator,
                int(filter_value),
                InventoryItemPropertyModel.property_name,
                InventoryItemPropertyModel.property_i_value,
            )
        elif helpers.is_float(filter_value):
            filter_condition = __create_numerical_field_filter_expression(
                field_name,
                operator,
                float(filter_value),
                InventoryItemPropertyModel.property_name,
                InventoryItemPropertyModel.property_f_value,
            )
        else:
            value = filter_value if type(filter_value) is str else str(filter_value)
            filter_condition = __create_string_field_filter_expression(
                field_name,
                operator,
                value,
                InventoryItemPropertyModel.property_name,
                InventoryItemPropertyModel.property_s_value,
            )
        filters.append(filter_condition)

    return filters


def __parse_filter_for_sqlalquemy_model(model, filter_model_prefix, search_filters):
    filters = []
    item_model_metadata = metadata_parser.get_model_metadata_by_model(model)
    prefix_size = len(filter_model_prefix) + 1
    for filter_key, filter_value in {
        k[prefix_size:]: v
        for k, v in search_filters.items()
        if k.startswith(filter_model_prefix + "_")
    }.items():
        filter_key_split = filter_key.split("_")
        if len(filter_key_split) < 2:
            raise MalformedSearchQueryError(
                __l(
                    "Cannot apply filter for model {0} cause it should be only composed by {1}_PROPNAME_OPERATOR",
                    model,
                    filter_model_prefix,
                )
            )

        # For database model related filters [0] is the field name and [1] is the filter operator
        field_name = filter_key[: filter_key.rindex("_")]
        operator = filter_key_split[-1]

        field_metadata = item_model_metadata.fields.get(field_name, None)
        if not field_metadata:
            raise MalformedSearchQueryError(
                __l(
                    "Field {0} cannot be recognised as a valid field for {1}",
                    field_name,
                    model,
                )
            )

        field_column = getattr(model, field_name)

        if (
            (field_metadata.data_type is int)
            and helpers.is_int(filter_value)
            and "." not in filter_value
        ):
            filter_condition = __create_numerical_field_filter_expression(
                field_name, operator, int(filter_value), field_column, field_column
            )
        elif field_metadata.data_type is int:
            # Field is an int but the passed value is not...
            raise MalformedSearchQueryError(
                __l(
                    "Filter value for field {0} is not of the proper type {1}",
                    field_name,
                    field_metadata.data_type.__name__,
                )
            )

        elif (field_metadata.data_type is float) and helpers.is_float(filter_value):
            filter_condition = __create_numerical_field_filter_expression(
                field_name, operator, float(filter_value), field_column, field_column
            )
        elif field_metadata.data_type is float:
            # Field is a float but the passed value is not...
            raise MalformedSearchQueryError(
                __l(
                    "Filter value for field {0} is not of the proper type {1}",
                    field_name,
                    field_metadata.data_type.__name__,
                )
            )
        elif field_metadata.data_type is bool:
            bool_value = (
                True if filter_value and filter_value.lower() == "true" else False
            )
            filter_condition = __create_boolean_field_filter_expression(
                field_name, operator, bool_value, field_column, field_column
            )

        elif field_metadata.data_type is str:
            value = filter_value if type(filter_value) is str else str(filter_value)
            filter_condition = __create_string_field_filter_expression(
                field_name, operator, value, field_column, field_column
            )
        else:
            raise MalformedSearchQueryError(
                __l("Filter for field {0} is not supported", field_name)
            )

        filters.append(filter_condition)

    return filters


async def search_items(
    db: AsyncSession,
    search_filters: typing.Dict[str, str],
    page_number: int,
    page_size: int,
    load_component: bool = False,
):
    # Allow passing empty filters
    search_filters = {} if not search_filters else search_filters

    query_build = select(InventoryItemModel)
    filters = __parse_filter_for_sqlalquemy_model(
        InventoryItemModel, "item", search_filters
    )

    # Apply item property filters
    prop_filters = __parse_item_property_filters(search_filters)
    if len(prop_filters) > 0:
        filters = filters + prop_filters
        query_build = query_build.join(InventoryItemPropertyModel)

    # Apply component model filters
    if any(filt.startswith("comp_") for filt in search_filters.keys()):
        # An specific component type has been provided
        if "comp_type_eq" in search_filters and metadata_parser.model_exists_by_name(
            search_filters.get("comp_type_eq")
        ):
            component_model = metadata_parser.get_model_by_name(
                search_filters.get("comp_type_eq")
            )
        else:
            # Generic component search
            component_model = ComponentModel
        query_build = query_build.join(InventoryItemModel.component)
        filters = filters + __parse_filter_for_sqlalquemy_model(
            component_model, "comp", search_filters
        )

    if load_component:
        # joinedload instead of selectin to avoid performance issues
        query_build = query_build.options(joinedload(InventoryItemModel.component))

    # todo: apply the same search strategy to other services
    query_build = query_build.filter(*filters).order_by(InventoryItemModel.id.desc())
    query_build = query_build.limit(page_size).offset((page_number - 1) * page_size)
    _count_column_name = "__private_edaparts_search_items_row_count"
    new_query = query_build.add_columns(func.count().over().label(_count_column_name))
    rows_result = (await db.execute(new_query)).fetchall()
    results = []
    total = 0
    for index in range(len(rows_result)):
        row_data = rows_result[index]
        if index == 0:
            total = row_data[1]
        results.append(row_data[0])

    return results, total
