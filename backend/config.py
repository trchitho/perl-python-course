import os
import urllib.parse


class Config:
    """Strict SQL Server configuration (SQLite disabled).

    Accepted inputs:
    - DATABASE_URL: must start with mssql+pyodbc://
    - Or MSSQL_* env vars to compose an ODBC connection string.
    """

    # Secrets
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)

    # Resolve SQL Server URI only
    env_url = os.getenv('DATABASE_URL') or ''
    if env_url:
        if not env_url.lower().startswith('mssql+pyodbc://'):
            raise RuntimeError('DATABASE_URL must use mssql+pyodbc; SQLite is disabled')
        SQLALCHEMY_DATABASE_URI = env_url
    else:
        SERVER = os.getenv('MSSQL_SERVER', r'np:\\.\pipe\MSSQL$SQLEXPRESS\sql\query')
        DATABASE = os.getenv('MSSQL_DATABASE', 'ELearningDB')
        USERNAME = os.getenv('MSSQL_USERNAME', 'learning')
        PASSWORD = os.getenv('MSSQL_PASSWORD', '123')
        DRIVER = os.getenv('MSSQL_DRIVER', 'ODBC Driver 18 for SQL Server')

        parts = [
            'DRIVER={' + DRIVER + '}',
            f'SERVER={SERVER}',
            f'DATABASE={DATABASE}',
            f'UID={USERNAME}',
            f'PWD={PASSWORD}',
            'Encrypt=yes',
            'TrustServerCertificate=yes',
        ]
        odbc_cs = ';'.join(parts)
        encoded = urllib.parse.quote_plus(odbc_cs)
        SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc:///?odbc_connect={encoded}'
        

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    # Keep default engine options minimal here; finalize in app factory
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }
