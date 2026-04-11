import httpx

DEFAULT_TIMEOUT = 30.0


def create_http_client(timeout: float = DEFAULT_TIMEOUT) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout, follow_redirects=True)
