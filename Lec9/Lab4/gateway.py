"""Three-tier blue-green routing for the order endpoint."""

import hashlib
import logging

from flask import request

from handlers import v1_create_order, v2_create_order


V2_PERCENT = 5
V2_COHORTS = {"beta", "internal"}
V2_FORCE_ACCOUNTS = {"acct_42", "acct_99"}

log = logging.getLogger("gateway")


def route_to_v2(body):
    """Apply cohort, allow-list, then deterministic percentage routing."""
    cohort = request.headers.get("X-Cohort", "").strip().lower()
    if cohort in V2_COHORTS:
        return True

    account_id = body.get("account_id", "")
    if account_id in V2_FORCE_ACCOUNTS:
        return True

    if V2_PERCENT <= 0:
        return False
    if V2_PERCENT >= 100:
        return True

    bucket = int(hashlib.md5(str(account_id).encode("utf-8")).hexdigest(), 16) % 100
    return bucket < V2_PERCENT


def dispatch(body):
    if route_to_v2(body):
        log.info("order routed to v2: account_id=%s", body.get("account_id"))
        return "v2", v2_create_order(body)

    log.info("order routed to v1: account_id=%s", body.get("account_id"))
    return "v1", v1_create_order(body)
