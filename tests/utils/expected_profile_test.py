import pandas as pd
import numpy as np
import pytest
from src.utils import expected_profile as ep



df_1 = pd.DataFrame({
    'A': [5, 6, 7, 8],
    'B': ['a', 'b', 'c', 'd']
})
df_2 = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': ['a', 'a', 'c', 'd']
})

class TestExpectedProfiler:
    @pytest.fixture
    def profiler(self):
        return ep.ExpectedProfiler(df_1, df_2)

    def test_try_numeric_conversion(self, profiler):
        test_series = pd.Series(['1', '2', '3', '4'])
        result = profiler._ExpectedProfiler__try_numeric_conversion(test_series)
        assert result.dtype == np.int64

    def test_convert_to_numeric(self, profiler):
        profiler._ExpectedProfiler__convert_to_numeric()
        assert profiler.df_1['A'].dtype == np.int64
        assert profiler.df_1['B'].dtype == object

    def test_numeric_comparisons(self, profiler):
        profiler._ExpectedProfiler__numeric_comparisons()
        assert profiler.percent_differences is not None
        assert profiler.absolute_differences is not None

    def test_categorical_comparisons(self, profiler):
        profiler._ExpectedProfiler__categorical_comparisons()
        assert profiler.avg_frequency_ratio is not None
        assert profiler.frequency_differences is not None

    def test_get_dataframe_shapes(self, profiler):
        result = profiler._ExpectedProfiler__get_dataframe_shapes()
        assert isinstance(result, pd.DataFrame)

    def test_compare(self, profiler):
        profiler.compare()
        assert profiler.percent_differences is not None
        assert profiler.absolute_differences is not None
        assert profiler.avg_frequency_ratio is not None
        assert profiler.frequency_differences is not None

if __name__ == "__main__":
    pytest.main()