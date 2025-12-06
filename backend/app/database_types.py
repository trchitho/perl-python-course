"""
Custom SQLAlchemy types for SQL Server Vietnamese support
Force NVARCHAR instead of VARCHAR for Unicode text
"""
from sqlalchemy.types import TypeDecorator, Unicode, UnicodeText
from sqlalchemy.dialects.mssql import NVARCHAR


class UnicodeString(TypeDecorator):
    """Force NVARCHAR for SQL Server to support Vietnamese"""
    impl = Unicode
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'mssql':
            return dialect.type_descriptor(NVARCHAR(self.impl.length))
        else:
            return dialect.type_descriptor(Unicode(self.impl.length))


class UnicodeTextType(TypeDecorator):
    """Force NVARCHAR(MAX) for SQL Server to support Vietnamese"""
    impl = UnicodeText
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'mssql':
            return dialect.type_descriptor(NVARCHAR(None))  # NVARCHAR(MAX)
        else:
            return dialect.type_descriptor(UnicodeText())
