import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from argparse import Namespace
from src.utils import expected_profile, snowflake_connector
from src.__main__ import parse_arguments, get_user_input, load_profile_data, main

try:
    username = os.getenv("USER")
    if not username:
        username = os.getenv("USERNAME")
    if not username:
        raise ValueError("Environment variable for user is not set.")
except ValueError as e:
    print(e)

@pytest.fixture
def mock_args():
    args = Namespace(table='test_table', filter='test_filter', custom_schema='test_schema')
    return args

@patch('argparse.ArgumentParser.parse_args')
def test_parse_arguments(mock_parse_args):
    mock_parse_args.return_value = Namespace(table='test_table', filter='test_filter', custom_schema='test_schema')
    assert parse_arguments() == mock_parse_args.return_value

@patch('builtins.input', side_effect=['test_table', 'test_schema', 'test_filter'])
def test_get_user_input(mock_input):
    assert get_user_input() == ('test_schema', 'test_table', 'test_filter')

def test_load_profile_data():
    USER, ACCOUNT, WAREHOUSE, PASSWORD, SCHEMA_PROD_DEFAULT, SCHEMA_DEV_DEFAULT = (
        load_profile_data(username)
    )

    assert USER is not None
    assert ACCOUNT is not None
    assert WAREHOUSE is not None
    assert PASSWORD is not None
    assert SCHEMA_PROD_DEFAULT is not None
    assert SCHEMA_DEV_DEFAULT is not None

@patch('os.getenv', MagicMock(return_value=username))
@patch('src.utils.snowflake_connector.SnowflakeConnector')
@patch('argparse.ArgumentParser.parse_args')
def test_main(mock_parse_args, mock_snowflake_connector):
    mock_parse_args.return_value = Namespace(table='test_table', filter='test_filter', custom_schema=None)
    mock_snowflake_connector_instance = MagicMock()
    mock_snowflake_connector.return_value = mock_snowflake_connector_instance
    main()
    mock_snowflake_connector_instance.query.assert_called()
