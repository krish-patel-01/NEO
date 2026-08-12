import json
from typing import Any

import requests
import urllib3


def _get_default_params() -> dict:
    return {"language": "en", "format": "json"}


class SearxResults(dict):
    """Dict like wrapper around search API results."""

    def __init__(self, data: str):
        """Initialize the SearxResults object from raw JSON data."""
        json_data = json.loads(data)
        super().__init__(json_data)
        self.__dict__ = self

    def __str__(self) -> str:
        """Text representation of Searx result."""
        return json.dumps(self)

    @property
    def results(self) -> Any:
        """Accessor for the 'results' field in the JSON response."""
        return self.get("results")

    @property
    def answers(self) -> Any:
        """Accessor for the 'answers' field in the JSON response."""
        return self.get("answers")


class SearxSearchWrapper:
    """Wrapper for Searx API."""

    def __init__(
        self,
        searx_host: str = "",
        unsecure: bool = False,
        params: dict | None = None,
        headers: dict | None = None,
        engines: list[str] | None = None,
        categories: list[str] | None = None,
        query_suffix: str | None = "",
        k: int = 10,
    ):
        self.searx_host = searx_host
        self.unsecure = unsecure
        self.params = _get_default_params()
        if params:
            self.params.update(params)
        self.headers = headers
        self.engines = engines or []
        self.categories = categories or []
        self.query_suffix = query_suffix
        self.k = k

        # Disable SSL warnings if unsecure is True
        if self.unsecure:
            self.disable_ssl_warnings()

        # Update params with engines and categories
        if self.engines:
            self.params["engines"] = ",".join(self.engines)
        if self.categories:
            self.params["categories"] = ",".join(self.categories)

        # Validate and format searx_host
        self.validate_searx_host()

    def disable_ssl_warnings(self):
        """Disable SSL warnings."""
        try:
            urllib3.disable_warnings()
        except ImportError as e:
            print(f"Failed to import urllib3: {e}")

    def validate_searx_host(self):
        """Ensure searx_host starts with http or https."""
        if not self.searx_host.startswith("http"):
            print(f"Warning: missing URL scheme on host! Assuming secure https://{self.searx_host}")
            self.searx_host = "https://" + self.searx_host
        elif self.searx_host.startswith("http://"):
            self.unsecure = True
            self.disable_ssl_warnings()

    def _searx_api_query(self, params: dict) -> SearxResults:
        """Perform a synchronous request to the Searx API."""
        response = requests.get(
            self.searx_host,
            headers=self.headers,
            params=params,
            verify=not self.unsecure,
        )
        if not response.ok:
            raise ValueError("Searx API returned an error: ", response.text)
        return SearxResults(response.text)

    def run(
        self,
        query: str,
        engines: list[str] | None = None,
        categories: list[str] | None = None,
        query_suffix: str | None = "",
        **kwargs: Any,
    ) -> str:
        """Run query through Searx API and parse results."""
        _params = {"q": query}
        params = {**self.params, **_params, **kwargs}

        # Update query with suffixes and engines
        if self.query_suffix:
            params["q"] += " " + self.query_suffix
        if query_suffix:
            params["q"] += " " + query_suffix
        if engines:
            params["engines"] = ",".join(engines)
        if categories:
            params["categories"] = ",".join(categories)

        res = self._searx_api_query(params)

        if res.answers:
            return res.answers[0]
        elif res.results:
            return "\n\n".join([r.get("content", "") for r in res.results[: self.k]])
        else:
            return "No good search result found"

    def results(
        self,
        query: str,
        num_results: int,
        engines: list[str] | None = None,
        categories: list[str] | None = None,
        query_suffix: str | None = "",
        **kwargs: Any,
    ) -> list[dict]:
        """Run query through Searx API and return results with metadata."""
        _params = {"q": query}
        params = {**self.params, **_params, **kwargs}

        # Update query with suffixes and engines
        if self.query_suffix:
            params["q"] += " " + self.query_suffix
        if query_suffix:
            params["q"] += " " + query_suffix
        if engines:
            params["engines"] = ",".join(engines)
        if categories:
            params["categories"] = ",".join(categories)

        results = self._searx_api_query(params).results[:num_results]

        if not results:
            return [{"Result": "No good Search Result was found"}]

        return [
            {
                "snippet": result.get("content", ""),
                "title": result["title"],
                "link": result["url"],
                "engines": result["engines"],
                "category": result["category"],
            }
            for result in results
        ]


# if __name__ == "__main__":
#     search = SearxSearchWrapper(
#         searx_host="http://127.0.0.1:8080", k=8,
#         engines=['google', 'duckduckgo','wikipedia'],
#     )
#     query = """What is the capital of Nigeria?"""
#     print(search.run(query))
