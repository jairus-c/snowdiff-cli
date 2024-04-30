import pandas as pd
import numpy as np

class ExpectedProfiler:
    """
    Class to perform comparisons between two dataframes.

    Attributes:
        df_1 (DataFrame): The first dataframe for comparison.
        df_2 (DataFrame): The second dataframe for comparison.
        df_1_describe (DataFrame): Descriptive statistics of df_1.
        df_2_describe (DataFrame): Descriptive statistics of df_2.
        numeric_cols (list): List of numeric column names in the dataframes.
        categorical_cols (list): List of categorical column names in the dataframes.
        shapes (DataFrame): Counts of rows/columns between dataframes and their percent/absolute differences.
        percent_differences (DataFrame): Percent differences between descriptive statistics of numeric columns.
        absolute_differences (DataFrame): Absolute differences between numeric values in the dataframes.
        avg_frequency_ratio (dict): Average frequency ratio of categorical values between the dataframes.
        frequency_differences (dict): Frequency differences of categorical values between the dataframes.

    Methods:
        compare: Runs computations for comparison
        __numeric_comparions: Initializes class attributes related to numeric comparisons
        __categorical_comparisons: Initializes class attributes related to categorical comparisons
        __get_dataframe_shapes: Initializes shapes class attributes
        __assertions: Checks assertions on the dataframes
    """

    def __init__(self, df_1, df_2):
        """
        Initializes the ExpectedProfiler class with two dataframes.

        Args:
            df_1 (DataFrame): The first dataframe for comparison.
            df_2 (DataFrame): The second dataframe for comparison.
        Returns:
            None
        """
        self.df_1 = df_1
        self.df_2 = df_2
        self.df_1_describe = df_1.describe()
        self.df_2_describe = df_2.describe()
        self.numeric_cols = df_1.select_dtypes(include="number").columns.tolist()
        self.categorical_cols = df_1.select_dtypes(exclude="number").columns.tolist()
        self.shapes = self.__get_dataframe_shapes()
        self.percent_differences = None
        self.absolute_differences = None
        self.avg_frequency_ratio = None
        self.frequency_differences = None

    def __assertions(self):
        """
        Checks assertions on the dataframes.

        Raises exceptions if the assertions fail.

        Args:
            None
        Returns:
            None
        """
        # Assertion 1: Check if both dataframes have len() > 0
        assert len(self.df_1) > 0, "DataFrame 1 has zero length."
        assert len(self.df_2) > 0, "DataFrame 2 has zero length."

        # Assertion 2: Check if both dataframes have the same exact column names
        assert set(self.df_1.columns) == set(
            self.df_2.columns
        ), "Column names are not the same in both dataframes."

        # Assertion 3: Check if both dataframes have the same number of numeric type columns
        assert len(self.df_1.select_dtypes(include=np.number).columns) == len(
            self.df_2.select_dtypes(include=np.number).columns
        ), "Number of numeric type columns are not the same in both dataframes. Please cast approriately"

    def __numeric_comparisons(self):
        """
        Performs numeric comparisons between the two dataframes.

        Calculates percent differences, absolute differences, mean absolute difference,
        and max absolute difference between numeric values in the dataframes.
        Args:
            None
        Returns:
            None
        """
        self.percent_differences = (
            (self.df_1_describe - self.df_2_describe) / self.df_1_describe
        ) * 100
        self.absolute_differences = (
            self.df_1.select_dtypes(include="number").describe()
            - self.df_2.select_dtypes(include="number").describe()
        ).abs()

    def __categorical_comparisons(self):
        """
        Performs categorical comparisons between the two dataframes.

        Calculates the average frequency ratio and frequency differences of categorical values
        between the dataframes.

        Args:
            None
        Returns:
            None
        """
        avg_frequency_ratio = {}
        frequency_differences = {}

        for col in self.df_1.select_dtypes(exclude=["number"]):
            # Calculate frequency ratios
            frequency_ratio = (
                self.df_1[col].value_counts().sort_index()
                / self.df_2[col].value_counts().sort_index()
            ).mean()
            avg_frequency_ratio[col] = frequency_ratio

            # Calculate frequency differences
            frequency_diff = pd.DataFrame(self.df_1[col].value_counts()).merge(
                pd.DataFrame(self.df_2[col].value_counts()),
                left_index=True,
                right_index=True,
                suffixes=("_df1", "_df2"),
            )
            frequency_diff["absolute_difference"] = abs(
                frequency_diff["count_df1"] - frequency_diff["count_df2"]
            )
            frequency_diff["percent_difference"] = (
                frequency_diff["absolute_difference"]
                / (frequency_diff["count_df1"] + frequency_diff["count_df2"])
            ) * 100

            # Calculate percent of total
            total_count_df1 = frequency_diff["count_df1"].sum()
            total_count_df2 = frequency_diff["count_df2"].sum()
            frequency_diff["percent_total_df1"] = (
                frequency_diff["count_df1"] / total_count_df1
            ) * 100
            frequency_diff["percent_total_df2"] = (
                frequency_diff["count_df2"] / total_count_df2
            ) * 100

            frequency_differences[col] = frequency_diff

        self.avg_frequency_ratio = avg_frequency_ratio
        self.frequency_differences = frequency_differences

    def __get_dataframe_shapes(self):
        """
        Creates shape attribute of dataframes for comparisons.
        Args:
            None
        Returns:
            pd.DataFrame: dataframe containing row/col counts and percent/absolute differences
        """
        df = pd.DataFrame(
            {
                "df_1": [self.df_1.shape[0], self.df_1.shape[1]],
                "df_2": [self.df_2.shape[0], self.df_2.shape[1]],
            },
            index=["rows", "columns"],
        )
        df = df.assign(
            absolute_difference=lambda x: abs(x["df_1"] - x["df_2"]),
            percent_difference=lambda x: (
                x["absolute_difference"] / (x["df_1"] + x["df_2"])
            )
            * 100,
        )
        return df

    def compare(self):
        """
        Compares the two dataframes.

        Calls numeric_comparisons and categorical_comparisons methods to perform
        numeric and categorical comparisons between the dataframes.

        Args:
            None
        Returns:
            None
        """
        try:
            self.__assertions()  # Check assertions
        except AssertionError as e:
            raise AssertionError("Assertion Error: {}".format(str(e)))

        self.__numeric_comparisons()
        self.__categorical_comparisons()