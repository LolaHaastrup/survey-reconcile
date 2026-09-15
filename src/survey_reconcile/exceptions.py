class SurveyReconcileError(Exception):
    """Base exception for expected pipeline failures."""


class ConfigurationError(SurveyReconcileError):
    """Raised when configuration is incomplete or inconsistent."""


class SchemaError(SurveyReconcileError):
    """Raised when an input file does not satisfy its configured schema."""

