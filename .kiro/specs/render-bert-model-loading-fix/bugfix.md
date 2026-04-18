# Bugfix Requirements Document

## Introduction

The ReviewGuard application fails to load the BERT model when deployed to Render, displaying the error message "BERT temporarily unavailable. Using fallback scoring. Details: Hugging Face model not found. Check HF_MODEL_ID." This causes the app to use a hardcoded fallback score of 0.50 instead of the fine-tuned BERT model predictions, defeating the purpose of the ML-powered review analysis. The app works correctly locally using the ./bert_model/ directory, but the deployed version on Render cannot access the HuggingFace model via the hf_api backend.

The root cause is that the HF_MODEL_ID and HF_TOKEN environment variables are marked as `sync: false` in render.yaml, requiring manual configuration in Render's dashboard. These variables are either not set, set incorrectly, or the model configuration is invalid (wrong format, private model without proper authentication, or non-existent model).

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the app is deployed to Render with MODEL_BACKEND=hf_api AND HF_MODEL_ID is not set in the environment THEN the system raises "Hugging Face model not found. Check HF_MODEL_ID." and falls back to bert_score=50%

1.2 WHEN the app is deployed to Render with MODEL_BACKEND=hf_api AND HF_MODEL_ID is set to an invalid format (not "owner/repo") THEN the system raises "Hugging Face model not found or inaccessible" and falls back to bert_score=50%

1.3 WHEN the app is deployed to Render with MODEL_BACKEND=hf_api AND HF_MODEL_ID points to a private model without HF_TOKEN configured THEN the system raises "Hugging Face auth failed for private model access" and falls back to bert_score=50%

1.4 WHEN the app is deployed to Render with MODEL_BACKEND=hf_api AND HF_MODEL_ID points to a non-existent model THEN the system raises "Hugging Face model not found or inaccessible" and falls back to bert_score=50%

1.5 WHEN the app is deployed to Render with missing environment variables THEN the deployment configuration does not provide clear guidance on which HuggingFace model to use or how to configure authentication

### Expected Behavior (Correct)

2.1 WHEN the app is deployed to Render with MODEL_BACKEND=hf_api AND HF_MODEL_ID is properly configured with a valid public model THEN the system SHALL successfully load the BERT model and return real predictions with accurate bert_score values

2.2 WHEN the app is deployed to Render with MODEL_BACKEND=hf_api AND HF_MODEL_ID points to a private model with valid HF_TOKEN THEN the system SHALL successfully authenticate and load the BERT model

2.3 WHEN the app is deployed to Render with MODEL_BACKEND=hf_api THEN the render.yaml configuration SHALL provide clear default values or documentation for HF_MODEL_ID and HF_TOKEN

2.4 WHEN the app deployment fails due to missing or invalid HF_MODEL_ID THEN the system SHALL provide actionable error messages that guide the user to fix the configuration

2.5 WHEN the app is deployed to Render THEN the deployment configuration SHALL ensure all required environment variables are set with valid values before the app starts serving requests

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the app runs locally with MODEL_BACKEND=local AND local model weights exist in ./bert_model/ THEN the system SHALL CONTINUE TO load the model from the local directory and return accurate predictions

3.2 WHEN the app runs with MODEL_BACKEND=pipeline AND HF_MODEL_ID and HF_TOKEN are configured THEN the system SHALL CONTINUE TO download and use the HuggingFace model via the transformers pipeline

3.3 WHEN the BERT model fails to load for any reason THEN the system SHALL CONTINUE TO use the fallback mechanism (bert_score=0.50) to keep the app functional

3.4 WHEN the app receives a review analysis request THEN the system SHALL CONTINUE TO return the fused score combining BERT, GNN simulation, and heuristic boost

3.5 WHEN the /health endpoint is called THEN the system SHALL CONTINUE TO report the current model_backend, local weights status, and environment variable configuration status
