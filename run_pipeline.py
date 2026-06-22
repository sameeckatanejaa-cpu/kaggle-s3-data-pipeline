"""
run_pipeline.py

THIS IS THE FILE YOU RUN.

It does exactly 4 things, in order, every time you run it:
  1. Downloads the Netflix dataset from Kaggle
  2. Computes its fingerprint (hash) and compares to last time
  3. If unchanged -> stops here, prints "skipping" (this is the
     idempotent behavior the assignment asks for)
  4. If changed/new -> uploads it to your S3 bucket, then remembers
     the new fingerprint for next time

Run it with:
    python3 run_pipeline.py

Run it a SECOND time right after, and you should see it skip the
upload -- that's your proof the pipeline is idempotent.
"""

import os
import shutil
import zipfile
import subprocess

import boto3

from hash_tracker import has_changed, record_upload

# ---- CONFIG ----
S3_BUCKET = "rohittaneja-netflix-pipeline-2026"

KAGGLE_DATASET = "shivamb/netflix-shows"
LOCAL_FOLDER = "netflix_data"
DATA_FILENAME = "netflix_titles.csv"
DATASET_NAME = "netflix_titles"  # just a label we use internally


def find_kaggle_executable() -> str:
    """Finds the kaggle command-line tool even if it's not on PATH --
    some setups (like Mac with user-level pip installs) put it somewhere
    PATH doesn't automatically check."""
    found = shutil.which("kaggle")
    if found:
        return found

    home = os.path.expanduser("~")
    fallback_paths = [
        os.path.join(home, "Library/Python/3.9/bin/kaggle"),
        os.path.join(home, "Library/Python/3.10/bin/kaggle"),
        os.path.join(home, "Library/Python/3.11/bin/kaggle"),
        os.path.join(home, "Library/Python/3.12/bin/kaggle"),
        "/usr/local/bin/kaggle",
    ]
    for path in fallback_paths:
        if os.path.exists(path):
            return path

    raise FileNotFoundError(
        "Could not find the 'kaggle' executable. Try running "
        "'pip3 show -f kaggle' to locate it manually."
    )


def download_from_kaggle():
    """Downloads the Netflix dataset zip from Kaggle and unzips it."""
    os.makedirs(LOCAL_FOLDER, exist_ok=True)
    kaggle_cmd = find_kaggle_executable()

    print(f"Downloading '{KAGGLE_DATASET}' from Kaggle...")
    subprocess.run(
        [kaggle_cmd, "datasets", "download", "-d", KAGGLE_DATASET, "-p", LOCAL_FOLDER],
        check=True,
    )

    for filename in os.listdir(LOCAL_FOLDER):
        if filename.endswith(".zip"):
            zip_path = os.path.join(LOCAL_FOLDER, filename)
            print(f"Unzipping {filename}...")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(LOCAL_FOLDER)
            os.remove(zip_path)


def upload_to_s3(filepath: str) -> str:
    """Uploads the file to S3."""
    s3 = boto3.client("s3")
    s3_key = f"raw/{DATASET_NAME}/{DATA_FILENAME}"

    print(f"Uploading to s3://{S3_BUCKET}/{s3_key} ...")
    s3.upload_file(filepath, S3_BUCKET, s3_key)
    print("Upload complete.")

    return s3_key


def main():
    download_from_kaggle()

    filepath = os.path.join(LOCAL_FOLDER, DATA_FILENAME)
    if not os.path.exists(filepath):
        print(f"ERROR: expected file not found at {filepath}")
        print(f"Files actually present: {os.listdir(LOCAL_FOLDER)}")
        return

    changed, current_hash = has_changed(DATASET_NAME, filepath)

    if not changed:
        print(f"No change detected (hash: {current_hash[:10]}...).")
        print("Skipping upload -- pipeline is idempotent, nothing to do.")
        return

    print(f"New or changed data detected (hash: {current_hash[:10]}...).")

    s3_key = upload_to_s3(filepath)

    record_upload(DATASET_NAME, current_hash, s3_key)
    print("Pipeline run complete. Fingerprint saved for next run.")


if __name__ == "__main__":
    main()
