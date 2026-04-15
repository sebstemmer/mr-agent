import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import httpx


class MicrosoftTodoClient:
    _ONE_DAY = timedelta(days=1)
    _TOKEN_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
    _GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

    @dataclass
    class _CachedToken:
        access_token: str = ""
        expires_at: float = 0.0

    def __init__(
        self,
        client: httpx.AsyncClient,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        list_id: str,
    ):
        self._client = client
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._list_id = list_id
        self._token = self._CachedToken()

    async def find_by_status_and_due_date_between_inclusive(
        self, status: str, due_from: date | None, due_to: date | None
    ) -> list[dict]:
        filters = [f"status eq '{status}'"]
        if due_from is not None:
            filters.append(f"dueDateTime/dateTime ge '{due_from.isoformat()}'")
        if due_to is not None:
            filters.append(
                f"dueDateTime/dateTime lt '{(due_to + self._ONE_DAY).isoformat()}'"
            )
        response = await self._get(
            path=f"/me/todo/lists/{self._list_id}/tasks",
            params={"$filter": " and ".join(filters)},
        )
        return response["value"]

    async def save(
        self,
        title: str,
        due_datetime: datetime | None,
        recurrence: dict | None,
    ) -> dict:
        body: dict = {"title": title}
        if due_datetime is not None:
            body["dueDateTime"] = {
                "dateTime": due_datetime.isoformat(),
                "timeZone": "UTC",
            }
        if recurrence is not None:
            body["recurrence"] = recurrence
        return await self._post(
            path=f"/me/todo/lists/{self._list_id}/tasks",
            json=body,
        )

    async def update_status_to_completed_by_id(self, task_id: str) -> dict:
        return await self._patch(
            path=f"/me/todo/lists/{self._list_id}/tasks/{task_id}",
            json={"status": "completed"},
        )

    async def _get(self, path: str, params: dict | None = None) -> dict:
        headers = await self._auth_headers()
        response = await self._client.get(
            url=f"{self._GRAPH_BASE_URL}{path}", headers=headers, params=params
        )
        response.raise_for_status()
        return response.json()

    async def _post(self, path: str, json: dict) -> dict:
        headers = await self._auth_headers()
        response = await self._client.post(
            url=f"{self._GRAPH_BASE_URL}{path}", headers=headers, json=json
        )
        response.raise_for_status()
        return response.json()

    async def _patch(self, path: str, json: dict) -> dict:
        headers = await self._auth_headers()
        response = await self._client.patch(
            url=f"{self._GRAPH_BASE_URL}{path}", headers=headers, json=json
        )
        response.raise_for_status()
        return response.json()

    async def _auth_headers(self) -> dict[str, str]:
        if time.time() >= self._token.expires_at:
            await self._refresh_access_token()
        return {"Authorization": f"Bearer {self._token.access_token}"}

    async def _refresh_access_token(self) -> None:
        response = await self._client.post(
            url=self._TOKEN_URL,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
                "grant_type": "refresh_token",
                "scope": "Tasks.ReadWrite offline_access",
            },
        )
        response.raise_for_status()
        data = response.json()
        self._token = self._CachedToken(
            access_token=data["access_token"],
            expires_at=time.time() + data["expires_in"] - 60,
        )
