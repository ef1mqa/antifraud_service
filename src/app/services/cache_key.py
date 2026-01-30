import hashlib
import json
from app.schemas import UserCheck


def make_user_check_key(user: UserCheck) -> str:
    payload = json.dumps(
        user.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"antifraud:{digest}"