from .client import supabase

def upload_file(bucket: str, path: str, file_data, content_type: str = "application/octet-stream") -> dict:
    try:
        file_bytes = file_data.read()
        storage = supabase.storage.from_(bucket)
        response = storage.upload(
            path=path,
            file=file_bytes,
            file_options={
                "content-type": content_type,
                "cache-control": "3600",
                "upsert": "true"
            }
        )
    except Exception as e:
        raise e
    return response

def get_file_url(bucket: str, path: str, is_public: bool = False):
    storage = supabase.storage.from_(bucket)

    if is_public:
        return storage.get_public_url(path)

    return storage.create_signed_url(path, 60 * 60 * 4).get("signedURL")  # 4 giờ

def delete_file(bucket: str, path: str):
    return supabase.storage.from_(bucket).remove([path])

