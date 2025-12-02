#!/usr/bin/env python3
"""
AI Orchestrator for Janusz Document Processing

Provides intelligent orchestration of document processing workflows,
including schema selection, AI model routing, and context-aware decision making.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models import (
    OrchestratorContext, OrchestratorResponse, DocumentStructure,
    ModularSchema
)
from ..schemas.schema_manager import SchemaManager
from ..ai.ai_content_analyzer import AIContentAnalyzer

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    AI-powered orchestrator for intelligent document processing.

    Features:
    - Context-aware schema selection
    - Intent recognition and workflow optimization
    - AI model routing based on task complexity
    - Adaptive processing based on user preferences
    """

    def __init__(self,
                 schema_manager: Optional[SchemaManager] = None,
                 ai_analyzer: Optional[AIContentAnalyzer] = None):
        """
        Initialize AI Orchestrator.

        Args:
            schema_manager: Schema manager instance
            ai_analyzer: AI analyzer for decision making
        """
        self.schema_manager = schema_manager or SchemaManager()
        self.ai_analyzer = ai_analyzer
        self.user_context_history: List[Dict[str, Any]] = []

    def process_document_request(self,
                               user_input: str,
                               document: Optional[DocumentStructure] = None,
                               context: Optional[OrchestratorContext] = None) -> OrchestratorResponse:
        """
        Process a document processing request with intelligent orchestration.

        Args:
            user_input: Natural language description of what the user wants
            document: Optional document to process
            context: Additional context information

        Returns:
            Orchestrator response with recommendations
        """
        # Analyze user intent
        intent_analysis = self._analyze_user_intent(user_input)

        # Build orchestrator context
        orch_context = self._build_context(user_input, document, context, intent_analysis)

        # Generate recommendations
        response = self._generate_orchestrator_response(orch_context, document)

        # Update context history
        self._update_context_history(user_input, response)

        return response

    def recommend_schemas_for_document(self,
                                     document: DocumentStructure,
                                     user_requirements: Optional[str] = None) -> List[ModularSchema]:
        """
        Recommend appropriate schemas for a document.

        Args:
            document: Document to analyze
            user_requirements: Optional user requirements

        Returns:
            List of recommended schemas
        """
        # Find matching schemas based on content
        matching_schemas = self.schema_manager.find_matching_schemas(document)

        if user_requirements and self.ai_analyzer:
            # Use AI to refine recommendations based on requirements
            refined_schemas = self._refine_schema_recommendations_ai(
                matching_schemas, document, user_requirements
            )
            return refined_schemas

        return matching_schemas[:5]  # Return top 5

    def optimize_processing_workflow(self,
                                  document: DocumentStructure,
                                  selected_schema: ModularSchema,
                                  user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize the document processing workflow based on schema and preferences.

        Args:
            document: Document to process
            selected_schema: Selected processing schema
            user_preferences: User processing preferences

        Returns:
            Optimized processing configuration
        """
        workflow_config = {
            "schema_id": selected_schema.id,
            "ai_processing": self._should_use_ai(document, selected_schema, user_preferences),
            "quality_level": user_preferences.get("quality_level", "standard"),
            "output_formats": user_preferences.get("output_formats", ["YAML"]),
            "processing_steps": self._determine_processing_steps(selected_schema, user_preferences)
        }

        # AI-based optimization if available
        if self.ai_analyzer and workflow_config["ai_processing"]:
            ai_optimized = self._optimize_workflow_ai(document, workflow_config)
            workflow_config.update(ai_optimized)

        return workflow_config

    def _analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user intent from natural language input."""
        intent_analysis = {
            "primary_action": "unknown",
            "document_type": None,
            "complexity": "medium",
            "urgency": "normal",
            "quality_focus": False
        }

        input_lower = user_input.lower()

        # Determine primary action
        if any(word in input_lower for word in ["convert", "transform", "change"]):
            intent_analysis["primary_action"] = "convert"
        elif any(word in input_lower for word in ["analyze", "understand", "review"]):
            intent_analysis["primary_action"] = "analyze"
        elif any(word in input_lower for word in ["optimize", "improve", "enhance"]):
            intent_analysis["primary_action"] = "optimize"

        # Determine document type hints
        if "api" in input_lower:
            intent_analysis["document_type"] = "api_documentation"
        elif "security" in input_lower or "secure" in input_lower:
            intent_analysis["document_type"] = "security_guide"
        elif "tutorial" in input_lower or "guide" in input_lower:
            intent_analysis["document_type"] = "tutorial"

        # Determine complexity
        if any(word in input_lower for word in ["simple", "basic", "quick"]):
            intent_analysis["complexity"] = "simple"
        elif any(word in input_lower for word in ["complex", "detailed", "comprehensive"]):
            intent_analysis["complexity"] = "complex"

        # Determine urgency
        if any(word in input_lower for word in ["urgent", "asap", "quickly", "fast"]):
            intent_analysis["urgency"] = "high"

        # Quality focus
        intent_analysis["quality_focus"] = any(word in input_lower for word in
                                              ["quality", "high-quality", "professional", "polish"])

        return intent_analysis

    def _build_context(self, user_input: str,
                      document: Optional[DocumentStructure],
                      context: Optional[OrchestratorContext],
                      intent_analysis: Dict[str, Any]) -> OrchestratorContext:
        """Build comprehensive orchestrator context."""

        # Start with provided context or create new
        orch_context = context or OrchestratorContext(user_intent=user_input)

        # Update with intent analysis
        orch_context.user_intent = user_input
        orch_context.complexity_level = intent_analysis.get("complexity", "medium")
        orch_context.quality_requirements = ("high" if intent_analysis.get("quality_focus")
                                          else orch_context.quality_requirements)

        # Infer from document if available
        if document:
            orch_context.document_type = (orch_context.document_type or
                                        self._infer_document_type(document))
            orch_context.domain = self._infer_document_domain(document)

        # Update available schemas
        orch_context.available_schemas = [s.id for s in self.schema_manager.list_schemas()]

        # Add recent context
        if self.user_context_history:
            recent_contexts = self.user_context_history[-3:]  # Last 3 interactions
            orch_context.previous_interactions = recent_contexts

        return orch_context

    def _generate_orchestrator_response(self,
                                      context: OrchestratorContext,
                                      document: Optional[DocumentStructure]) -> OrchestratorResponse:
        """Generate intelligent orchestrator response."""

        recommended_schema_ids = []
        reasoning_parts = []
        confidence_score = 0.5

        # Basic schema recommendations
        if document:
            matching_schemas = self.schema_manager.find_matching_schemas(document, limit=3)
            recommended_schema_ids = [s.id for s in matching_schemas]

            if matching_schemas:
                top_schema = matching_schemas[0]
                reasoning_parts.append(f"Found matching schema '{top_schema.name}' with {top_schema.confidence_score:.1%} confidence")
                confidence_score = top_schema.confidence_score

        # AI-enhanced reasoning if available
        if self.ai_analyzer and context.user_intent:
            ai_reasoning = self._generate_ai_reasoning(context, document)
            reasoning_parts.append(ai_reasoning)
            confidence_score = max(confidence_score, 0.7)  # AI boosts confidence

        # Build reasoning
        reasoning = " ".join(reasoning_parts) if reasoning_parts else "Standard processing recommended"

        # Generate alternatives
        alternatives = self._generate_alternatives(context, recommended_schema_ids)

        # Processing plan
        processing_plan = self._create_processing_plan(context, recommended_schema_ids)

        # Estimated time
        estimated_time = self._estimate_processing_time(context, len(recommended_schema_ids or []))

        return OrchestratorResponse(
            recommended_schemas=recommended_schema_ids,
            reasoning=reasoning,
            confidence_score=confidence_score,
            alternative_options=alternatives,
            processing_plan=processing_plan,
            estimated_time=estimated_time
        )

    def _generate_ai_reasoning(self, context: OrchestratorContext,
                             document: Optional[DocumentStructure]) -> str:
        """Generate AI-enhanced reasoning for orchestration decisions."""
        if not self.ai_analyzer:
            return ""

        prompt = f"""
        Analyze this document processing request and provide reasoning for schema selection:

        User Intent: {context.user_intent}
        Document Type: {context.document_type or 'Unknown'}
        Complexity: {context.complexity_level}
        Quality Requirements: {context.quality_requirements}

        Available schemas: {', '.join(context.available_schemas[:5])}

        Provide concise reasoning (2-3 sentences) for the best processing approach.
        """

        try:
            response = self.ai_analyzer.client.chat_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=200)

            return response["choices"][0]["message"]["content"].strip()

        except Exception as e:
            logger.warning(f"AI reasoning failed: {e}")
            return "AI reasoning unavailable, using standard approach"

    def _infer_document_type(self, document: DocumentStructure) -> str:
        """Infer document type from content."""
        title_lower = document.metadata.title.lower()
        content_lower = document.content.raw_text[:1000].lower()

        if any(keyword in title_lower + content_lower for keyword in
               ["api", "endpoint", "rest", "graphql", "swagger"]):
            return "api_documentation"
        elif any(keyword in title_lower + content_lower for keyword in
                 ["security", "authentication", "authorization", "vulnerability"]):
            return "security_guide"
        elif any(keyword in title_lower + content_lower for keyword in
                 ["tutorial", "guide", "how to", "getting started"]):
            return "tutorial"
        else:
            return "technical_document"

    def _infer_document_domain(self, document: DocumentStructure) -> Optional[str]:
        """Infer document domain/specialization."""
        content_lower = document.content.raw_text[:2000].lower()

        domains = {
            "web": ["web", "http", "html", "javascript", "frontend", "backend"],
            "data": ["database", "sql", "nosql", "data", "analytics"],
            "ai": ["ai", "machine learning", "neural", "gpt", "llm"],
            "devops": ["docker", "kubernetes", "ci/cd", "deployment"],
            "security": ["security", "encryption", "authentication", "oauth"]
        }

        for domain, keywords in domains.items():
            if any(keyword in content_lower for keyword in keywords):
                return domain

        return None

    def _should_use_ai(self, document: DocumentStructure,
                      schema: ModularSchema, preferences: Dict[str, Any]) -> bool:
        """Determine if AI processing should be used."""
        # Check user preference
        if preferences.get("use_ai") is False:
            return False

        # Use AI for complex documents
        doc_length = len(document.content.raw_text)
        if doc_length > 5000:  # Long documents benefit from AI
            return True

        # Use AI for high-quality requirements
        if preferences.get("quality_level") == "high":
            return True

        # Use AI if schema recommends it
        if schema.confidence_score > 0.8:
            return True

        return False

    def _determine_processing_steps(self, schema: ModularSchema,
                                  preferences: Dict[str, Any]) -> List[str]:
        """Determine the processing steps for a schema."""
        steps = ["load_document", "parse_structure"]

        if preferences.get("use_ai", False):
            steps.extend(["ai_analysis", "apply_schema"])

        steps.extend(["generate_output", "validate_results"])

        return steps

    def _refine_schema_recommendations_ai(self, schemas: List[ModularSchema],
                                        document: DocumentStructure,
                                        requirements: str) -> List[ModularSchema]:
        """Use AI to refine schema recommendations based on user requirements."""
        if not self.ai_analyzer:
            return schemas

        prompt = f"""
        Given these schemas and user requirements, rank and filter the most relevant ones:

        Schemas:
        {chr(10).join([f"- {s.name}: {s.description}" for s in schemas])}

        User Requirements: {requirements}

        Document Type: {self._infer_document_type(document)}

        Return the top 3 most relevant schema names, separated by newlines.
        """

        try:
            response = self.ai_analyzer.client.chat_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=100)

            recommended_names = response["choices"][0]["message"]["content"].strip().split('\n')
            recommended_names = [name.strip('- ').strip() for name in recommended_names if name.strip()]

            # Filter schemas by recommended names
            name_to_schema = {s.name: s for s in schemas}
            filtered_schemas = []

            for name in recommended_names:
                if name in name_to_schema:
                    filtered_schemas.append(name_to_schema[name])

            return filtered_schemas or schemas[:3]

        except Exception as e:
            logger.warning(f"AI schema refinement failed: {e}")
            return schemas[:3]

    def _generate_alternatives(self, context: OrchestratorContext,
                             recommended_ids: List[str]) -> List[Dict[str, Any]]:
        """Generate alternative processing options."""
        alternatives = []

        # Alternative schemas
        all_schemas = self.schema_manager.list_schemas()
        alternative_schemas = [s for s in all_schemas if s.id not in recommended_ids][:2]

        for schema in alternative_schemas:
            alternatives.append({
                "type": "alternative_schema",
                "schema_id": schema.id,
                "reason": f"Alternative approach: {schema.description}"
            })

        # Alternative processing options
        if context.quality_requirements != "high":
            alternatives.append({
                "type": "processing_option",
                "option": "skip_ai",
                "reason": "Faster processing without AI analysis"
            })

        return alternatives

    def _create_processing_plan(self, context: OrchestratorContext,
                              schema_ids: List[str]) -> Dict[str, Any]:
        """Create a detailed processing plan."""
        plan = {
            "steps": ["validate_input", "load_document"],
            "schemas_to_apply": schema_ids,
            "ai_processing": context.quality_requirements == "high",
            "output_formats": ["YAML"],  # Default
            "validation_required": True
        }

        if schema_ids:
            plan["steps"].extend(["apply_schema", "extract_content", "generate_output"])

        if context.quality_requirements == "high":
            plan["steps"].append("quality_assessment")

        return plan

    def _estimate_processing_time(self, context: OrchestratorContext,
                                num_schemas: int) -> int:
        """Estimate processing time in seconds."""
        base_time = 30  # Base processing time
        schema_time = num_schemas * 15  # Time per schema
        ai_time = 45 if context.quality_requirements == "high" else 0  # AI processing time

        return base_time + schema_time + ai_time

    def _optimize_workflow_ai(self, document: DocumentStructure,
                            workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to optimize workflow configuration."""
        if not self.ai_analyzer:
            return {}

        prompt = f"""
        Optimize this document processing workflow:

        Current config: {workflow_config}
        Document length: {len(document.content.raw_text)} characters
        Document type: {self._infer_document_type(document)}

        Suggest optimizations for processing time, quality, or resource usage.
        Return JSON with optimization suggestions.
        """

        try:
            response = self.ai_analyzer.client.chat_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=150)

            content = response["choices"][0]["message"]["content"]
            optimizations = json.loads(content)
            return optimizations

        except Exception as e:
            logger.warning(f"AI workflow optimization failed: {e}")
            return {}

    def _update_context_history(self, user_input: str, response: OrchestratorResponse):
        """Update context history for future decisions."""
        context_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "recommended_schemas": response.recommended_schemas,
            "confidence": response.confidence_score,
            "processing_plan": response.processing_plan
        }

        self.user_context_history.append(context_entry)

        # Keep only last 10 entries
        if len(self.user_context_history) > 10:
            self.user_context_history = self.user_context_history[-10:]


# Import here to avoid circular imports
import json
