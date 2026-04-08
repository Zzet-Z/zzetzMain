from pathlib import Path

from werkzeug.utils import secure_filename


ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}


def save_upload(
    upload_dir: str,
    token: str,
    file_storage,
    *,
    max_upload_size_mb: int,
) -> tuple[str, str]:
    if file_storage.mimetype not in ALLOWED_MIME_TYPES:
        raise ValueError("只支持 PNG、JPEG、WEBP 图片")

    filename = secure_filename(file_storage.filename or "")
    if not filename:
        raise ValueError("文件名无效")

    file_storage.stream.seek(0, 2)
    size_bytes = file_storage.stream.tell()
    file_storage.stream.seek(0)

    if size_bytes > max_upload_size_mb * 1024 * 1024:
        raise ValueError(f"单张图片不能超过 {max_upload_size_mb}MB")

    token_dir = Path(upload_dir) / token
    token_dir.mkdir(parents=True, exist_ok=True)
    path = token_dir / filename
    file_storage.save(path)
    return filename, str(path)
