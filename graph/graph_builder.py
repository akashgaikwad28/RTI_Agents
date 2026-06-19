"""Builds and compiles the RTI-Agent LangGraph StateGraph."""

from __future__ import annotations

import os
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from config.settings import settings
from graph.nodes.approval_node import approval_node
from graph.nodes.classifier_node import classifier_node
from graph.nodes.consensus_node import consensus_node
from graph.nodes.critic_node import critic_node
from graph.nodes.debate_node import debate_node
from graph.nodes.formatter_node import formatter_node
from graph.nodes.memory_learning_node import memory_learning_node
from graph.nodes.planner_node import planner_node
from graph.nodes.reflection_node import reflection_node
from graph.nodes.retrieval_node import retrieval_node
from graph.nodes.reviewer_node import reviewer_node
from graph.nodes.router_node import router_node
from graph.nodes.tool_selection_node import tool_selection_node
from graph.nodes.tracker_node import tracker_node
from graph.nodes.verifier_node import verifier_node
from graph.nodes.info_fetcher_node import info_fetcher_node
from graph.router import route_after_approval, route_after_consensus, route_after_reflection, route_after_reviewer, route_after_router, route_after_info_fetcher

from graph.state import RTIAgentState
from observability.structured_logger import get_logger

logger = get_logger(__name__)


class LazyPostgresCheckpointer(BaseCheckpointSaver):
    def __init__(self):
        super().__init__()
        self._delegate = None
        self._conn_string = None
        self._context = None

    def set_delegate(self, checkpointer):
        self._delegate = checkpointer

    def set_conn_string(self, conn_string):
        self._conn_string = conn_string

    def set_context(self, context):
        self._context = context

    async def _reconnect(self):
        if not self._conn_string:
            logger.warning("[LazyPostgresCheckpointer] Cannot reconnect: No connection string configured.")
            return

        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        logger.info("📡 Re-connecting to Neon PostgreSQL checkpointer...")

        if self._context:
            try:
                await self._context.__aexit__(None, None, None)
            except Exception as ex:
                logger.debug(f"[LazyPostgresCheckpointer] Error exiting old Postgres context: {ex}")

        try:
            self._context = AsyncPostgresSaver.from_conn_string(self._conn_string)
            self._delegate = await self._context.__aenter__()
            await self._delegate.setup()
            logger.info("✅ Neon PostgreSQL checkpointer successfully reconnected and schema verified")
        except Exception as e:
            logger.error(f"[LazyPostgresCheckpointer] Failed to re-establish connection pool: {e}")
            raise e

    async def _safe_call(self, method_name, *args, **kwargs):
        if self._delegate is None:
            raise RuntimeError("Postgres checkpointer not initialized yet")

        last_ex = None
        for attempt in range(3):
            try:
                method = getattr(self._delegate, method_name)
                return await method(*args, **kwargs)
            except Exception as e:
                last_ex = e
                err_msg = str(e).lower()
                is_conn_error = any(
                    token in err_msg
                    for token in [
                        "terminating connection",
                        "closed",
                        "admin",
                        "connection",
                        "broken pipe",
                        "operationalerror",
                        "interfaceerror",
                        "pool"
                    ]
                )
                if is_conn_error and attempt < 2:
                    logger.warning(
                        f"[LazyPostgresCheckpointer] Postgres connection error on '{method_name}': {e}. "
                        f"Reconnecting and retrying (attempt {attempt + 1}/3)..."
                    )
                    try:
                        await self._reconnect()
                    except Exception as reconn_err:
                        logger.error(f"[LazyPostgresCheckpointer] Reconnection attempt failed: {reconn_err}")
                        last_ex = reconn_err
                else:
                    raise e
        if last_ex:
            raise last_ex

    def get(self, config):
        if self._delegate is None:
            raise RuntimeError("Postgres checkpointer not initialized yet")
        return self._delegate.get(config)

    def get_tuple(self, config):
        if self._delegate is None:
            raise RuntimeError("Postgres checkpointer not initialized yet")
        return self._delegate.get_tuple(config)

    def list(self, config, *, filter=None, before=None, limit=None):
        if self._delegate is None:
            raise RuntimeError("Postgres checkpointer not initialized yet")
        return self._delegate.list(config, filter=filter, before=before, limit=limit)

    def put(self, config, checkpoint, metadata, new_versions):
        if self._delegate is None:
            raise RuntimeError("Postgres checkpointer not initialized yet")
        return self._delegate.put(config, checkpoint, metadata, new_versions)

    def put_writes(self, config, writes, taskId):
        if self._delegate is None:
            raise RuntimeError("Postgres checkpointer not initialized yet")
        return self._delegate.put_writes(config, writes, taskId)

    def delete_thread(self, config):
        if self._delegate is None:
            raise RuntimeError("Postgres checkpointer not initialized yet")
        return self._delegate.delete_thread(config)

    async def aget(self, config):
        return await self._safe_call("aget", config)

    async def aget_tuple(self, config):
        return await self._safe_call("aget_tuple", config)

    async def alist(self, config, *, filter=None, before=None, limit=None):
        return await self._safe_call("alist", config, filter=filter, before=before, limit=limit)

    async def aput(self, config, checkpoint, metadata, new_versions):
        return await self._safe_call("aput", config, checkpoint, metadata, new_versions)

    async def aput_writes(self, config, writes, taskId):
        return await self._safe_call("aput_writes", config, writes, taskId)

    async def adelete_thread(self, config):
        return await self._safe_call("adelete_thread", config)



lazy_checkpointer = LazyPostgresCheckpointer()


def build_graph(enable_hitl: bool = True):
    if settings.CHECKPOINTER_TYPE == "postgres" and settings.POSTGRES_CHECKPOINTER_URL:
        checkpointer = lazy_checkpointer
    else:
        db_path = settings.CHECKPOINTER_DB
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path, check_same_thread=False)
        checkpointer = SqliteSaver(conn)

    builder = StateGraph(RTIAgentState)

    for name, node in {
        "router_node": router_node,
        "planner_node": planner_node,
        "formatter_node": formatter_node,
        "info_fetcher_node": info_fetcher_node,
        "classifier_node": classifier_node,
        "tool_selection_node": tool_selection_node,
        "retrieval_node": retrieval_node,
        "debate_node": debate_node,
        "critic_node": critic_node,
        "verifier_node": verifier_node,
        "reviewer_node": reviewer_node,
        "approval_node": approval_node,
        "reflection_node": reflection_node,
        "consensus_node": consensus_node,
        "memory_learning_node": memory_learning_node,
        "tracker_node": tracker_node,
    }.items():
        builder.add_node(name, node)

    builder.add_edge(START, "router_node")
    builder.add_conditional_edges("router_node", route_after_router, {"planner_node": "planner_node", "tracker_node": "tracker_node"})
    builder.add_edge("planner_node", "formatter_node")
    builder.add_edge("formatter_node", "info_fetcher_node")
    builder.add_conditional_edges("info_fetcher_node", route_after_info_fetcher, {"tracker_node": "tracker_node", "classifier_node": "classifier_node"})
    builder.add_edge("classifier_node", "tool_selection_node")
    builder.add_edge("tool_selection_node", "retrieval_node")
    builder.add_edge("retrieval_node", "debate_node")
    builder.add_edge("debate_node", "critic_node")
    builder.add_edge("critic_node", "verifier_node")
    builder.add_edge("verifier_node", "reviewer_node")
    builder.add_conditional_edges("reviewer_node", route_after_reviewer, {"approval_node": "approval_node", "reflection_node": "reflection_node"})
    builder.add_conditional_edges("approval_node", route_after_approval, {"consensus_node": "consensus_node", "reflection_node": "reflection_node", "approval_node": "approval_node"})
    builder.add_conditional_edges("reflection_node", route_after_reflection, {"formatter_node": "formatter_node", "tracker_node": "tracker_node"})
    builder.add_conditional_edges("consensus_node", route_after_consensus, {"memory_learning_node": "memory_learning_node"})
    builder.add_edge("memory_learning_node", "tracker_node")
    builder.add_edge("tracker_node", END)

    graph = builder.compile(checkpointer=checkpointer, interrupt_before=["approval_node"] if enable_hitl else [])
    logger.info(f"[GraphBuilder] Graph compiled | nodes={list(builder.nodes.keys())} | hitl={'enabled' if enable_hitl else 'disabled'}")
    return graph


_graph_instance = None


def get_graph(enable_hitl: bool = True):
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = build_graph(enable_hitl=enable_hitl)
    return _graph_instance

