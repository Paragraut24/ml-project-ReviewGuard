"""
Bug Condition Exploration Test for Private Model Authentication

**Validates: Requirements 1.1, 1.3, 1.4**

This test is designed to FAIL on unfixed code to confirm the bug exists.
The bug occurs when MODEL_BACKEND=hf_api and the HuggingFace model is private.

CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

Expected behavior on UNFIXED code:
- Test will FAIL with authentication error (401/403)
- This proves the bug exists and the test correctly detects it

Expected behavior on FIXED code:
- Test will PASS with successful authentication
- This proves the fix works correctly
"""

import os
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app import infer_with_hf_api


# Property 1: Bug Condition - Private Model Authentication Failure
@pytest.mark.skipif(
    not os.environ.get("HF_TOKEN") or not os.environ.get("HF_MODEL_ID"),
    reason="HF_TOKEN and HF_MODEL_ID must be set to run this test"
)
@given(review_text=st.text(min_size=5, max_size=200))
@settings(
    max_examples=10,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=120000  # 120 seconds for API calls
)
def test_private_model_authentication(review_text):
    """
    **Validates: Requirements 1.1, 1.3, 1.4**
    
    Property 1: Bug Condition - Private Model Authentication Failure
    
    For any review text, when HF_MODEL_ID points to a private model (ParagR24/reviewguard-bert)
    and HF_TOKEN is configured, the infer_with_hf_api function should successfully authenticate
    and return valid predictions.
    
    CRITICAL: This test is EXPECTED TO FAIL on unfixed code with authentication errors.
    Failure confirms the bug exists. Success after fix confirms the bug is resolved.
    
    Test assertions verify:
    1. No authentication exception is raised (401/403 errors)
    2. Result contains valid label
    3. Result contains score between 0.0 and 1.0
    """
    # Ensure we're testing the private model scenario
    model_id = os.environ.get("HF_MODEL_ID")
    token = os.environ.get("HF_TOKEN")
    
    assert model_id, "HF_MODEL_ID must be set"
    assert token, "HF_TOKEN must be set"
    assert "ParagR24/reviewguard-bert" in model_id, f"Expected private model, got {model_id}"
    
    # Set MODEL_BACKEND to hf_api to trigger the bug condition
    original_backend = os.environ.get("MODEL_BACKEND")
    os.environ["MODEL_BACKEND"] = "hf_api"
    
    try:
        # This should fail on unfixed code with authentication error
        label, score = infer_with_hf_api(review_text)
        
        # If we get here, authentication succeeded (expected on FIXED code)
        # Verify the result is valid
        assert label is not None, "Label should not be None"
        assert isinstance(label, str), f"Label should be string, got {type(label)}"
        assert len(label) > 0, "Label should not be empty"
        
        assert score is not None, "Score should not be None"
        assert isinstance(score, float), f"Score should be float, got {type(score)}"
        assert 0.0 <= score <= 1.0, f"Score should be between 0.0 and 1.0, got {score}"
        
    except RuntimeError as e:
        error_msg = str(e)
        
        # On unfixed code, we expect authentication failures
        # Document the counterexample for analysis
        if "auth failed" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
            pytest.fail(
                f"COUNTEREXAMPLE FOUND - Authentication failed for private model:\n"
                f"  Model: {model_id}\n"
                f"  Token configured: {bool(token)}\n"
                f"  Review text: {review_text[:50]}...\n"
                f"  Error: {error_msg}\n"
                f"\nThis failure confirms the bug exists. The test will pass after the fix is implemented."
            )
        else:
            # Unexpected error - re-raise for investigation
            raise
    
    finally:
        # Restore original backend setting
        if original_backend is not None:
            os.environ["MODEL_BACKEND"] = original_backend
        elif "MODEL_BACKEND" in os.environ:
            del os.environ["MODEL_BACKEND"]


# Unit test version for simpler debugging
@pytest.mark.skipif(
    not os.environ.get("HF_TOKEN") or not os.environ.get("HF_MODEL_ID"),
    reason="HF_TOKEN and HF_MODEL_ID must be set to run this test"
)
def test_private_model_authentication_unit():
    """
    **Validates: Requirements 1.1, 1.3, 1.4**
    
    Unit test version of the bug condition test.
    Tests a single concrete example to verify private model authentication.
    
    CRITICAL: This test is EXPECTED TO FAIL on unfixed code.
    """
    model_id = os.environ.get("HF_MODEL_ID")
    token = os.environ.get("HF_TOKEN")
    
    assert model_id, "HF_MODEL_ID must be set"
    assert token, "HF_TOKEN must be set"
    
    # Set MODEL_BACKEND to hf_api
    original_backend = os.environ.get("MODEL_BACKEND")
    os.environ["MODEL_BACKEND"] = "hf_api"
    
    try:
        # Test with a simple review text
        test_review = "This product is amazing! Best purchase ever!"
        
        # This should fail on unfixed code with authentication error
        label, score = infer_with_hf_api(test_review)
        
        # If we get here, authentication succeeded
        assert label is not None
        assert isinstance(label, str)
        assert len(label) > 0
        
        assert score is not None
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        
        print(f"✓ Authentication successful - label: {label}, score: {score}")
        
    except RuntimeError as e:
        error_msg = str(e)
        
        # On unfixed code, we expect authentication failures
        if "auth failed" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
            pytest.fail(
                f"COUNTEREXAMPLE FOUND - Authentication failed:\n"
                f"  Model: {model_id}\n"
                f"  Token configured: {bool(token)}\n"
                f"  Error: {error_msg}\n"
                f"\nThis failure confirms the bug exists."
            )
        else:
            raise
    
    finally:
        if original_backend is not None:
            os.environ["MODEL_BACKEND"] = original_backend
        elif "MODEL_BACKEND" in os.environ:
            del os.environ["MODEL_BACKEND"]
