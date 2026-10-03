import logging
import sys
import re
from contextvars import ContextVar
from typing import Optional

# Context variables for distributed request tracing and audit correlation
ctx_request_id: ContextVar[Optional[str]] = ContextVar("ctx_request_id", default=None)
ctx_org_id: ContextVar[Optional[str]] = ContextVar("ctx_org_id", default=None)
ctx_user_id: ContextVar[Optional[str]] = ContextVar("ctx_user_id", default=None)
ctx_tx_id: ContextVar[Optional[str]] = ContextVar("ctx_tx_id", default=None)

# Sanitization patterns for sensitive credentials
SENSITIVE_PATTERNS = [
    (re.compile(r'(password["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED]\3'),
    (re.compile(r'(authorization["\']?\s*[:=]\s*["\']Bearer\s+)([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED_JWT]\3'),
    (re.compile(r'(api_key["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED_KEY]\3'),
]

class ContextualSanitizingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Inject correlation IDs from contextvars
        req_id = ctx_request_id.get()
        org_id = ctx_org_id.get()
        user_id = ctx_user_id.get()
        tx_id = ctx_tx_id.get()

        context_parts = []
        if req_id:
            context_parts.append(f"req={req_id[:8]}")
        if org_id:
            context_parts.append(f"org={org_id[:8]}")
        if user_id:
            context_parts.append(f"user={user_id[:8]}")
        if tx_id:
            context_parts.append(f"tx={tx_id[:8]}")

        record.context_info = f"[{' '.join(context_parts)}] " if context_parts else ""
        
        # Standard format
        formatted = super().format(record)

        # Redact any passwords or secret tokens from log output
        for pattern, replacement in SENSITIVE_PATTERNS:
            formatted = pattern.sub(replacement, formatted)

        return formatted

def setup_logging():
    log = logging.getLogger("fraudshield")
    log.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = ContextualSanitizingFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(context_info)s%(message)s'
    )
    handler.setFormatter(formatter)
    
    if not log.handlers:
        log.addHandler(handler)
        
    return log

logger = setup_logging()
