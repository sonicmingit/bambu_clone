from __future__ import annotations

import json
import re
from contextvars import ContextVar
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

__all__ = [
    "Flask",
    "Blueprint",
    "abort",
    "current_app",
    "jsonify",
    "request",
    "send_file",
]


class HTTPException(Exception):
    def __init__(self, status_code: int, description: str | None = None) -> None:
        self.status_code = status_code
        self.description = description or ""
        super().__init__(self.description)


_current_app: ContextVar["Flask"] = ContextVar("current_app")
_request: ContextVar["Request"] = ContextVar("request")


class Headers(dict):
    def get(self, key: str, default: Any = None) -> Any:  # type: ignore[override]
        if key in self:
            return super().get(key, default)
        lowered = key.lower()
        for existing_key, value in self.items():
            if existing_key.lower() == lowered:
                return value
        return default


@dataclass
class Response:
    data: bytes = b""
    status_code: int = 200
    mimetype: str = "text/plain"
    headers: Dict[str, str] = field(default_factory=dict)

    @property
    def content(self) -> bytes:
        return self.data

    @property
    def content_type(self) -> str:
        return self.mimetype

    def get_json(self) -> Any:
        return json.loads(self.data.decode("utf-8"))


class Request:
    def __init__(self, headers: Optional[Dict[str, str]] = None) -> None:
        self.headers: Headers = Headers(headers or {})


class _LocalProxy:
    def __init__(self, lookup: Callable[[], Any]) -> None:
        object.__setattr__(self, "_lookup", lookup)

    def __getattr__(self, item: str) -> Any:
        return getattr(self._lookup(), item)

    def __setattr__(self, key: str, value: Any) -> None:
        setattr(self._lookup(), key, value)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._lookup()(*args, **kwargs)


request = _LocalProxy(lambda: _request.get())
current_app = _LocalProxy(lambda: _current_app.get())


@dataclass
class Route:
    methods: List[str]
    rule: str
    func: Callable[..., Any]
    pattern: re.Pattern[str]


class Blueprint:
    def __init__(self, name: str, import_name: str, url_prefix: str = "") -> None:
        self.name = name
        self.import_name = import_name
        self.url_prefix = url_prefix.rstrip("/")
        self._routes: List[Route] = []

    def route(self, rule: str, methods: Optional[Iterable[str]] = None) -> Callable:
        methods_list = [method.upper() for method in (methods or ["GET"])]
        path = self._join_paths(rule)
        pattern = self._compile_pattern(path)

        def decorator(func: Callable) -> Callable:
            self._routes.append(Route(methods_list, path, func, pattern))
            return func

        return decorator

    def get(self, rule: str) -> Callable:
        return self.route(rule, methods=["GET"])

    def post(self, rule: str) -> Callable:
        return self.route(rule, methods=["POST"])

    def iter_routes(self) -> Iterable[Route]:
        return list(self._routes)

    def _join_paths(self, rule: str) -> str:
        rule = rule or ""
        if not rule.startswith("/"):
            rule = f"/{rule}"
        return f"{self.url_prefix}{rule}" if self.url_prefix else rule

    @staticmethod
    def _compile_pattern(path: str) -> re.Pattern[str]:
        pattern = re.sub(r"<([^>]+)>", r"(?P<\1>[^/]+)", path.rstrip("/"))
        if not pattern:
            pattern = "/"
        return re.compile(f"^{pattern}$")


class Flask:
    def __init__(self, import_name: str) -> None:
        self.import_name = import_name
        self.config: Dict[str, Any] = {}
        self._routes: List[Route] = []

    def route(self, rule: str, methods: Optional[Iterable[str]] = None) -> Callable:
        methods_list = [method.upper() for method in (methods or ["GET"])]
        path = self._normalize_rule(rule)
        pattern = Blueprint._compile_pattern(path)

        def decorator(func: Callable) -> Callable:
            self._routes.append(Route(methods_list, path, func, pattern))
            return func

        return decorator

    def get(self, rule: str) -> Callable:
        return self.route(rule, methods=["GET"])

    def post(self, rule: str) -> Callable:
        return self.route(rule, methods=["POST"])

    def register_blueprint(self, blueprint: Blueprint) -> None:
        self._routes.extend(blueprint.iter_routes())

    def test_client(self) -> "TestClient":
        return TestClient(self)

    def handle_request(self, method: str, path: str, headers: Optional[Dict[str, str]] = None) -> Response:
        headers = headers or {}
        normalized_path = path.rstrip("/") or "/"
        route, params = self._find_handler(method, normalized_path)
        app_token = _current_app.set(self)
        request_obj = Request(headers)
        request_token = _request.set(request_obj)
        try:
            result = route.func(**params)
            response = self._coerce_to_response(result)
        except HTTPException as exc:  # pragma: no cover - defensive
            response = jsonify({"message": exc.description})
            response.status_code = exc.status_code
        finally:
            _request.reset(request_token)
            _current_app.reset(app_token)
        return response

    def _find_handler(self, method: str, path: str) -> Tuple[Route, Dict[str, str]]:
        for route in self._routes:
            if method.upper() not in route.methods:
                continue
            match = route.pattern.match(path)
            if match:
                return route, match.groupdict()
        raise HTTPException(404, "Not Found")

    @staticmethod
    def _normalize_rule(rule: str) -> str:
        rule = rule or ""
        if not rule.startswith("/"):
            rule = f"/{rule}"
        return rule

    def _coerce_to_response(self, result: Any) -> Response:
        if isinstance(result, Response):
            return result
        if isinstance(result, tuple):
            body, status = result
            response = self._coerce_to_response(body)
            response.status_code = status
            return response
        if isinstance(result, (bytes, bytearray)):
            return Response(bytes(result))
        if isinstance(result, str):
            return Response(result.encode("utf-8"), mimetype="text/plain; charset=utf-8")
        return jsonify(result)


class TestClient:
    def __init__(self, app: Flask) -> None:
        self.app = app

    def open(self, path: str, method: str = "GET", headers: Optional[Dict[str, str]] = None):
        return self.app.handle_request(method, path, headers=headers)

    def get(self, path: str, headers: Optional[Dict[str, str]] = None):
        response = self.open(path, "GET", headers=headers)
        response.mimetype = response.mimetype or "application/octet-stream"
        return response

    def post(self, path: str, headers: Optional[Dict[str, str]] = None):
        response = self.open(path, "POST", headers=headers)
        response.mimetype = response.mimetype or "application/octet-stream"
        return response


def abort(status_code: int, description: str | None = None) -> None:
    raise HTTPException(status_code, description)


def jsonify(data: Any) -> Response:
    payload = json.dumps(data).encode("utf-8")
    return Response(payload, mimetype="application/json")


def send_file(file_obj: BytesIO, mimetype: str, as_attachment: bool = False, download_name: str | None = None) -> Response:
    data = file_obj.read()
    headers: Dict[str, str] = {}
    if as_attachment and download_name:
        headers["Content-Disposition"] = f"attachment; filename={download_name}"
    return Response(data, mimetype=mimetype, headers=headers)
