"""
llm_router/circuit_breaker.py
------------------------------
Simple circuit breaker for LLM provider resilience.
States: CLOSED (normal) → OPEN (failing) → HALF_OPEN (testing)
"""

import time
from observability.structured_logger import get_logger

logger = get_logger(__name__)


class CircuitBreaker:
    """
    Circuit breaker to protect against cascading LLM provider failures.

    States:
    - CLOSED   : Normal operation, all calls pass through.
    - OPEN     : Too many failures, calls blocked for reset_timeout.
    - HALF_OPEN: Testing if provider has recovered.
    """

    def __init__(self, name: str, failure_threshold: int = 5, reset_timeout: float = 60.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._state = "CLOSED"

    @property
    def is_open(self) -> bool:
        """Returns True if circuit is OPEN (calls should be blocked)."""
        if self._state == "OPEN":
            # Check if reset timeout has elapsed → move to HALF_OPEN
            if self._last_failure_time and (time.time() - self._last_failure_time) > self.reset_timeout:
                self._state = "HALF_OPEN"
                logger.info(f"[CircuitBreaker:{self.name}] → HALF_OPEN (testing recovery)")
                return False
            return True
        return False

    def record_failure(self):
        """Record a failure. Opens circuit if threshold exceeded."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.failure_threshold:
            self._state = "OPEN"
            logger.warning(
                f"[CircuitBreaker:{self.name}] OPEN after {self._failure_count} failures. "
                f"Blocking for {self.reset_timeout}s."
            )

    def record_success(self):
        """Record a success. Resets circuit to CLOSED."""
        if self._state in ("OPEN", "HALF_OPEN"):
            logger.info(f"[CircuitBreaker:{self.name}] → CLOSED (recovered)")
        self._failure_count = 0
        self._last_failure_time = None
        self._state = "CLOSED"

    def get_state(self) -> dict:
        return {
            "name": self.name,
            "state": self._state,
            "failure_count": self._failure_count,
            "is_open": self.is_open,
        }
