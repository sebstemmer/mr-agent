import logging
import time
from dataclasses import dataclass
from datetime import date, timedelta

import httpx
from utils.common.src.update_field import Update, UpdateField

from microsoft_todo.src.task_status import TaskStatus


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
        logger: logging.Logger,
    ):
        self._client = client
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._logger = logger
        self._token = self._CachedToken()

    async def find_by_status_and_due_date_between_inclusive(
        self,
        list_id: str,
        status: TaskStatus,
        due_from: date | None,
        due_to: date | None,
    ) -> list[dict]:
        filters = [f"status eq '{status.value}'"]
        if due_from is not None:
            filters.append(f"dueDateTime/dateTime ge '{due_from.isoformat()}'")
        if due_to is not None:
            filters.append(
                f"dueDateTime/dateTime lt '{(due_to + self._ONE_DAY).isoformat()}'"
            )
        response = await self._request(
            method="GET",
            path=f"/me/todo/lists/{list_id}/tasks",
            params={"$filter": " and ".join(filters)},
        )
        return response["value"]

    async def save(
        self,
        list_id: str,
        title: str,
        due_date: date | None,
        recurrence: dict | None,
    ) -> dict:
        body: dict = {"title": title}
        if recurrence is not None:
            body["recurrence"] = recurrence
            if due_date is None:
                due_date = date.fromisoformat(recurrence["range"]["startDate"])
        if due_date is not None:
            body["dueDateTime"] = {
                "dateTime": due_date.isoformat(),
                "timeZone": "UTC",
            }
        return await self._request(
            method="POST",
            path=f"/me/todo/lists/{list_id}/tasks",
            json=body,
        )

    async def update_by_id(
        self,
        list_id: str,
        task_id: str,
        title: UpdateField[str],
        due_date: UpdateField[date | None],
        status: UpdateField[TaskStatus],
        completed_date: UpdateField[date | None],
    ) -> dict:
        body: dict = {}
        if isinstance(title, Update):
            body["title"] = title.value
        if isinstance(due_date, Update):
            body["dueDateTime"] = (
                {"dateTime": due_date.value.isoformat(), "timeZone": "UTC"}
                if due_date.value is not None
                else None
            )
        if isinstance(status, Update):
            body["status"] = status.value.value
        if isinstance(completed_date, Update):
            body["completedDateTime"] = (
                {"dateTime": completed_date.value.isoformat(), "timeZone": "UTC"}
                if completed_date.value is not None
                else None
            )
        return await self._request(
            method="PATCH",
            path=f"/me/todo/lists/{list_id}/tasks/{task_id}",
            json=body,
        )

    async def delete_by_id(self, list_id: str, task_id: str) -> None:
        await self._request(
            method="DELETE",
            path=f"/me/todo/lists/{list_id}/tasks/{task_id}",
        )

    async def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json: dict | None = None,
    ) -> dict | None:
        headers = await self._auth_headers()
        url = f"{self._GRAPH_BASE_URL}{path}"
        self._logger.debug("%s %s params=%s body=%s", method, path, params, json)
        response = await self._client.request(
            method=method, url=url, headers=headers, params=params, json=json
        )
        self._logger.debug(
            "%s %s status=%s response=%s",
            method,
            path,
            response.status_code,
            response.text,
        )
        response.raise_for_status()
        if response.status_code == 204:
            return None
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
