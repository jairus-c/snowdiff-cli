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

df_3 = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4.0, 5.5, 6.1],
    'C': [pd.Timestamp('20230101'), pd.Timestamp('20230102'), pd.Timestamp('20230103')],
    'D': ['foo', 'bar', 'baz']
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

        # test percent_differences
        assert np.allclose(profiler.percent_differences, ((df_1.describe() - df_2.describe()) / df_1.describe()) * 100)
        
        # test absolute_differences
        assert np.allclose(profiler.absolute_differences, (df_1.describe() - df_2.describe()).abs())

        # test avg_frequency_ratio
        assert profiler.avg_frequency_ratio == {'B': 0.8333333333333334}

        # test frequency_differences
        assert (profiler.frequency_differences['B']['absolute_difference'] == pd.Series([1, 0, 0], index=['a', 'c', 'd'])).all()

    def test_drop_time_cols(self, profiler):
        all_columns = df_3.columns
        time_dropped_columns = profiler._ExpectedProfiler__drop_timestamps(df_3).columns
        assert len(all_columns) != len(time_dropped_columns)
        assert set(time_dropped_columns) == set(['A', 'B', 'D'])
if __name__ == "__main__":
    pytest.main()
