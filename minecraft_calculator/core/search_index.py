from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class SearchResult:
    item_id: str
    name: str
    match_type: str
    source_mod: str = "vanilla"


class SearchIndex:
    def __init__(self):
        self._id_index: Dict[str, str] = {}
        self._name_index: Dict[str, str] = {}
        self._item_data: Dict[str, SearchResult] = {}
        self._built: bool = False

    def build(self, recipes: Dict[str, Any]) -> None:
        self._id_index.clear()
        self._name_index.clear()
        self._item_data.clear()

        for item_id, item_recipe in recipes.items():
            if isinstance(item_recipe, dict):
                name = item_recipe.get("name", item_id)
                source_mod = item_recipe.get("_source_mod", "vanilla")
            else:
                name = getattr(item_recipe, "name", item_id)
                source_mod = getattr(item_recipe, "source_mod", "vanilla")

            self._id_index[item_id] = item_id
            self._name_index[name] = item_id
            self._id_index[item_id.lower()] = item_id
            self._name_index[name.lower()] = item_id

            self._item_data[item_id] = SearchResult(
                item_id=item_id, name=name, match_type="exact", source_mod=source_mod
            )

        self._built = True

    def search(self, query: str) -> List[SearchResult]:
        if not self._built:
            return []

        if not query:
            return []

        query_lower = query.lower()

        if query in self._id_index:
            item_id = self._id_index[query]
            return [self._item_data[item_id]]

        if query in self._name_index:
            item_id = self._name_index[query]
            return [self._item_data[item_id]]

        if query_lower in self._id_index:
            item_id = self._id_index[query_lower]
            return [self._item_data[item_id]]

        if query_lower in self._name_index:
            item_id = self._name_index[query_lower]
            return [self._item_data[item_id]]

        results: List[SearchResult] = []
        for item_id, item_recipe in self._item_data.items():
            if query_lower in item_id.lower():
                results.append(item_recipe)
            elif query_lower in item_recipe.name.lower():
                results.append(item_recipe)

        return results

    def get(self, item_id: str) -> Optional[SearchResult]:
        return self._item_data.get(item_id)

    def exists(self, item_id: str) -> bool:
        return item_id in self._item_data

    def get_all(self) -> List[SearchResult]:
        return list(self._item_data.values())

    def count(self) -> int:
        return len(self._item_data)
