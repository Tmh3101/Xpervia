import modal
import os

app = modal.App("xpervia-chatbot-service")

hf_cache_vol = modal.Volume.from_name("hf-model-cache", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("gcc", "g++", "libpq-dev", "libpq5", "libgomp1", "curl", "git")
    .pip_install_from_requirements("requirements.txt")
    .env({
        "HF_HOME": "/app/.cache/huggingface",
        "TRANSFORMERS_CACHE": "/app/.cache/huggingface",
        "TOKENIZERS_PARALLELISM": "false",
        "PYTHONPATH": "/app",
    })
    .add_local_dir(
        local_path=".",
        remote_path="/app",
        ignore=["venv", ".venv", "__pycache__", ".git", ".env"]
    )
)

@app.function(
    image=image,
    gpu="T4",
    timeout=120,          
    max_containers=5,
    volumes={"/app/.cache/huggingface": hf_cache_vol},
    secrets=[modal.Secret.from_dotenv(".env")]
)
@modal.asgi_app()
def serve():
    import sys
    if "/app" not in sys.path:
        sys.path.insert(0, "/app")

    os.environ["LLM_MODEL"] = "Qwen/Qwen2.5-1.5B-Instruct"
    os.environ["LORA_PATH"] = "/app/app/core/model/qwen2_5-1_5B-instruct-lora"
    
    current_db_port = os.environ.get("SUPABASE_DB_PORT", "5432")
    if current_db_port == "5432":
        os.environ["SUPABASE_DB_PORT"] = "6543"

    db_host = os.environ.get("SUPABASE_DB_HOST", "")
    if "supabase.co" in db_host:
        try:
            project_id = db_host.split(".")[1]
            db_user = os.environ.get("SUPABASE_DB_USER", "postgres")
            if "." not in db_user:
                os.environ["SUPABASE_DB_USER"] = f"{db_user}.{project_id}"
        except IndexError:
            pass

    from app.api.main import app as fastapi_app
    return fastapi_app