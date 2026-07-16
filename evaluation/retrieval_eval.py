"""Asynchronous RAGAS evaluation module using Ragas 0.4.3 direct scoring APIs."""

import asyncio
from typing import List, Dict
from observability.structured_logger import get_logger
from config.settings import settings

logger = get_logger(__name__)

async def evaluate_ragas_async(
    query: str,
    answer: str,
    contexts: List[str],
    ground_truth: str = ""
) -> Dict[str, float]:
    """
    Runs RAGAS evaluation asynchronously using direct .ascore() methods.
    Evaluates:
    - Faithfulness (groundedness / no hallucination check)
    - Answer Relevancy
    If ground_truth is provided:
    - Context Precision
    - Context Recall
    - Answer Correctness
    Uses free Groq/Gemini models as Judges to avoid OpenAI API costs.
    """
    if not settings.ENABLE_RAGAS_EVALS:
        return {}
        
    try:
        import instructor
        from groq import Groq
        from ragas.llms.base import InstructorLLM
        from ragas.embeddings import GoogleEmbeddings
        from ragas.metrics.collections import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall, AnswerCorrectness

        # 1. Initialize Ragas LLM (using Groq)
        groq_client = Groq(api_key=settings.GROQ_API_KEY)
        patched_client = instructor.from_groq(groq_client)
        ragas_llm = InstructorLLM(
            client=patched_client,
            model=settings.PRIMARY_MODEL,
            provider="groq"
        )

        # 2. Initialize Ragas Embeddings (using Gemini)
        ragas_emb = GoogleEmbeddings(model=settings.GEMINI_EMBEDDING_MODEL)

        # 3. Instantiate Metrics
        faith = Faithfulness(llm=ragas_llm)
        answer_rel = AnswerRelevancy(llm=ragas_llm, embeddings=ragas_emb)

        # Build list of coroutines to run in parallel
        # Faithfulness: (user_input, response, retrieved_contexts)
        # AnswerRelevancy: (user_input, response)
        tasks = {
            "faithfulness": faith.ascore(user_input=query, response=answer, retrieved_contexts=contexts),
            "answer_relevance": answer_rel.ascore(user_input=query, response=answer)
        }

        if ground_truth:
            # ContextPrecision: (user_input, reference, retrieved_contexts)
            ctx_precision = ContextPrecision(llm=ragas_llm)
            # ContextRecall: (user_input, retrieved_contexts, reference)
            ctx_recall = ContextRecall(llm=ragas_llm)
            # AnswerCorrectness: (user_input, response, reference)
            ans_correctness = AnswerCorrectness(llm=ragas_llm, embeddings=ragas_emb)

            tasks["context_precision"] = ctx_precision.ascore(user_input=query, reference=ground_truth, retrieved_contexts=contexts)
            tasks["context_recall"] = ctx_recall.ascore(user_input=query, retrieved_contexts=contexts, reference=ground_truth)
            tasks["answer_correctness"] = ans_correctness.ascore(user_input=query, response=answer, reference=ground_truth)

        # Run tasks concurrently
        keys = list(tasks.keys())
        coroutines = list(tasks.values())
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        scores = {}
        for key, result in zip(keys, results):
            if isinstance(result, Exception):
                logger.error(f"[RAGAS] Metric '{key}' evaluation failed: {result}")
            else:
                try:
                    scores[key] = round(float(result.value), 4)
                except (TypeError, ValueError) as val_err:
                    logger.warning(f"[RAGAS] Failed to parse score for '{key}': {val_err}")

        logger.info(f"[RAGAS] Live evaluation complete for query '{query[:30]}...': {scores}")
        return scores

    except ImportError as e:
        logger.error(f"[RAGAS] Missing dependency. Run `pip install ragas datasets`: {e}")
        return {}
    except Exception as e:
        logger.error(f"[RAGAS] Evaluation pipeline initialization failed: {e}")
        return {}
