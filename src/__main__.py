import os
import yaml
import argparse
from src.utils import expected_profile, snowflake_connector


def parse_arguments():
    """
    Parses arguments for main script as CLI flags. If no --flags,
    will ask for user input.
    Args:
        None
    Returns:
        ArgumentParser.parse_args() object
    """
    parser = argparse.ArgumentParser(
        description="Compare tables between prod/dev environments in Snowflake via dbt project.yml file."
    )

    # Add arguments for table name and filter
    parser.add_argument(
        "-t", "--table", type=str, help="Name of the Snowflake table to compare."
    )
    parser.add_argument(
        "-f", "--filter", type=str, help="Filter condition for the comparison query."
    )
    parser.add_argument(
        "-cs",
        "--custom-schema",
        type=str,
        help="Name of the custom Snowflake schema to compare.",
    )

    args = parser.parse_args()

    if not (args.table and args.filter):
        print("Schema, table, and filter are required. Please provide values.")
        custom_schema, table, filter_condition = get_user_input()
        args.custom_schema = custom_schema if custom_schema else args.custom_schema
        args.table = table if table else args.table
        args.filter = filter_condition if filter_condition else args.filter

    return args


def get_user_input():
    """
    Gets user input for table, custom schema, and filter_condition.
    Default schema is 'DBT for production and 'DBT_DEV' for development.
    Args:
        None
    Returns:
        (tuple) : schema (str), table (str), filter_condition (str)
    """
    table = input("Enter the name of the Snowflake table to compare: ")
    custom_schema = input(
        "Enter custom schema of the Snowflake table (leave blank if default): "
    )
    filter_condition = input("Enter a filter condition for the comparison query: ")

    return custom_schema, table, filter_condition


def load_profile_data(username):
    """
    Load and parse the profiles.yml file for a specific user.

    Args:
        username (str): The username used to construct the file path.

    Returns:
        tuple: A tuple containing the user, account, warehouse, 
        password, schema_prod, schema_dev.
    """
    # Construct the file path using the username
    try:
        # mac
        profiles_path = os.path.join("/Users", username, ".dbt", "profiles.yml")
    except (OSError, FileNotFoundError):
        # windows
        profiles_path = os.path.join("C:\\Users", username, ".dbt", "profiles.yml")

    # Load and parse the YAML file
    with open(profiles_path, "r") as file:
        profiles_data = yaml.safe_load(file)

    # Extract relevant information from the parsed YAML data
    try:
        account = profiles_data["default"]["outputs"]["dev"]["account"]
        password = profiles_data["default"]["outputs"]["dev"]["password"]
        user = profiles_data["default"]["outputs"]["dev"]["user"]
        warehouse = profiles_data["default"]["outputs"]["dev"]["warehouse"]
        schema_prod = profiles_data["default"]["outputs"]["prod"]["schema"]
        schema_dev = profiles_data["default"]["outputs"]["dev"]["schema"]

    except KeyError:
        raise KeyError(
            "The specified key path does not exist in the profiles.yml file."
        )

    return user, account, warehouse, password, schema_prod, schema_dev


def main():
    """
    Runs main function to print snowflake data diffs.
    """
    # get username env variable
    try:
        username = os.getenv("USER")
        if not username:
            username = os.getenv("USERNAME")
        if not username:
            raise ValueError("Environment variable for user is not set.")
    except ValueError as e:
        print(e)

    # get the necessary credentials
    USER, ACCOUNT, WAREHOUSE, PASSWORD, SCHEMA_PROD_DEFAULT, SCHEMA_DEV_DEFAULT = (
        load_profile_data(username)
    )

    # get args
    args = parse_arguments()

    DATABASE_PROD = "PRD_EDW_DBT"
    DATABASE_DEV = "SANDBOX_EDW"

    CUSTOM_SCHEMA = args.custom_schema

    if CUSTOM_SCHEMA is None:
        SCHEMA_PROD = SCHEMA_PROD_DEFAULT
        SCHEMA_DEV = SCHEMA_DEV_DEFAULT
    else:
        SCHEMA_PROD = f"DBT_{CUSTOM_SCHEMA}"
        SCHEMA_DEV = f"DBT_DEV_{CUSTOM_SCHEMA}"

    TABLE = args.table
    FILTER = args.filter

    sc = snowflake_connector.SnowflakeConnector(
        user=USER, account=ACCOUNT, warehouse=WAREHOUSE, password=PASSWORD
    )

    try:
        query_prod = f"""
        select * 
        from {DATABASE_PROD}.{SCHEMA_PROD}.{TABLE} 
        where {FILTER} 
        """
        query_dev = f"""
        select * 
        from {DATABASE_DEV}.{SCHEMA_DEV}.{TABLE} 
        where {FILTER} 
        """

        df_prod = sc.query(query_prod)
        df_dev = sc.query(query_dev)

        ep = expected_profile.ExpectedProfiler(df_prod, df_dev)

        ep.compare()
        print("---" * 25)
        print("DataFrame Key:\n")
        print(f"df_1 = {DATABASE_PROD}.{SCHEMA_PROD.upper()}.{TABLE.upper()}")
        print(f"df_2 = {DATABASE_DEV}.{SCHEMA_DEV.upper()}.{TABLE.upper()}")
        #print("---" * 15)
        print("\nTable Shape Differences:\n")
        print(ep.shapes)

        # if ep.compare() ran succesfully:
        if ep.percent_differences != None:
            print("---" * 15)
            print("\nMean Percent Differences Between Numeric Columns:\n")
            print(ep.percent_differences.loc["mean"])
            print("---" * 25)
            print("\nMean Frequency Ratio of Categorical Columns\n")
            for col, ratio in ep.avg_frequency_ratio.items():
                print(f"{col}: {ratio}")
        else:
            pass
        print("---" * 25)
    except Exception as e:
        print(f"An error occurred with the query:\n {str(e)}")


if __name__ == "__main__":
    main()
