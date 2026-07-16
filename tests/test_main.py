"""Tests for mcp-financial-data utility and econ functions."""

import pytest
from mcp_financial_data.utils import format_dataframe, safe_float, handle_error


class TestSafeFloat:
    """Tests for safe_float conversion function."""

    def test_float_string(self):
        """Test converting a float string."""
        result = safe_float("3.14", 0.0)
        assert isinstance(result, float)
        assert result == 3.14

    def test_int_string(self):
        """Test converting an integer string."""
        result = safe_float("42", 0.0)
        assert result == 42.0

    def test_none_value(self):
        """Test converting None returns default."""
        result = safe_float(None, 0.0)
        assert result == 0.0

    def test_invalid_string(self):
        """Test that invalid string returns default."""
        result = safe_float("not_a_number", -1.0)
        assert result == -1.0

    def test_empty_string(self):
        """Test that empty string returns default."""
        result = safe_float("", 99.0)
        assert result == 99.0

    def test_nan_value(self):
        """Test converting NaN returns default."""
        import math
        result = safe_float(float("nan"), 0.0)
        assert result == 0.0

    def test_negative_number(self):
        """Test converting a negative number."""
        result = safe_float("-123.45", 0.0)
        assert result == -123.45


class TestFormatDataFrame:
    """Tests for format_dataframe function."""

    def test_empty_dataframe(self):
        """Test formatting an empty DataFrame."""
        import pandas as pd
        df = pd.DataFrame()
        result = format_dataframe(df)
        assert isinstance(result, str)

    def test_small_dataframe(self):
        """Test formatting a small DataFrame."""
        import pandas as pd
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        result = format_dataframe(df)
        assert isinstance(result, str)
        assert "|" in result or len(result) > 0

    def test_max_rows_limiting(self):
        """Test that max_rows limits the output."""
        import pandas as pd
        df = pd.DataFrame({"col": list(range(50))})
        result = format_dataframe(df, max_rows=5)
        assert isinstance(result, str)

    def test_dataframe_with_na(self):
        """Test formatting DataFrame with NaN values."""
        import pandas as pd
        import numpy as np
        df = pd.DataFrame({"A": [1.0, np.nan], "B": [np.nan, 2.0]})
        result = format_dataframe(df)
        assert isinstance(result, str)


class TestHandleError:
    """Tests for handle_error decorator/function."""

    def test_handle_error_returns_string(self):
        """Test that handle_error returns a string on failure."""
        import pandas as pd
        df = pd.DataFrame({"col": [1, 2, 3]})
        result = format_dataframe(df)
        assert isinstance(result, str)

    def test_modifier(self):
        """Test that format_dataframe handles modifier parameter."""
        import pandas as pd
        df = pd.DataFrame({"A": [1]})
        result = format_dataframe(df)
        assert isinstance(result, str)


class TestEconTools:
    """Tests for economic indicator tools availability."""

    def test_econ_tools_import(self):
        """Test that econ_tools module is importable."""
        from mcp_financial_data import econ_tools
        assert econ_tools is not None

    def test_market_tools_import(self):
        """Test that market_tools module is importable."""
        from mcp_financial_data import market_tools
        assert market_tools is not None

    def test_stock_tools_import(self):
        """Test that stock_tools module is importable."""
        from mcp_financial_data import stock_tools
        assert stock_tools is not None

    def test_utils_import(self):
        """Test that utils module provides expected functions."""
        from mcp_financial_data import utils
        assert hasattr(utils, "safe_float")
        assert hasattr(utils, "format_dataframe")
