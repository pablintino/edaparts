import typing
from sqlalchemy import func, Select
from sqlalchemy.ext.asyncio import AsyncSession


async def query_page(db: AsyncSession, query: Select) -> typing.Tuple[typing.Any, int]:
    new_query = query.add_columns(
        func.count().over().label("__private_edaparts_search_row_count")
    )
    rows_result = (await db.execute(new_query)).fetchall()
    results = []
    total = 0
    for index in range(len(rows_result)):
        row_data = rows_result[index]
        if index == 0:
            total = typing.cast(int, row_data[1])
        results.append(row_data[0])
    return results, total
