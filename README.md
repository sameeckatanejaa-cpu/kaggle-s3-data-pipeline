# Kaggle to S3 Data Pipeline

End-to-end Python data pipeline ingesting Kaggle datasets and loading to Amazon S3 for vector database ingestion.

## Technologies Used
- Python
- Kaggle API
- boto3 (AWS SDK for Python)
- Amazon S3
- Pandas

## What It Does
1. Authenticates and pulls datasets from Kaggle using the Kaggle API
2. Transforms and cleans the data using Pandas
3. Loads the processed data into a designated Amazon S3 bucket
4. Prepares data for downstream vector database ingestion in a RAG architecture

## How to Run
1. Install dependencies: `pip install kaggle boto3 pandas`
2. Set up Kaggle API credentials in `~/.kaggle/kaggle.json`
3. Configure AWS credentials via environment variables or `~/.aws/credentials`
4. Run: `python pipeline.py`
