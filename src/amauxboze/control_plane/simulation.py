from __future__ import annotations

from amauxboze.registries import AgentRegistry, SkillRegistry


def example(schema: dict, name: str = ""):
    kind = schema.get("type", "string")
    if kind == "object":
        return {key: example(rule, key) for key, rule in schema.get("properties", {}).items()}
    if kind == "array":
        return []
    if kind == "boolean":
        return name in {"consequential", "response_required"}
    if kind in {"number", "integer"}:
        return 0
    return "SIMULATION · Beispiel, keine belegte Geschäftsaussage."


class SimulationExecutor:
    def __init__(self, agents: AgentRegistry, skills: SkillRegistry):
        self.agents, self.skills = agents, skills

    def __call__(self, agent, skill_id, payload):
        self.agents.assert_skill_allowed(agent, skill_id)
        self.skills.validate_input(skill_id, payload)
        result = example(self.skills.get(skill_id).outputs)
        if "category" in result:
            result["category"] = "product"
        if "summary" in result and agent == "elena":
            result["summary"] = "SIMULATION · Dieser Plan braucht Belege. Definiere Ziel, Verantwortlichen und Erfolgskriterium, bevor du Ressourcen bindest."
        if skill_id == "define-product-brief":
            result.update(objective=f"SIMULATION · {payload['founder_brief']}", constraints=payload.get("constraints", []), open_questions=["Welche messbare Kundenwirkung soll die Uhr haben?"])
        if skill_id == "intake-feedback":
            result.update(source=payload["source"], observation=payload["raw_feedback"], metadata={"simulation": True})
        if skill_id == "prioritize-feedback-action":
            result.update(priority="review", rationale="SIMULATION · Auswirkungen prüfen, keine Änderung ohne Entscheidung.", consequential=True)
        if skill_id == "prepare-strategic-decision":
            result["decision_options"] = ["act", "investigate_further", "monitor", "archive"]
        if skill_id == "update-intelligence-knowledge":
            result["status"] = "simulation_only_not_written"
        self.skills.validate_output(skill_id, result)
        return result
