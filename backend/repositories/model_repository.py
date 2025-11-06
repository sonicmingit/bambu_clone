"""Repository helpers for reading model metadata from the database."""
from __future__ import annotations

import sqlite3
from typing import List, Optional, Sequence


class ModelRepository:
    """High level query helpers for the ``models`` table."""

    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection
        self._connection.row_factory = sqlite3.Row

    def list_models(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        keywords: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
        author_ids: Optional[Sequence[int]] = None,
    ) -> List[sqlite3.Row]:
        """Fetch paginated models with optional keyword search and tag filtering."""
        query = [
            "SELECT m.* FROM models m",
        ]
        parameters: List[object] = []
        joins: List[str] = []
        wheres: List[str] = []

        if tags:
            joins.append(
                "JOIN model_tag mt ON mt.model_id = m.id "
                "JOIN tags t ON t.id = mt.tag_id"
            )
            placeholders = ",".join(["?"] * len(tags))
            wheres.append(f"t.name IN ({placeholders})")
            parameters.extend(tags)

        if keywords:
            wheres.append("(m.name LIKE ? OR m.description LIKE ?)")
            pattern = f"%{keywords}%"
            parameters.extend([pattern, pattern])

        if author_ids:
            placeholders = ",".join(["?"] * len(author_ids))
            wheres.append(f"m.author_id IN ({placeholders})")
            parameters.extend(author_ids)

        if joins:
            query.extend(joins)

        if wheres:
            query.append("WHERE " + " AND ".join(wheres))

        query.append("GROUP BY m.id")

        if tags:
            # ensure all tags matched by counting tag occurrences
            query.append("HAVING COUNT(DISTINCT t.name) = ?")
            parameters.append(len(tags))

        query.append("ORDER BY m.updated_at DESC")
        query.append("LIMIT ? OFFSET ?")
        parameters.extend([page_size, (page - 1) * page_size])

        sql = " ".join(query)
        cursor = self._connection.execute(sql, parameters)
        return cursor.fetchall()

    def count_models(
        self,
        *,
        keywords: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
        author_ids: Optional[Sequence[int]] = None,
    ) -> int:
        """Return the total number of models that match the filters."""
        query = ["SELECT COUNT(DISTINCT m.id) FROM models m"]
        parameters: List[object] = []
        joins: List[str] = []
        wheres: List[str] = []

        if tags:
            joins.append(
                "JOIN model_tag mt ON mt.model_id = m.id "
                "JOIN tags t ON t.id = mt.tag_id"
            )
            placeholders = ",".join(["?"] * len(tags))
            wheres.append(f"t.name IN ({placeholders})")
            parameters.extend(tags)

        if keywords:
            wheres.append("(m.name LIKE ? OR m.description LIKE ?)")
            pattern = f"%{keywords}%"
            parameters.extend([pattern, pattern])

        if author_ids:
            placeholders = ",".join(["?"] * len(author_ids))
            wheres.append(f"m.author_id IN ({placeholders})")
            parameters.extend(author_ids)

        if joins:
            query.extend(joins)

        if wheres:
            query.append("WHERE " + " AND ".join(wheres))

        sql = " ".join(query)
        cursor = self._connection.execute(sql, parameters)
        result = cursor.fetchone()
        return int(result[0]) if result else 0


__all__ = ["ModelRepository"]
