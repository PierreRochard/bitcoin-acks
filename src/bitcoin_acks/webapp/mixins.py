from sqlalchemy import nullsfirst, nullslast, desc


class NullOrderMixinView(object):
    """
    A mixin view that will allow setting NULLS FIRST or NULLS LAST

    """

    def _order_by(self, query, joins, sort_joins, sort_field, sort_desc):
        """
            Apply order_by to the query

            :param query:
                Query
            :pram joins:
                Current joins
            :param sort_joins:
                Sort joins (properties or tables)
            :param sort_field:
                Sort field
            :param sort_desc:
                Select sort order:
                * True: for descending order
                * False or None: for ascending default order
                * 'LAST': for NULLS LAST
                * 'FIRST': for NULLS FIRST
        """
        if sort_field is not None:
            # Handle joins
            query, joins, alias = self._apply_path_joins(query, joins, sort_joins, inner_join=False)

            column = sort_field if alias is None else getattr(alias, sort_field.key)

            if sort_desc is True:
                if isinstance(column, tuple):
                    query = query.order_by(*map(desc, column))
                else:
                    query = query.order_by(desc(column))
            elif sort_desc is False:
                if isinstance(column, tuple):
                    query = query.order_by(*column)
                else:
                    query = query.order_by(column)
            elif sort_desc == 'LAST':
                query = query.order_by(nullslast(desc(column)))
            elif sort_desc == 'FIRST':
                query = query.order_by(nullsfirst(desc(column)))

        return query, joins
