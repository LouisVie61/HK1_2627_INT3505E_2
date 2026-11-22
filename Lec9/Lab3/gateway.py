"""Gateway routing for the blue-green order rollout."""

import hashlib
import logging

from flask import request

from handlers import v1_create_order, v2_create_order


# In production this value can be changed by a feature-flag dashboard.
V2_PERCENT = 5
V2_COHORTS = {"beta", "internal"}
V2_FORCE_ACCOUNTS = {"acct_42", "acct_99"}

log = logging.getLogger("gateway")


def route_to_v2(body):
    """Return whether *body* should be served by the v2 handler.

    Routing decisions deliberately have a stable priority.  A request that
    matches an explicit rule never falls through to the percentage rollout.
    """
    cohort = request.headers.get("X-Cohort", "").strip().lower()
    if cohort in V2_COHORTS:
        return True

    account_id = body.get("account_id", "") if isinstance(body, dict) else ""
    if account_id in V2_FORCE_ACCOUNTS:
        return True

    if V2_PERCENT <= 0:
        return False
    if V2_PERCENT >= 100:
        return True

    # md5 is used only as a deterministic bucketing function; no secret or
    # security decision depends on it.
    bucket = int(hashlib.md5(str(account_id).encode("utf-8")).hexdigest(), 16) % 100
    return bucket < V2_PERCENT


def dispatch(body):
    """Call the selected order handler and return ``(version, result)``."""
    if route_to_v2(body):
        log.info("routing order account=%s handler=v2", body.get("account_id"))
        return "v2", v2_create_order(body)

    log.info("routing order account=%s handler=v1", body.get("account_id"))
    return "v1", v1_create_order(body)
