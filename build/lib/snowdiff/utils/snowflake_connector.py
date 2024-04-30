import pandas as pd
import snowflake.connector

class SnowflakeConnector:
    """
    Class for connecting to Snowflake, executing a query,
    and returning a Pandas dataframe.
    Attributes:
        user: snowflake user name/email
        password: snowflake password
        account: alpha-num-id.location-id.cloud-provider
        warehouse: Snowflake warehouse
        authenticator: Snowflake SSO (default = 'external')
        conn: Snowflake connector object

    Methods:
        query: Executes query against Snowflake to return a dataframe
        close_connection: Closes the Snowflake connection once run is complete
        _connect_to_snowflake: Creates Snowflake connector object
    """

    def __init__(
        self,
        user: str,
        account: str,
        warehouse: str,
        authenticator: str = "externalbrowser",
        password: str = None,
    ):
        self.user = user
        self.password = password
        self.account = account
        self.authenticator = authenticator
        self.warehouse = warehouse.upper()
        self.conn = self._connect_to_snowflake()

    def close_connection(self):
        """Close Snowflake connector."""
        self.conn.close()

    def _connect_to_snowflake(self):
        """Establish connection to Snowflake via Password or SSO"""
        if self.password is not None:
            conn = snowflake.connector.connect(
                user=self.user,
                password=self.password,
                account=self.account,
                warehouse=self.warehouse,
            )
            return conn
        else:
            conn = snowflake.connector.connect(
                user=self.user,
                authenticator=self.authenticator,
                account=self.account,
                warehouse=self.warehouse,
            )
            return conn

    def query(self, query: str):
        """
        Executes query and retuns a dataframe
        Args:
            :param query: query
            :type query: string
        Returns:
            df (pd.DataFrame): Snowflake table as a dataframe
        """
        # Create a cursor object
        cur = self.conn.cursor()

        # Execute a query
        cur.execute(f"{query}")

        # Fetch the results
        results = cur.fetchall()

        # convert to df
        df = pd.DataFrame(results, columns=[col[0] for col in cur.description])

        cur.close()

        return df