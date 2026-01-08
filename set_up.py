from huggingface_hub import snapshot_download
import os

if not os.path.exists("./model/Qwen3-4B-Instruct-2507"):
    model_id = "Qwen/Qwen3-4B-Instruct-2507"      # your preferred model
    local_dir = "./model/Qwen3-4B-Instruct-2507"  # save model directory or your preferred path 
    snapshot_download(repo_id=model_id, local_dir=local_dir, local_dir_use_symlinks=False)
