import json
import logging
import re
from dataclasses import dataclass
from typing import Any, ClassVar

# Constants
DETAILED_LOG_MODULE_REGEX = [
    r"^common\.middlewares$",
]
DEFAULT_VALUE = ""


@dataclass
class LogDetails:
    """Structure for holding log record details."""

    src_ip: str = DEFAULT_VALUE
    path: str = DEFAULT_VALUE
    method: str = DEFAULT_VALUE
    status_code: str = DEFAULT_VALUE
    reason: str = DEFAULT_VALUE
    response_time: float = 0.0
    error_trace: str | None = None


class BaseFormatter(logging.Formatter):
    """Base formatter with common functionality."""

    def get_log_details(self, record: logging.LogRecord) -> LogDetails:
        """Extract common log details from record."""
        return LogDetails(
            src_ip=getattr(record, "src_ip", DEFAULT_VALUE),
            path=getattr(record, "path", DEFAULT_VALUE),
            method=getattr(record, "method", DEFAULT_VALUE),
            status_code=getattr(record, "status_code", DEFAULT_VALUE),
            reason=getattr(record, "reason", DEFAULT_VALUE),
            response_time=float(getattr(record, "response_time", 0.0)),
            error_trace=getattr(record, "error_trace", None),
        )

    def format_message(self, details: LogDetails) -> str:
        """Format message with common pattern."""
        message = (
            f'{details.src_ip} {details.method} "{details.path}" '
            f"{details.status_code} {details.reason} - {details.response_time * 1000:5.2f}ms"
        )
        if details.error_trace:
            message += f"\n{details.error_trace}"
        return message


class JsonFormatter(BaseFormatter):
    """JSON formatter for logging system."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string.

        Args:
            record : logging.LogRecord
                The log record to be formatted.

        Returns:
            str: The formatted log message as a JSON string containing:
                - asctime: Formatted timestamp
                - level: Log level name
                - message: Formatted log message
                - ip: Source IP address
                - path: Request path
                - response_time_ms: Response time measured in milliseconds

        Returns:
            str: The formatted log message as a JSON string.
        """
        if re.match("|".join(DETAILED_LOG_MODULE_REGEX), record.module):
            details = self.get_log_details(record)
            message = self.format_message(details)
        else:
            message = record.getMessage()

        log_record: dict[str, Any] = {
            "asctime": self.formatTime(record, "%Y-%m-%d %H:%M:%S %z"),
            "level": record.levelname,
            "message": message,
            "ip": getattr(record, "src_ip", DEFAULT_VALUE),
            "path": getattr(record, "path", DEFAULT_VALUE),
            "module": record.module,
            "response_time_ms": getattr(record, "response_time", 0.0) * 1000,
        }
        return json.dumps(log_record)


class ColorFormatter(BaseFormatter):
    """Formatter that adds color codes to log messages."""

    COLORS: ClassVar[dict[str, str]] = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[1;31m",
        "RESET": "\033[0m",
        "BLUE": "\033[34m",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with color-coded output.

        Args:
        record : logging.LogRecord
            The log record to be formatted.

        Returns:
            str: The formatted log message with color codes.
        """
        levelname = record.levelname
        asctime = self.formatTime(record, "%Y-%m-%d %H:%M:%S%z")

        if re.match("|".join(DETAILED_LOG_MODULE_REGEX), record.module):
            details = self.get_log_details(record)
            message = self.format_message(details)
        else:
            message = record.getMessage()

        return (
            f"{self.COLORS.get(levelname, self.COLORS['RESET'])}{levelname:8}"
            f"{self.COLORS['BLUE']} - {asctime} - {self.COLORS['RESET']}"
            f"{message}"
        )


class RequestLoggingFilter(logging.Filter):
    """Filter that excludes h11_impl, operation, and basehttp module logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter logs to exclude health check requests and specific module logs.

        Args:
            record (logging.LogRecord): The log record to be filtered

        Returns:
            bool: True if the log record should be processed, False if it should be filtered out.
                Specifically, returns False for:
                - Health check requests from the 'middlewares' module
                - Any logs from the 'h11_impl', 'operation', or 'basehttp' modules
        """
        excluded_modules = {"h11_impl", "operation", "basehttp"}
        health_check_paths = {"/api/health_check", "/api/health_check/", "/"}
        is_health_check_log = getattr(record, "path", None) in health_check_paths
        return not (is_health_check_log or record.module in excluded_modules)
