from flask import current_app


class AdminAuthError(PermissionError):
    pass


def require_admin_token(request) -> None:
    header = request.headers.get("Authorization", "")
    expected = current_app.config.get("ADMIN_TOKEN", "")
    if not expected or header != f"Bearer {expected}":
        raise AdminAuthError("invalid admin token")
