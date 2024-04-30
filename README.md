# Snow Diff CLI

This is a CLI tool that allows dbt users to quickly see a high-level difference between a table that exists in both the production and development environments. It utilizes the dbt project.yml file to get the needed Snowflake credentials/schemas and 
then queries from both databases to then numerically compare the outputs of the table. 

## Requirements:
- Make sure you have the ```project.yml``` file in your ```.dbt``` directry
  - Ex: ```C:\Users\JairusMartinez\.dbt\profiles.yml```
- Include both the development and production dbt environments in the ```project.yml``` file:

```{YAML}
default:
  outputs:
    dev:
      account: zb45354.east-us-2.azure
      database: SANDBOX_EDW
      password: your-snowflake-password
      role: ANALYTICS_ENGINEER
      schema: DBT_DEV
      threads: 4
      type: snowflake
      user: your-curaleaf-email
      warehouse: WH_BI_PRD
    prod:
      account: zb45354.east-us-2.azure
      database: PRD_EDW_DBT
      password: your-snowflake-password
      role: ANALYTICS_ENGINEER
      schema: DBT
      threads: 4
      type: snowflake
      user: your-curaleaf-email
      warehouse: WH_BI_PRD
  target: dev
```
- Have dbt-core / dbt-cloud CLI set up
- Have a dedicated virtual environment for dbt to use PowerUser in VSCode

### Virtual Environment Dependencies
- Make sure your pipenv / venv contains:
```
pandas = "*"
numpy = "*"
snowflake-connector-python = "*"
dbt-snowflake = "*"
pyyaml = "*"
```

# Downloading Snow Diff CLI Package:
1. Activate your dbt virtual environment
2. Make sure the packages above are installed
3. In your dbt virtual environment run the command:
   - ```pip install -e git+https://github.com/jairus-c/snowdiff-cli.git#egg=snowdiff-cli```
4. Run the command pip freeze in your virtual environment and look for the output below to verify the installation:
```
snow-diff @ file:///C:/Users/JairusMartinez/OneDrive%20-%20Curaleaf/Desktop/snowdiff-cli
-e git+https://github.com/jairus-c/snowdiff-cli.git@6990bfd9f1842c1ae14b56ac127fb8129a9d7e88#egg=snowdiff_cli
```
5. To uninstall from your activated virtual environment, run:
   - ```pip uninstall snowdiff-cli```
6. To update, simply run the command from step 4!
  
# Usage

