# Multi-Agent Orchestration Template

**Context**: Use this template for coordinating complex, multi-step workflows that require multiple specialized agents working together.

---

## Task Overview

**Complex Task**: [DESCRIBE THE OVERALL OBJECTIVE]

This task requires coordination between multiple specialized agents.

---

## Agent Definitions

### Available Agents

| Agent | Role | Tools | Scope |
|-------|------|-------|-------|
| **PlannerAgent** | Breaks down tasks, creates execution plans | Planning tools | High-level strategy |
| **ResearcherAgent** | Gathers information from sources | Web search, RAG, Docs | Information retrieval |
| **CoderAgent** | Writes and modifies code | File tools, Terminal | Implementation |
| **TesterAgent** | Creates and runs tests | Test runner, Coverage | Validation |
| **ReviewerAgent** | Reviews for quality and correctness | Code analysis | Quality assurance |

---

## Orchestration Rules

### Routing Logic
1. Analyze user request and classify intent
2. Route to appropriate specialist agent
3. Keep subsequent turns with same agent until topic shifts
4. Log every routing decision for debugging

### State Management
- Maintain shared state across agent handoffs
- Use session-specific state (keyed by session/user)
- Checkpoint at important milestones
- Each agent reads from and writes to shared state

### Verification Layers
- Before finalizing, invoke ReviewerAgent to validate
- On validation failure, route back to original agent for correction
- Maximum 3 correction attempts before escalation

### Error Handling
- On agent error: retry once, then try alternative approach
- On timeout: abort current step, log, and escalate
- On validation failure: route to correction flow
- Maximum 10 steps per workflow to prevent runaway loops

---

## Workflow Template

```yaml
workflow:
  name: "[WORKFLOW_NAME]"
  
  steps:
    - step: "Plan"
      agent: PlannerAgent
      action: "Analyze request and create execution plan"
      output: execution_plan
      
    - step: "Research"
      agent: ResearcherAgent
      action: "Gather required information"
      input: execution_plan
      output: research_results
      
    - step: "Implement"
      agent: CoderAgent
      action: "Write code according to plan"
      input: [execution_plan, research_results]
      output: implementation
      
    - step: "Test"
      agent: TesterAgent
      action: "Create and run tests"
      input: implementation
      output: test_results
      
    - step: "Review"
      agent: ReviewerAgent
      action: "Review implementation quality"
      input: [implementation, test_results]
      output: review_verdict
      
    - step: "Finalize"
      condition: "review_verdict == 'pass'"
      action: "Aggregate results and deliver"
      fallback: "Route to correction flow"
```

---

## Coordination Protocol

### Message Format
```json
{
  "from_agent": "AgentName",
  "to_agent": "AgentName | Orchestrator",
  "message_type": "request | response | error",
  "content": {
    "action": "what was done",
    "result": "output data",
    "status": "success | failure | needs_input"
  },
  "context": {
    "step_number": 1,
    "session_id": "...",
    "trace_id": "..."
  }
}
```

### Handoff Rules
- Agent completes its task fully before handoff
- Pass only necessary context to next agent
- Include validation status in handoff
- Orchestrator maintains global view

---

## Safety Controls

- [ ] Each agent has limited, well-defined tools
- [ ] No agent can execute high-risk actions without approval
- [ ] Maximum step limit enforced
- [ ] All agent actions logged for audit
- [ ] Human escalation path defined

---

## Success Criteria
- [ ] All subtasks completed successfully
- [ ] Final output meets all requirements
- [ ] All agent outputs validated
- [ ] Complete audit trail maintained
- [ ] No security violations

