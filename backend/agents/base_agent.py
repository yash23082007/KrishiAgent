"""
BaseAgent — Abstract Autonomous Agent with Reasoning Lifecycle.

Every KrishiAgent specialist agent inherits from this base class,
which enforces a structured think → act → validate → reflect cycle.
This ensures each agent is genuinely autonomous — it reasons about its
inputs, decides how to act, validates its outputs, and self-corrects
on failure.
"""

import time
import traceback
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, ValidationError
from utils.logger import get_logger

logger = get_logger("agent")


class AgentTrace:
    """Captures the full reasoning trace of an agent execution."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.thinking: str = ""
        self.action_log: str = ""
        self.validation_status: str = ""
        self.reflection: str = ""
        self.retries: int = 0
        self.latency_ms: int = 0
        self.success: bool = False
        self.error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "agent": self.agent_name,
            "thinking": self.thinking,
            "action_log": self.action_log,
            "validation_status": self.validation_status,
            "reflection": self.reflection,
            "retries": self.retries,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error": self.error,
        }


class BaseAgent(ABC):
    """
    Abstract base class for all KrishiAgent autonomous agents.

    Lifecycle:
        1. think()    — Reason about the input and plan the approach
        2. act()      — Execute the core tool/API call
        3. validate() — Validate output against Pydantic schema
        4. reflect()  — Self-assess quality and decide if retry is needed

    Features:
        - Automatic retry with self-correction (up to max_retries)
        - Pydantic output validation
        - Structured reasoning trace logging
        - Latency measurement
    """

    role: str = "Agent"
    goal: str = ""
    backstory: str = ""
    max_retries: int = 2
    output_schema: Optional[Type[BaseModel]] = None

    @abstractmethod
    async def think(self, **kwargs) -> str:
        """
        Reasoning step: analyze inputs and plan the approach.
        Returns a string describing the agent's reasoning chain.
        """
        pass

    @abstractmethod
    async def act(self, **kwargs) -> dict:
        """
        Action step: execute the core tool call and return raw results.
        """
        pass

    def validate(self, result: dict) -> dict:
        """
        Validation step: validate output against the Pydantic schema.
        Fills in defaults for missing fields. Raises ValidationError if invalid.
        """
        if self.output_schema is None:
            return result

        try:
            validated = self.output_schema.model_validate(result)
            return validated.model_dump()
        except ValidationError as e:
            logger.warning(
                f"[{self.role}] Output validation failed: {e}. "
                f"Attempting to fix with defaults."
            )
            # Try to fill missing fields with schema defaults
            for field_name, field_info in self.output_schema.model_fields.items():
                if field_name not in result:
                    if field_info.default is not None:
                        result[field_name] = field_info.default
                    elif field_info.default_factory is not None:
                        result[field_name] = field_info.default_factory()
            # Re-validate after fixes
            validated = self.output_schema.model_validate(result)
            return validated.model_dump()

    async def reflect(self, result: dict, thinking: str) -> str:
        """
        Reflection step: self-assess output quality.
        Returns a string with the agent's self-assessment.
        Override in subclasses for domain-specific reflection.
        """
        confidence = result.get("confidence", None)
        if confidence is not None and confidence < 0.5:
            return (
                f"Low confidence ({confidence}). "
                f"Result may be unreliable — flagging for human expert review."
            )
        return f"Output validated successfully. Agent {self.role} completed task."

    async def execute_with_reasoning(self, **kwargs) -> tuple[dict, AgentTrace]:
        """
        Full autonomous execution lifecycle with reasoning trace.

        Returns:
            tuple of (result_dict, AgentTrace)
        """
        trace = AgentTrace(self.role)
        start_time = time.time()
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # Step 1: THINK — Reason about the task
                thinking = await self.think(**kwargs)
                trace.thinking = thinking
                logger.info(f"[{self.role}] THINK: {thinking[:200]}")

                # Step 2: ACT — Execute core tool
                trace.action_log = f"Attempt {attempt + 1}/{self.max_retries + 1}"
                result = await self.act(**kwargs)
                logger.info(f"[{self.role}] ACT: Got result with {len(result)} fields")

                # Step 3: VALIDATE — Check output against schema
                result = self.validate(result)
                trace.validation_status = "PASSED"
                logger.info(f"[{self.role}] VALIDATE: Schema validation passed")

                # Step 4: REFLECT — Self-assess quality
                reflection = await self.reflect(result, thinking)
                trace.reflection = reflection
                logger.info(f"[{self.role}] REFLECT: {reflection[:200]}")

                # Attach reasoning to result
                result["_reasoning"] = {
                    "thinking": thinking,
                    "reflection": reflection,
                    "retries": attempt,
                }

                trace.success = True
                trace.retries = attempt
                trace.latency_ms = int((time.time() - start_time) * 1000)
                return result, trace

            except Exception as e:
                last_error = str(e)
                trace.retries = attempt + 1
                logger.warning(
                    f"[{self.role}] Attempt {attempt + 1} failed: {last_error}"
                )
                if attempt < self.max_retries:
                    logger.info(
                        f"[{self.role}] Self-correcting — retrying with stricter constraints..."
                    )
                    # Enable strict mode for retry (subclasses can check this)
                    kwargs["_strict_mode"] = True
                    kwargs["_retry_attempt"] = attempt + 1
                    kwargs["_last_error"] = last_error

        # All retries exhausted
        trace.success = False
        trace.error = last_error
        trace.validation_status = "FAILED"
        trace.latency_ms = int((time.time() - start_time) * 1000)
        logger.error(
            f"[{self.role}] All {self.max_retries + 1} attempts failed: {last_error}"
        )

        # Return a minimal fallback result
        fallback = self._get_fallback_result(**kwargs)
        fallback["_reasoning"] = {
            "thinking": trace.thinking or "Failed before reasoning could complete",
            "reflection": f"FAILED after {self.max_retries + 1} attempts: {last_error}",
            "retries": self.max_retries + 1,
        }
        return fallback, trace

    def _get_fallback_result(self, **kwargs) -> dict:
        """Override in subclasses to provide domain-specific fallback results."""
        return {}
