"""Integration with ``variants.queries``.

TODO: we need to limit the annotations to those that the user has access to (via project).
"""

from sqlalchemy import true
from sqlalchemy.sql import and_, func, select

from varannos.models import VarAnnoSetEntry
from variants.models import SmallVariant
from variants.queries import ExtendQueryPartsBase, same_variant


class ExtendQueryPartsVarAnnosJoin(ExtendQueryPartsBase):
    """Extend query from ``variants.queries`` to join with the ``VarAnnoSetEntry`` model."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = (
            select(
                [
                    func.count().label("varannos_varannosetentry_count_inner"),
                ]
            )
            .select_from(VarAnnoSetEntry.sa)
            .where(
                and_(
                    same_variant(SmallVariant, VarAnnoSetEntry),
                )
            )
            .distinct(  # DISTINCT ON
                SmallVariant.sa.release,
                SmallVariant.sa.chromosome,
                SmallVariant.sa.start,
                SmallVariant.sa.end,
                SmallVariant.sa.reference,
                SmallVariant.sa.alternative,
            )
            .lateral("varannos_subquery")
        )

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())

    def extend_fields(self, _query_parts):
        return [
            func.coalesce(self.subquery.c.varannos_varannosetentry_count_inner, 0).label(
                "varannos_varannosetentry_count"
            ),
        ]
