#!/usr/bin/env python3
"""
Prompt Tester and Benchmarking System for Janusz

This module provides comprehensive testing and benchmarking capabilities
for prompt evaluation and comparison.
"""

import asyncio
import json
import logging
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..ai.ai_content_analyzer import AIContentAnalyzer
from ..models import BenchmarkResult, TestResult

logger = logging.getLogger(__name__)


class PromptTester:
    """
    Comprehensive prompt testing and benchmarking system.

    Provides:
    - Individual prompt testing
    - Comparative benchmarking
    - Statistical analysis
    - Performance metrics
    """

    def __init__(self, model: str = "anthropic/claude-3-haiku", api_key: Optional[str] = None,
                 max_concurrent: int = 3):
        self.ai_analyzer = AIContentAnalyzer(model=model, api_key=api_key)
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)

    async def test_prompt(self, prompt: str, test_cases: List[Dict[str, str]],
                         prompt_id: str = "test") -> List[TestResult]:
        """
        Test a single prompt against multiple test cases.

        Args:
            prompt: The prompt to test
            test_cases: List of test cases with 'input' and optional 'expected' keys
            prompt_id: Identifier for the prompt being tested

        Returns:
            List of TestResult objects
        """
        logger.info(f"Testing prompt '{prompt_id}' with {len(test_cases)} test cases")

        results = []

        # Process test cases concurrently but limit concurrency
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def test_single_case(case_idx: int, test_case: Dict[str, str]) -> TestResult:
            async with semaphore:
                return await self._execute_test_case(
                    prompt, test_case, f"{prompt_id}_case_{case_idx}"
                )

        tasks = [
            test_single_case(i, test_case)
            for i, test_case in enumerate(test_cases)
        ]

        results = await asyncio.gather(*tasks)
        logger.info(f"Completed testing prompt '{prompt_id}': {len(results)} results")
        return results

    async def benchmark_prompts(self, prompts: Dict[str, str],
                               test_dataset: List[Dict[str, str]],
                               model_name: str = "claude-3-haiku") -> List[BenchmarkResult]:
        """
        Benchmark multiple prompts against a test dataset.

        Args:
            prompts: Dict mapping prompt IDs to prompt texts
            test_dataset: List of test cases
            model_name: Name of the model being tested

        Returns:
            List of BenchmarkResult objects
        """
        logger.info(f"Benchmarking {len(prompts)} prompts against {len(test_dataset)} test cases")

        results = []

        for prompt_id, prompt_text in prompts.items():
            logger.info(f"Benchmarking prompt: {prompt_id}")

            start_time = time.time()
            test_results = await self.test_prompt(prompt_text, test_dataset, prompt_id)
            total_time = time.time() - start_time

            # Calculate aggregate metrics
            scores = [r.quality_score for r in test_results]
            metrics = self._calculate_metrics(scores)

            # Calculate confidence interval
            confidence_interval = self._calculate_confidence_interval(scores)

            benchmark_result = BenchmarkResult(
                prompt_id=prompt_id,
                model_name=model_name,
                test_dataset=f"dataset_{len(test_dataset)}_cases",
                metrics=metrics,
                average_score=statistics.mean(scores) if scores else 0.0,
                execution_time=total_time,
                total_token_usage=sum(r.token_usage for r in test_results),
                sample_size=len(test_results),
                confidence_interval=confidence_interval,
            )

            results.append(benchmark_result)
            logger.info(f"Completed benchmarking {prompt_id}: avg_score={benchmark_result.average_score:.3f}")

        return results

    async def compare_prompts(self, prompts: Dict[str, str],
                            test_dataset: List[Dict[str, str]],
                            baseline_prompt_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare multiple prompts and provide detailed analysis.

        Args:
            prompts: Dict mapping prompt IDs to prompt texts
            test_dataset: Test cases to evaluate against
            baseline_prompt_id: ID of baseline prompt for comparison

        Returns:
            Comprehensive comparison report
        """
        logger.info(f"Comparing {len(prompts)} prompts")

        # Run benchmarks
        benchmark_results = await self.benchmark_prompts(prompts, test_dataset)

        # Sort by average score
        sorted_results = sorted(benchmark_results, key=lambda x: x.average_score, reverse=True)

        # Calculate improvements over baseline
        if baseline_prompt_id and baseline_prompt_id in [r.prompt_id for r in benchmark_results]:
            baseline_result = next(r for r in benchmark_results if r.prompt_id == baseline_prompt_id)

            for result in benchmark_results:
                if result.prompt_id != baseline_prompt_id:
                    improvement = result.average_score - baseline_result.average_score
                    improvement_pct = (improvement / baseline_result.average_score) * 100 if baseline_result.average_score > 0 else 0

                    result.improvement_percentage = improvement_pct
                    result.comparison_baseline = baseline_prompt_id

        return {
            "ranking": [r.prompt_id for r in sorted_results],
            "results": {r.prompt_id: r.model_dump() for r in benchmark_results},
            "best_performer": sorted_results[0].prompt_id if sorted_results else None,
            "performance_spread": sorted_results[0].average_score - sorted_results[-1].average_score if len(sorted_results) > 1 else 0,
            "summary": self._generate_comparison_summary(benchmark_results),
        }

    async def _execute_test_case(self, prompt: str, test_case: Dict[str, str],
                               case_id: str) -> TestResult:
        """Execute a single test case."""
        start_time = time.time()

        # Prepare the test prompt
        test_input = test_case.get('input', '')
        expected_output = test_case.get('expected', '')

        full_prompt = f"{prompt}\n\nTest Input: {test_input}"
        if expected_output:
            full_prompt += f"\nExpected Output: {expected_output}"

        try:
            # Execute the prompt
            response = await self.ai_analyzer.client.chat_completion(
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.5,  # Consistent temperature for testing
                max_tokens=1024
            )

            execution_time = time.time() - start_time

            if response:
                # Calculate quality metrics
                quality_score = self._evaluate_response_quality(response, expected_output, test_input)
                metrics = self._calculate_detailed_metrics(response, expected_output, test_input)

                return TestResult(
                    prompt_id=case_id,
                    test_input=test_input,
                    expected_output=expected_output,
                    actual_output=response,
                    execution_time=execution_time,
                    token_usage=self._estimate_token_usage(response),
                    quality_score=quality_score,
                    metrics=metrics,
                )
            else:
                return TestResult(
                    prompt_id=case_id,
                    test_input=test_input,
                    expected_output=expected_output,
                    actual_output="No response generated",
                    execution_time=time.time() - start_time,
                    token_usage=0,
                    quality_score=0.0,
                    metrics={"error": "no_response"},
                )

        except Exception as e:
            logger.error(f"Error executing test case {case_id}: {e}")
            return TestResult(
                prompt_id=case_id,
                test_input=test_input,
                expected_output=expected_output,
                actual_output=f"Error: {str(e)}",
                execution_time=time.time() - start_time,
                token_usage=0,
                quality_score=0.0,
                metrics={"error": str(e)},
            )

    def _evaluate_response_quality(self, response: str, expected: str, input_text: str) -> float:
        """
        Evaluate the quality of a response based on multiple criteria.

        Returns a score between 0.0 and 1.0
        """
        if not response.strip():
            return 0.0

        score = 0.0
        criteria_count = 0

        # Relevance to input
        if input_text:
            input_words = set(input_text.lower().split())
            response_words = set(response.lower().split())
            overlap = len(input_words.intersection(response_words))
            relevance_score = min(1.0, overlap / max(1, len(input_words)))
            score += relevance_score
            criteria_count += 1

        # Adherence to expected output (if provided)
        if expected:
            expected_words = set(expected.lower().split())
            response_words = set(response.lower().split())
            overlap = len(expected_words.intersection(response_words))
            adherence_score = min(1.0, overlap / max(1, len(expected_words)))
            score += adherence_score
            criteria_count += 1

        # Response coherence (basic check)
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        if len(sentences) > 1:
            coherence_score = min(1.0, len(sentences) / 3)  # Reward multiple coherent sentences
            score += coherence_score
            criteria_count += 1

        # Response length appropriateness
        word_count = len(response.split())
        if expected:
            expected_word_count = len(expected.split())
            if expected_word_count > 0:
                length_ratio = word_count / expected_word_count
                # Ideal ratio between 0.5 and 2.0
                if 0.5 <= length_ratio <= 2.0:
                    length_score = 1.0
                elif length_ratio < 0.5:
                    length_score = length_ratio / 0.5
                else:
                    length_score = 2.0 / length_ratio
                score += length_score
                criteria_count += 1

        # Basic grammar check (very simple)
        if any(punct in response for punct in ['.', '!', '?']):
            score += 0.5
            criteria_count += 1

        return score / max(1, criteria_count)

    def _calculate_detailed_metrics(self, response: str, expected: str, input_text: str) -> Dict[str, float]:
        """Calculate detailed metrics for response analysis."""
        metrics = {}

        # Basic counts
        metrics["response_length_chars"] = len(response)
        metrics["response_length_words"] = len(response.split())
        metrics["response_length_sentences"] = len([s for s in response.split('.') if s.strip()])

        # Readability approximation
        avg_words_per_sentence = metrics["response_length_words"] / max(1, metrics["response_length_sentences"])
        metrics["avg_words_per_sentence"] = avg_words_per_sentence

        # Complexity score (0-1, higher is more complex)
        complex_words = sum(1 for word in response.split() if len(word) > 6)
        metrics["complexity_score"] = min(1.0, complex_words / max(1, metrics["response_length_words"]))

        # Uniqueness (approximate)
        words = response.lower().split()
        unique_words = len(set(words))
        metrics["vocabulary_richness"] = unique_words / max(1, len(words))

        return metrics

    def _estimate_token_usage(self, text: str) -> int:
        """Roughly estimate token usage (GPT-style approximation)."""
        # Simple approximation: ~4 characters per token
        return len(text) // 4

    def _calculate_metrics(self, scores: List[float]) -> Dict[str, float]:
        """Calculate statistical metrics from a list of scores."""
        if not scores:
            return {}

        return {
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
            "min_score": min(scores),
            "max_score": max(scores),
            "q25": statistics.quantiles(scores, n=4)[0] if len(scores) >= 4 else min(scores),
            "q75": statistics.quantiles(scores, n=4)[2] if len(scores) >= 4 else max(scores),
        }

    def _calculate_confidence_interval(self, scores: List[float], confidence: float = 0.95) -> Optional[Tuple[float, float]]:
        """Calculate confidence interval for scores."""
        if len(scores) < 2:
            return None

        mean = statistics.mean(scores)
        std_err = statistics.stdev(scores) / (len(scores) ** 0.5)

        # Approximation using t-distribution (simplified)
        t_value = 2.0  # Roughly 95% confidence for reasonable sample sizes
        margin = t_value * std_err

        return (mean - margin, mean + margin)

    def _generate_comparison_summary(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Generate a summary of benchmark comparison."""
        if not results:
            return {}

        best_result = max(results, key=lambda r: r.average_score)
        worst_result = min(results, key=lambda r: r.average_score)

        return {
            "total_prompts": len(results),
            "best_prompt": best_result.prompt_id,
            "best_score": best_result.average_score,
            "worst_prompt": worst_result.prompt_id,
            "worst_score": worst_result.average_score,
            "score_range": best_result.average_score - worst_result.average_score,
            "average_execution_time": statistics.mean([r.execution_time for r in results]),
            "total_token_usage": sum(r.total_token_usage for r in results),
        }

    async def load_test_dataset(self, dataset_path: str) -> List[Dict[str, str]]:
        """Load test dataset from JSON file."""
        path = Path(dataset_path)
        if not path.exists():
            raise FileNotFoundError(f"Test dataset not found: {dataset_path}")

        with open(path, encoding='utf-8') as f:
            data = json.load(f)

        return data.get("test_cases", [])

    def save_test_results(self, results: List[TestResult], output_path: str):
        """Save test results to JSON file."""
        output_data = {
            "metadata": {
                "total_tests": len(results),
                "average_score": statistics.mean([r.quality_score for r in results]) if results else 0,
                "export_date": time.time(),
            },
            "results": [result.model_dump() for result in results],
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

    def save_benchmark_results(self, results: List[BenchmarkResult], output_path: str):
        """Save benchmark results to JSON file."""
        output_data = {
            "metadata": {
                "total_benchmarks": len(results),
                "export_date": time.time(),
            },
            "results": [result.model_dump() for result in results],
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
