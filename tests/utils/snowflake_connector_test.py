import os
import pytest
from pytest_mock import mocker
import pandas as pd
from src.utils import snowflake_connector as sc
from src.__main__ import load_profile_data

try:
    username = os.getenv("USER")
    if not username:
        username = os.getenv("USERNAME")
    if not username:
        raise ValueError("Environment variable for user is not set.")
except ValueError as e:
    print(e)

USER, ACCOUNT, WAREHOUSE, PASSWORD, _, _ = (
        load_profile_data(username)
    )

@pytest.fixture
def snowflake_connector():
    """Fixture to create SnowflakeConnector instance with mock connection"""
    snowflake_connector = sc.SnowflakeConnector(
        user=USER,
        password=PASSWORD,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
    )
    yield snowflake_connector

def test_conntect_to_smowflake(snowflake_connector):
    assert snowflake_connector.conn is not None


def test_query(snowflake_connector):
    """Test query method"""
    result = snowflake_connector.query('select * from sandbox_edw.analytics.data_profiling')
    assert type(result) == pd.DataFrame

def test_close_connection(snowflake_connector, mocker):
    """Test close_connection method"""
    # mock the connection object
    mock_close = mocker.patch.object(snowflake_connector.conn, 'close')
    
    # call the close_connection method
    snowflake_connector.close_connection()
    
    # assert that the close method of the connection object is called
    mock_close.assert_called_once()

