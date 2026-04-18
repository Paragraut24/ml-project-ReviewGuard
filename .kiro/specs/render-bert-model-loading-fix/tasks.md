# Implementation Plan

- [ ] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Private Model Authentication Failure
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the private model authentication bug exists
  - **Scoped PBT Approach**: Scope the property to the concrete failing case - private model (ParagR24/reviewguard-bert) with valid HF_TOKEN
  - Test that `infer_with_hf_api("test review")` successfully authenticates and returns valid predictions when HF_MODEL_ID points to a private model and HF_TOKEN is configured
  - The test assertions should verify: (1) no authentication exception is raised, (2) result contains valid label, (3) result contains score between 0.0 and 1.0
  - Run test on UNFIXED code with environment variables: `HF_MODEL_ID=ParagR24/reviewguard-bert`, `HF_TOKEN=<valid_token>`, `MODEL_BACKEND=hf_api`
  - **EXPECTED OUTCOME**: Test FAILS with authentication error (401/403) - this is correct and proves the bug exists
  - Document counterexamples found: exact error message, HTTP status code, and API response details
  - Examine failures to understand root cause: token format issue, missing permissions, or API parameter problem
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.3, 1.4_

- [~] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Non-Private Model Behavior
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs (local models, pipeline mode, public models)
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Property-based testing generates many test cases for stronger guarantees
  - **Test Case 2.1**: Local model loading - observe that `MODEL_BACKEND=local` loads from `./bert_model/` and returns valid predictions on unfixed code
  - **Test Case 2.2**: Pipeline mode - observe that `MODEL_BACKEND=pipeline` downloads and uses HuggingFace models correctly on unfixed code
  - **Test Case 2.3**: Public model via hf_api - observe that `infer_with_hf_api()` works for public models (e.g., distilbert-base-uncased) without token on unfixed code
  - **Test Case 2.4**: Fallback mechanism - observe that when model loading fails, bert_score=0.50 is returned on unfixed code
  - Write property-based tests asserting: for all non-private model scenarios, the system returns valid predictions with label and score
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 3. Fix private model authentication in infer_with_hf_api()

  - [~] 3.1 Implement the authentication fix
    - Verify token presence and format before making API request
    - Add validation: check that `token` is not empty after stripping whitespace
    - Add debug logging: log token presence (but not value) for troubleshooting
    - Improve error messages to distinguish authentication failure scenarios:
      - 401: Invalid or expired token
      - 403: Token lacks permissions for private model
      - 404: Model not found or token lacks read access
    - Verify Authorization header format: `Bearer {token}` is correctly constructed
    - Consider adding retry logic with exponential backoff for transient auth failures (retry once after 2 seconds if 401/403)
    - Verify API endpoint URL is correct: `https://api-inference.huggingface.co/models/{model_id}`
    - _Bug_Condition: isBugCondition(input) where input.model_backend == "hf_api" AND modelRepositoryIsPrivate(input.hf_model_id) AND input.hf_token IS_SET_
    - _Expected_Behavior: For all inputs satisfying bug condition, infer_with_hf_api() SHALL successfully authenticate and return valid predictions (label, score) without raising authentication errors_
    - _Preservation: Local model loading (MODEL_BACKEND=local), pipeline mode (MODEL_BACKEND=pipeline), public model access (hf_api with public models), and fallback mechanism must remain unchanged_
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_

  - [~] 3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Private Model Authentication Success
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1 with private model and valid token
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed and private model authentication works)
    - _Requirements: 2.1, 2.2_

  - [~] 3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Non-Private Model Behavior Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2 (local models, pipeline mode, public models, fallback)
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions in existing functionality)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [~] 4. Checkpoint - Ensure all tests pass
  - Run complete test suite including bug condition and preservation tests
  - Verify all tests pass: bug condition test (private model auth), preservation tests (local, pipeline, public, fallback)
  - Test on Render deployment with actual private model credentials
  - Verify `/health` endpoint reports correct configuration
  - Verify `/predict` endpoint returns real BERT scores (not fallback 0.50) for private model
  - If any tests fail or questions arise, ask the user for guidance
