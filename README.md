# kaggle-s3-data-pipeline
End-to-end Python data pipeline ingesting Kaggle datasets and loading to Amazon S3 for vector database ingestion

Kaggle to S3 Data Pipeline
An end-to-end Python data pipeline that ingests datasets from Kaggle, applies transformation logic, and loads them into Amazon S3 to enable scalable vector database ingestion for enterprise RAG (Retrieval-Augmented Generation) systems.
Technologies Used

Python
Kaggle API
boto3 (AWS SDK for Python)
Amazon S3
Pandas

What It Does

Authenticates and pulls datasets from Kaggle using the Kaggle API
Transforms and cleans the data using Pandas
Loads the processed data into a designated Amazon S3 bucket
Prepares data for downstream vector database ingestion in a RAG architecture

How to Run

Install dependencies: pip install kaggle boto3 pandas
Set up Kaggle API credentials in ~/.kaggle/kaggle.json
Configure AWS credentials via environment variables or ~/.aws/credentials
Run: python pipeline.py
