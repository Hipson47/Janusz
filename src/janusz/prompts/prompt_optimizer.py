#!/usr/bin/env python3
"""
Prompt Optimizer for Janusz

This module provides intelligent prompt optimization using LLM analysis
to improve prompt quality, clarity, and effectiveness.
"""

import logging
import time
from typing import Dict, List, Optional

from ..ai.ai_content_analyzer import AIContentAnalyzer
from ..models import (
    OptimizationResult,
    PromptOptimizationRequest,
    TestResult,
)

logger = logging.getLogger(__name__)


class PromptOptimizer:
    """
    AI-powered prompt optimizer that analyzes and improves LLM prompts.

    Uses advanced techniques like:
    - Clarity enhancement
    - Specificity improvement
    - Context optimization
    - Instruction refinement
    """

    def __init__(self, model: str = "anthropic/claude-3-haiku", api_key: Optional[str] = None):
        self.ai_analyzer = AIContentAnalyzer(model=model, api_key=api_key)
        self.optimization_strategies = {
            "clarity": self._optimize_for_clarity,
            "efficiency": self._optimize_for_efficiency,
            "specificity": self._optimize_for_specificity,
            "creativity": self._optimize_for_creativity,
            "conciseness": self._optimize_for_conciseness,
            "comprehensiveness": self._optimize_for_comprehensiveness,
        }

    async def optimize_prompt(self, request: PromptOptimizationRequest) -> OptimizationResult:
        """
        Optimize a prompt based on the specified goal.

        Args:
            request: Optimization request with prompt text and parameters

        Returns:
            OptimizationResult with original/optimized prompts and metrics
        """
        start_time = time.time()

        logger.info(f"Optimizing prompt for goal: {request.optimization_goal}")

        # Get the appropriate optimization strategy
        strategy = self.optimization_strategies.get(request.optimization_goal)
        if not strategy:
            raise ValueError(f"Unknown optimization goal: {request.optimization_goal}")

        # Run pre-optimization testing if test cases provided
        test_results_before = []
        if request.test_cases:
            test_results_before = await self._test_prompt_quality(
                request.text, request.test_cases, "original"
            )

        # Apply optimization strategy
        optimization_steps = []
        optimized_prompt = await strategy(request, optimization_steps)

        # Run post-optimization testing
        test_results_after = []
        if request.test_cases:
            test_results_after = await self._test_prompt_quality(
                optimized_prompt, request.test_cases, "optimized"
            )

        # Calculate improvement score
        improvement_score = self._calculate_improvement_score(
            test_results_before, test_results_after
        )

        # Generate suggestions for further improvement
        suggestions = await self._generate_improvement_suggestions(
            request.text, optimized_prompt, request.optimization_goal
        )

        total_time = time.time() - start_time
        logger.info(f"Prompt optimization completed in {total_time:.2f} seconds")
        return OptimizationResult(
            original_prompt=request.text,
            optimized_prompt=optimized_prompt,
            improvement_score=improvement_score,
            optimization_steps=optimization_steps,
            test_results_before=test_results_before,
            test_results_after=test_results_after,
            suggestions=suggestions,
        )

    async def _optimize_for_clarity(self, request: PromptOptimizationRequest, steps: List[str]) -> str:
        """Optimize prompt for clarity and understandability."""
        steps.append("Analyzing prompt clarity and structure")

        optimization_prompt = f"""
        Analyze the following prompt and optimize it for maximum clarity and understandability.
        Focus on:
        - Clear, unambiguous language
        - Logical structure and flow
        - Precise instructions
        - Elimination of jargon unless necessary
        - Better organization of information

        Original prompt:
        ---
        {request.text}
        ---

        Context (if any):
        {request.context or "No additional context provided"}

        Target model: {request.target_model}

        Provide an optimized version that maintains the original intent but significantly improves clarity.
        Explain your changes briefly, then provide the optimized prompt.
        """

        response = await self.ai_analyzer.client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert prompt engineer specializing in clarity optimization."},
                {"role": "user", "content": optimization_prompt}
            ],
            temperature=0.3,
            max_tokens=2048
        )

        if response:
            # Extract the optimized prompt from the response
            optimized = self._extract_optimized_prompt_from_response(response)
            steps.append("Applied clarity enhancements: clearer language, better structure")
            return optimized

        return request.text  # Fallback

    async def _optimize_for_efficiency(self, request: PromptOptimizationRequest, steps: List[str]) -> str:
        """Optimize prompt for token efficiency and conciseness."""
        steps.append("Analyzing prompt for token efficiency")

        optimization_prompt = f"""
        Analyze the following prompt and optimize it for maximum efficiency.
        Focus on:
        - Reducing token usage while maintaining effectiveness
        - Eliminating redundant instructions
        - Combining similar requirements
        - Using more concise language
        - Maintaining all essential information

        Original prompt (token count estimate: ~{len(request.text.split()) * 1.3:.0f}):
        ---
        {request.text}
        ---

        Provide an optimized version that achieves the same results with fewer tokens.
        Show both the optimized prompt and the estimated token savings.
        """

        response = await self.ai_analyzer.client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert at optimizing prompts for token efficiency."},
                {"role": "user", "content": optimization_prompt}
            ],
            temperature=0.2,
            max_tokens=1024
        )

        if response:
            optimized = self._extract_optimized_prompt_from_response(response)
            steps.append("Reduced token usage while maintaining effectiveness")
            return optimized

        return request.text

    async def _optimize_for_specificity(self, request: PromptOptimizationRequest, steps: List[str]) -> str:
        """Optimize prompt for specificity and precision."""
        steps.append("Enhancing prompt specificity and precision")

        optimization_prompt = f"""
        Analyze the following prompt and optimize it for maximum specificity.
        Focus on:
        - Adding specific examples and constraints
        - Defining clear success criteria
        - Eliminating vague language
        - Adding measurable requirements
        - Specifying exact formats and structures

        Original prompt:
        ---
        {request.text}
        ---

        Context: {request.context or "No context provided"}

        Provide an optimized version with much more specific instructions and requirements.
        """

        response = await self.ai_analyzer.client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert at making prompts highly specific and actionable."},
                {"role": "user", "content": optimization_prompt}
            ],
            temperature=0.3,
            max_tokens=1536
        )

        if response:
            optimized = self._extract_optimized_prompt_from_response(response)
            steps.append("Added specific examples, constraints, and measurable criteria")
            return optimized

        return request.text

    async def _optimize_for_creativity(self, request: PromptOptimizationRequest, steps: List[str]) -> str:
        """Optimize prompt to encourage creative outputs."""
        steps.append("Enhancing prompt for creative thinking")

        optimization_prompt = f"""
        Analyze the following prompt and optimize it to encourage maximum creativity.
        Focus on:
        - Removing restrictive constraints
        - Adding encouragement for novel approaches
        - Opening up possibilities
        - Encouraging experimentation
        - Maintaining core requirements while allowing flexibility

        Original prompt:
        ---
        {request.text}
        ---

        Provide an optimized version that stimulates creative thinking and novel solutions.
        """

        response = await self.ai_analyzer.client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert at crafting prompts that unleash creativity."},
                {"role": "user", "content": optimization_prompt}
            ],
            temperature=0.7,
            max_tokens=1536
        )

        if response:
            optimized = self._extract_optimized_prompt_from_response(response)
            steps.append("Encouraged creative thinking and novel approaches")
            return optimized

        return request.text

    async def _optimize_for_conciseness(self, request: PromptOptimizationRequest, steps: List[str]) -> str:
        """Optimize prompt for maximum conciseness."""
        steps.append("Making prompt more concise")

        optimization_prompt = f"""
        Analyze the following prompt and make it as concise as possible while maintaining effectiveness.
        Focus on:
        - Removing unnecessary words and phrases
        - Combining related instructions
        - Using more direct language
        - Eliminating redundancy
        - Keeping only essential information

        Original prompt (length: {len(request.text)} characters):
        ---
        {request.text}
        ---

        Provide a much more concise version that achieves the same results.
        """

        response = await self.ai_analyzer.client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert at making prompts concise and to-the-point."},
                {"role": "user", "content": optimization_prompt}
            ],
            temperature=0.2,
            max_tokens=1024
        )

        if response:
            optimized = self._extract_optimized_prompt_from_response(response)
            steps.append(f"Reduced length by {len(request.text) - len(optimized)} characters")
            return optimized

        return request.text

    async def _optimize_for_comprehensiveness(self, request: PromptOptimizationRequest, steps: List[str]) -> str:
        """Optimize prompt for comprehensive coverage."""
        steps.append("Making prompt more comprehensive")

        optimization_prompt = f"""
        Analyze the following prompt and optimize it for comprehensive coverage.
        Focus on:
        - Adding missing aspects and edge cases
        - Including comprehensive instructions
        - Covering all important scenarios
        - Adding completeness checks
        - Ensuring thoroughness

        Original prompt:
        ---
        {request.text}
        ---

        Context: {request.context or "No context provided"}

        Provide an optimized version that covers all important aspects comprehensively.
        """

        response = await self.ai_analyzer.client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert at making prompts comprehensive and thorough."},
                {"role": "user", "content": optimization_prompt}
            ],
            temperature=0.3,
            max_tokens=2048
        )

        if response:
            optimized = self._extract_optimized_prompt_from_response(response)
            steps.append("Added comprehensive coverage and edge case handling")
            return optimized

        return request.text

    async def _test_prompt_quality(self, prompt: str, test_cases: List[Dict[str, str]], label: str) -> List[TestResult]:
        """Test prompt quality against provided test cases."""
        results = []

        for i, test_case in enumerate(test_cases):
            start_time = time.time()

            test_prompt = f"""
            {prompt}

            Test Input: {test_case.get('input', '')}
            Expected Output: {test_case.get('expected', '')}
            """

            try:
                response = await self.ai_analyzer.client.chat_completion(
                    messages=[
                        {"role": "user", "content": test_prompt}
                    ],
                    temperature=0.5,
                    max_tokens=512
                )

                execution_time = time.time() - start_time

                if response:
                    # Simple quality scoring based on response characteristics
                    quality_score = self._calculate_quality_score(
                        response, test_case.get('expected', '')
                    )

                    results.append(TestResult(
                        prompt_id=f"{label}_test_{i}",
                        test_input=test_case.get('input', ''),
                        expected_output=test_case.get('expected', ''),
                        actual_output=response,
                        execution_time=execution_time,
                        token_usage=len(response.split()) * 1.3,  # Rough estimate
                        quality_score=quality_score,
                        metrics={"response_length": len(response)}
                    ))
                else:
                    results.append(TestResult(
                        prompt_id=f"{label}_test_{i}",
                        test_input=test_case.get('input', ''),
                        expected_output=test_case.get('expected', ''),
                        actual_output="No response generated",
                        execution_time=time.time() - start_time,
                        token_usage=0,
                        quality_score=0.0,
                    ))

            except Exception as e:
                logger.error(f"Error testing prompt: {e}")
                results.append(TestResult(
                    prompt_id=f"{label}_test_{i}",
                    test_input=test_case.get('input', ''),
                    expected_output=test_case.get('expected', ''),
                    actual_output=f"Error: {str(e)}",
                    execution_time=time.time() - start_time,
                    token_usage=0,
                    quality_score=0.0,
                ))

        return results

    def _calculate_improvement_score(self, before_results: List[TestResult], after_results: List[TestResult]) -> float:
        """Calculate improvement score between before and after optimization."""
        if not before_results or not after_results or len(before_results) != len(after_results):
            return 0.0

        before_avg = sum(r.quality_score for r in before_results) / len(before_results)
        after_avg = sum(r.quality_score for r in after_results) / len(after_results)

        if before_avg == 0:
            return after_avg

        improvement = (after_avg - before_avg) / before_avg
        return max(0.0, min(1.0, improvement))  # Clamp to [0, 1]

    def _calculate_quality_score(self, response: str, expected: str) -> float:
        """Calculate quality score for a response (simplified implementation)."""
        if not response.strip():
            return 0.0

        score = 0.5  # Base score

        # Length appropriateness
        if expected and 0.5 * len(expected) <= len(response) <= 2.0 * len(expected):
            score += 0.2

        # Contains expected elements (simple keyword matching)
        if expected:
            expected_words = set(expected.lower().split())
            response_words = set(response.lower().split())
            overlap = len(expected_words.intersection(response_words))
            if overlap > 0:
                score += 0.3 * min(1.0, overlap / len(expected_words))

        # Coherence (basic check)
        if len(response.split('.')) > 2:  # Has multiple sentences
            score += 0.1

        return min(1.0, score)

    def _extract_optimized_prompt_from_response(self, response: str) -> str:
        """Extract the optimized prompt from AI response."""
        # Look for common patterns in the response
        lines = response.split('\n')
        optimized_lines = []

        in_optimized_section = False
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for section markers
            if any(marker in line.lower() for marker in ['optimized prompt', 'improved prompt', 'optimized version']):
                in_optimized_section = True
                continue

            if in_optimized_section:
                # Stop if we hit another section
                if any(marker in line.lower() for marker in ['explanation', 'changes', 'analysis', '---', '===']):
                    break
                optimized_lines.append(line)

        # If we found optimized lines, join them
        if optimized_lines:
            return '\n'.join(optimized_lines)

        # Fallback: try to extract content between code blocks or quotes
        if '```' in response:
            parts = response.split('```')
            if len(parts) >= 3:
                return parts[1].strip()

        # Last resort: return the whole response
        return response.strip()

    async def _generate_improvement_suggestions(self, original: str, optimized: str, goal: str) -> List[str]:
        """Generate suggestions for further improvement."""
        if not self.ai_analyzer.client.is_available:
            return ["Consider adding more specific examples", "Test the prompt with different inputs"]

        suggestion_prompt = f"""
        Compare the original and optimized prompts and suggest further improvements.

        Original: {original[:500]}

        Optimized: {optimized[:500]}

        Goal: {goal}

        Provide 3-5 specific suggestions for further improvement.
        """

        try:
            response = await self.ai_analyzer.client.chat_completion(
                messages=[
                    {"role": "system", "content": "You are an expert prompt engineer."},
                    {"role": "user", "content": suggestion_prompt}
                ],
                temperature=0.4,
                max_tokens=512
            )

            if response:
                # Split into bullet points
                suggestions = [line.strip('- •').strip() for line in response.split('\n')
                             if line.strip().startswith(('- ', '• ', '* '))]
                return suggestions[:5] if suggestions else [response[:200]]

        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")

        return ["Test with more diverse inputs", "Consider adding output format specifications"]
