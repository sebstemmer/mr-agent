from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


class HealthController:
    def __init__(self, engine: AsyncEngine, router: APIRouter):
        self._engine = engine
        self.router = router
        self.router.add_api_route(path="/health", endpoint=self.health, methods=["GET"])

    async def health(self):
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return {"status": "ok"}
        except Exception as e:
            raise HTTPException(status_code=503, detail=str(e))
