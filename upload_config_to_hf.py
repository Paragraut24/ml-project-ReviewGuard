import os
from huggingface_hub import HfApi

REPO_ID = "ParagR24/reviewguard-bert"
TOKEN = os.environ.get("HF_TOKEN")

if not TOKEN:
    print("ERROR: Set HF_TOKEN first. Run: $env:HF_TOKEN = 'hf_yourtoken'")
    raise SystemExit(1)

api = HfApi()

# Upload all non-weight files (config + tokenizer)
files_to_upload = [
    "bert_model/config.json",
    "bert_model/tokenizer_config.json",
    "bert_model/tokenizer.json",
]

for local_path in files_to_upload:
    filename = local_path.split("/")[-1]
    print(f"Uploading {filename} ...")
    api.upload_file(
        path_or_fileobj=local_path,
        path_in_repo=filename,
        repo_id=REPO_ID,
        repo_type="model",
        token=TOKEN,
        commit_message=f"Upload {filename} for HF Inference API compatibility",
    )
    print(f"  Done: https://huggingface.co/{REPO_ID}/blob/main/{filename}")

print("\nAll files uploaded successfully!")
print(f"Inference API: https://api-inference.huggingface.co/models/{REPO_ID}")
