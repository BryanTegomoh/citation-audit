"""Citation Verification Toolkit.

Detect and fix citation errors in academic literature.
"""

__version__ = "1.0.0"
__author__ = "Bryan Tegomoh"

from .coding_verifier import audit_coding, CodingAuditResult, CodingIssue

__all__ = ["audit_coding", "CodingAuditResult", "CodingIssue"]
