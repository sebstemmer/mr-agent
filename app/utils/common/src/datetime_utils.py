from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

_BERLIN = ZoneInfo("Europe/Berlin")


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def today_berlin() -> date:
    return datetime.now(tz=_BERLIN).date()
