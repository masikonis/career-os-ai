from unittest.mock import patch

import pytest

from src.utilities.text import preserve_paragraphs, sanitize_text


class TestSanitizeText:
    """Test suite for sanitize_text functionality"""

    @pytest.mark.parametrize(
        "input_text, expected",
        [
            ("  Hello   world  ", "Hello world"),
            ("\tNew\nLines\t", "New Lines"),
            ("", ""),
            (None, ""),
            (123, "123"),
            ([1, 2], "[1, 2]"),
        ],
    )
    def test_various_inputs(self, input_text, expected):
        assert sanitize_text(input_text) == expected

    def test_logging_on_invalid_type(self, mocker):
        mock_logger = mocker.patch("src.utilities.text.logger")
        sanitize_text(123)
        mock_logger.warning.assert_called_once_with(
            "Non-string input to sanitize_text: <class 'int'>"
        )


class TestPreserveParagraphs:
    """Test suite for preserve_paragraphs functionality"""

    @pytest.mark.parametrize(
        "input_text, expected",
        [
            ("Para1\n\nPara2", "Para1\n\nPara2"),
            ("  Para1 \n\n  Para2  ", "Para1\n\nPara2"),
            ("\n\nEmpty\n\n", "Empty"),
            (123, "123"),
            (None, ""),
        ],
    )
    def test_paragraph_handling(self, input_text, expected):
        assert preserve_paragraphs(input_text) == expected

    def test_paragraph_filtering(self, mocker):
        mock_logger = mocker.patch("src.utilities.text.logger")
        result = preserve_paragraphs("\n\nKeep\n\n\n")
        assert result == "Keep"
        mock_logger.debug.assert_any_call(
            "Processed 3 paragraphs, 1 remaining after filtering"
        )

    @pytest.mark.parametrize(
        "input_text, para_count, filtered_count",
        [("One\n\nTwo\n\nThree", 3, 3), ("\n\n\n", 2, 0), ("Mixed\n\n\nKeep", 2, 2)],
    )
    def test_paragraph_metrics_logging(
        self, mocker, input_text, para_count, filtered_count
    ):
        mock_logger = mocker.patch("src.utilities.text.logger")
        preserve_paragraphs(input_text)
        mock_logger.debug.assert_called_with(
            f"Processed {para_count} paragraphs, {filtered_count} remaining after filtering"
        )
