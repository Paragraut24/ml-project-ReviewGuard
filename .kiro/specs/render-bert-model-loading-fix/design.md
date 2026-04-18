# Render BERT Model Loading Bugfix Design

## Overview

The ReviewGuard application fails to load the BERT model when deployed to Render because the HuggingFace model repository (`ParagR24/reviewguard-bert`) is **PRIVATE**. While the environment variables `HF_MODEL_ID` and `HF_TOKEN` are correctly configured in Render's dashboard, the `infer_with_hf_api()` function does not properly authenticate with the private repository when making API requests. This causes the model loading to fail with authentication errors, triggering the fallback scoring mechanism (bert_score=0.50) instead of using the fine-tuned BERT model.

The fix requires ensuring that the HuggingFace API token is properly included in the Authorization header when making requests to the private model repository. The solution must work for both public and private models without breaking existing functionality.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when the HuggingFace model is PRIVATE and the API request does not include proper authentication
- **Property (P)**: The desired behavior when the bug condition holds - the API request should successfully authenticate and load the private model
- **Preservation**: Existing functionality that must remain unchanged - local model loading, pipeline mode, fallback mechanism, and public model access
- **infer_with_hf_api()**: The function in `app.py` that makes HTTP requests to the HuggingFace Inference API to get predictions from the remote model
- **HF_TOKEN**: Environment variable containing the HuggingFace access token with read permissions for the private model repository
- **HF_MODEL_ID**: Environment variable containing the model repository identifier in "owner/repo" format (e.g., "ParagR24/reviewguard-bert")
- **MODEL_BACKEND**: Environment variable that determines which model loading strategy to use (local, pipeline, or hf_api)

## Bug Details

### Bug Condition

The bug manifests when the application is deployed to Render with `MODEL_BACKEND=hf_api` and the HuggingFace model repository is PRIVATE. The `infer_with_hf_api()` function constructs the Authorization header correctly, but the HuggingFace Inference API may require additional authentication parameters or the token may not have the correct permissions.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type APIRequest
  OUTPUT: boolean
  
  RETURN input.model_backend == "hf_api"
         AND input.hf_model_id IS_SET
         AND input.hf_token IS_SET
         AND modelRepositoryIsPrivate(input.hf_model_id)
         AND NOT apiRequestSucceeds(input)
END FUNCTION
```

### Examples

- **Example 1**: Deploy to Render with `HF_MODEL_ID=ParagR24/reviewguard-bert` (PRIVATE) and valid `HF_TOKEN`
  - **Expected**: Model loads successfully, returns real predictions
  - **Actual**: API returns 401/403 error, falls back to bert_score=0.50

- **Example 2**: Make prediction request to `/predict` endpoint on Render
  - **Expected**: BERT model analyzes review text, returns confidence score based on model output
  - **Actual**: Error "Hugging Face auth failed for private model access", returns fallback score

- **Example 3**: Check `/health` endpoint on Render
  - **Expected**: Shows `model_backend: "hf_api"`, `hf_model_id_configured: true`, `hf_token_configured: true`
  - **Actual**: Shows correct configuration but model still fails to load during prediction

- **Edge Case**: Public model (e.g., `distilbert-base-uncased`)
  - **Expected**: Loads successfully without token, returns real predictions
  - **Actual**: Works correctly (no bug for public models)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Local model loading (`MODEL_BACKEND=local`) must continue to work with `./bert_model/` directory
- Pipeline mode (`MODEL_BACKEND=pipeline`) must continue to download and use HuggingFace models via transformers
- Fallback mechanism must continue to provide bert_score=0.50 when model loading fails
- Public model access via `hf_api` backend must continue to work without requiring a token
- The `/health` endpoint must continue to report configuration status accurately
- The fused scoring algorithm (BERT + GNN + heuristic) must continue to work as before

**Scope:**
All inputs that do NOT involve private HuggingFace models accessed via the `hf_api` backend should be completely unaffected by this fix. This includes:
- Local model inference with `MODEL_BACKEND=local`
- Remote model inference with `MODEL_BACKEND=pipeline`
- Public model inference with `MODEL_BACKEND=hf_api` (no token required)
- Fallback scoring when any backend fails
- All heuristic and GNN scoring logic

## Hypothesized Root Cause

Based on the bug description and status report, the most likely issues are:

1. **Token Format or Permissions**: The HuggingFace token may not have the correct permissions (read access) for the private repository, or the token format in the Authorization header may be incorrect

2. **API Request Parameters**: The HuggingFace Inference API may require additional parameters or headers for private model access beyond just the Authorization header

3. **Token Validation Timing**: The token may be valid but not yet propagated to the Inference API servers, causing intermittent authentication failures

4. **Model Repository Configuration**: The private model repository may have additional access restrictions (organization-level permissions, IP restrictions) that prevent API access even with a valid token

## Correctness Properties

Property 1: Bug Condition - Private Model Authentication

_For any_ API request where the model backend is "hf_api", the model repository is PRIVATE, and a valid HF_TOKEN is configured, the fixed infer_with_hf_api function SHALL successfully authenticate with the HuggingFace Inference API and load the private model, returning real predictions instead of fallback scores.

**Validates: Requirements 2.1, 2.2**

Property 2: Preservation - Non-Private Model Behavior

_For any_ model loading scenario that does NOT involve a private HuggingFace model accessed via the hf_api backend (local models, pipeline mode, public models), the fixed code SHALL produce exactly the same behavior as the original code, preserving all existing functionality for non-private model access.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct (token permissions or API request format):

**File**: `app.py`

**Function**: `infer_with_hf_api(text)`

**Specific Changes**:

1. **Verify Token Presence**: Ensure that when `HF_TOKEN` is set, it is properly included in the Authorization header
   - Current code already does this: `headers["Authorization"] = f"Bearer {token}"`
   - Verify the token value is not empty or malformed

2. **Add Token Validation**: Before making the API request, validate that the token is properly formatted
   - Check that token is not empty after stripping whitespace
   - Log token presence (but not value) for debugging

3. **Improve Error Messages**: Enhance error handling to distinguish between different authentication failure scenarios
   - 401: Invalid or expired token
   - 403: Token lacks permissions for private model
   - 404: Model not found or token lacks read access

4. **Add Retry Logic**: Implement exponential backoff for transient authentication failures
   - Retry once after 2 seconds if 401/403 received
   - This handles token propagation delays

5. **Verify API Endpoint**: Ensure the API endpoint URL is correctly constructed
   - Current: `https://api-inference.huggingface.co/models/{model_id}`
   - Verify this is the correct endpoint for private models

### Alternative Hypothesis

If the above changes don't resolve the issue, the problem may be:
- **Token Scope**: The token may need specific scopes (e.g., `repo:read`) that are not currently granted
- **Organization Permissions**: The private model may be in an organization that requires additional authentication
- **API Limitations**: The Inference API may not support private models in the same way as the transformers library

In this case, the fix would be to:
- Switch from `hf_api` backend to `pipeline` backend for private models
- Update `get_model_backend()` to detect private models and use `pipeline` instead of `hf_api`
- Ensure `pipeline` mode properly uses the token for authentication

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that simulate API requests to the private HuggingFace model with valid credentials. Run these tests on the UNFIXED code to observe authentication failures and understand the root cause.

**Test Cases**:
1. **Private Model API Request**: Call `infer_with_hf_api("test review")` with `HF_MODEL_ID=ParagR24/reviewguard-bert` and valid `HF_TOKEN` (will fail on unfixed code)
2. **Token Header Inspection**: Verify that the Authorization header is correctly formatted as `Bearer <token>` (may pass on unfixed code)
3. **API Response Analysis**: Capture the exact error response from HuggingFace API (401, 403, or 404) to identify the authentication issue
4. **Public Model Comparison**: Call `infer_with_hf_api("test review")` with a public model to verify the API request logic works for non-private models (should pass on unfixed code)

**Expected Counterexamples**:
- API returns 401 Unauthorized or 403 Forbidden when accessing private model
- Possible causes: token format incorrect, token lacks permissions, API endpoint requires additional parameters

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := infer_with_hf_api_fixed(input.text)
  ASSERT result.label IS_VALID_LABEL
  ASSERT result.score BETWEEN 0.0 AND 1.0
  ASSERT NO_EXCEPTION_RAISED
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT infer_with_hf_api_original(input) = infer_with_hf_api_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for local models, pipeline mode, and public models, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Local Model Preservation**: Observe that `MODEL_BACKEND=local` loads from `./bert_model/` correctly on unfixed code, then verify this continues after fix
2. **Pipeline Mode Preservation**: Observe that `MODEL_BACKEND=pipeline` downloads and uses HuggingFace models correctly on unfixed code, then verify this continues after fix
3. **Public Model Preservation**: Observe that `hf_api` backend works for public models on unfixed code, then verify this continues after fix
4. **Fallback Preservation**: Observe that fallback mechanism (bert_score=0.50) triggers on model load failure, then verify this continues after fix

### Unit Tests

- Test `infer_with_hf_api()` with private model and valid token (should succeed after fix)
- Test `infer_with_hf_api()` with private model and invalid token (should raise authentication error)
- Test `infer_with_hf_api()` with private model and no token (should raise authentication error)
- Test `infer_with_hf_api()` with public model and no token (should succeed)
- Test `get_hf_credentials()` returns correct values from environment variables
- Test error handling for 401, 403, and 404 responses

### Property-Based Tests

- Generate random review texts and verify private model returns valid predictions with valid token
- Generate random model IDs (public and private) and verify authentication logic works correctly
- Generate random token values and verify proper error handling for invalid tokens
- Test that all non-hf_api backends continue to work across many scenarios

### Integration Tests

- Test full prediction flow on Render with private model and valid credentials
- Test `/health` endpoint reports correct configuration status
- Test `/predict` endpoint returns real BERT scores (not fallback) for private model
- Test switching between different MODEL_BACKEND values and verify correct behavior
- Test that fallback mechanism still works when authentication fails
