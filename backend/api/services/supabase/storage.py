from .client import supabase

def upload_file(bucket: str, path: str, file_data, content_type: str = "application/octet-stream"):
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
        raise Exception(f"Error uploading file: {e}")
    return response

def get_file_url(bucket: str, path: str, is_public: bool = False):
    storage = supabase.storage.from_(bucket)
    return storage.get_public_url(path) if is_public else storage.create_signed_url(path, 60 * 60).get("signedURL")  # 1 giờ

def delete_file(bucket: str, path: str):
    return supabase.storage.from_(bucket).remove([path])

