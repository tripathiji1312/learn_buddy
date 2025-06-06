import pytest
from src.learning_models import extract_number, check_semantic_similarity

# Use @pytest.mark.parametrize to run the same test with different inputs
@pytest.mark.parametrize("input_string, expected_output", [
    ("the answer is 42", "42"),
    ("I think it might be 7.", "7"),
    ("There are no numbers here", None),
    ("The first is 1 and the second is 2", "1"), # Should find the first number
])
def test_extract_number(input_string, expected_output):
    """Tests the number extraction helper function with various inputs."""
    assert extract_number(input_string) == expected_output

def test_check_semantic_similarity_numeric_match():
    """
    Tests that the semantic checker correctly uses the number extractor
    for a perfect numeric match.
    """
    is_correct, score = check_semantic_similarity(
        user_answer="The answer is 50",  # More direct answer
        correct_answer="50"
    )
    assert is_correct is True
    assert score == 1.0

def test_check_semantic_similarity_text_match():
    """
    Tests that the AI model correctly identifies two sentences as similar.
    Note: This is more of an integration test as it uses the real model.
    """
    is_correct, score = check_semantic_similarity(
        user_answer="A vehicle used for traveling.",
        correct_answer="An automobile for transportation."
    )
    assert is_correct is True
    assert score > 0.6 # We check that the score is above our threshold

def test_check_semantic_similarity_text_mismatch():
    """Tests that the AI model correctly identifies two sentences as different."""
    is_correct, score = check_semantic_similarity(
        user_answer="A vehicle used for traveling.",
        correct_answer="The sky is blue."
    )
    assert is_correct is False
    assert score < 0.6 # The score should be below our threshold

def test_check_semantic_similarity_numeric_with_distractors():
    """
    Tests that the semantic checker finds the correct number
    even when there are other numbers in the text.
    """
    is_correct, score = check_semantic_similarity(
        user_answer="I am 100% sure the answer is 50",
        correct_answer="50"
    )
    assert is_correct is True
    assert score == 1.0

def test_check_semantic_similarity_numeric_no_match():
    """
    Tests that when the correct number isn't found, 
    it falls back to semantic matching.
    """
    is_correct, score = check_semantic_similarity(
        user_answer="I think it's around seventy-five",
        correct_answer="50"
    )
    # This should use semantic matching and likely fail
    assert is_correct is False
    assert score < 1.0