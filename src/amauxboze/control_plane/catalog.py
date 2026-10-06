from __future__ import annotations

from .contracts import Department, Organization, OrganizationNode, ProcessDefinition


DEPARTMENTS = [
    Department(id="operations", name="Operations", mission="Fokus, Prioritäten und gemeinsame Umsetzung.", member_ids=["elena"]),
    Department(id="product", name="Product", mission="Uhren mit Substanz und klarer Produktspezifikation.", member_ids=["lucien"]),
    Department(id="marketing", name="Marketing", mission="Marke, Geschichten und relevante Inhalte.", member_ids=["elodie", "maya"]),
    Department(id="intelligence", name="Intelligence", mission="Belegte Signale statt Vermutungen.", member_ids=["nora"]),
    Department(id="commerce", name="Commerce", mission="Wachstum und wirtschaftliche Klarheit.", member_ids=["marc"]),
    Department(id="customer", name="Customer", mission="Kunden verstehen, unterstützen und lernen.", member_ids=["sophie"]),
    Department(id="technology", name="Technology", mission="Verlässliche Systeme und kontrollierte Automatisierung.", member_ids=["kai"]),
]


def schema(fields: dict[str, dict], required: list[str]) -> dict:
    return {"type": "object", "properties": fields, "required": required, "additionalProperties": False}


def text(label: str, default: str = "") -> dict:
    return {"type": "string", "title": label, "default": default, "minLength": 1, "maxLength": 12000}


PROCESSES = [
    ProcessDefinition(id="watch-development", name="Neue Uhr entwickeln", description="Von der Gründeridee zur freigegebenen Produktspezifikation.", owner_department_id="product", participant_department_ids=["operations", "intelligence", "marketing", "commerce", "customer"], input_schema=schema({"founder_brief": text("Deine Produktidee"), "product_working_title": text("Arbeitstitel", "Neue Uhr"), "constraints": {"type": "array", "title": "Rahmenbedingungen (eine pro Zeile)", "items": {"type": "string"}}}, ["founder_brief"]), approval_summary="Konzeptfreigabe und separate Produktionsfreigabe."),
    ProcessDefinition(id="product-launch", name="Produkt lancieren", description="Ein freigegebenes Produkt für Markt, Inhalte und Kunden vorbereiten.", owner_department_id="commerce", participant_department_ids=["operations", "product", "marketing", "customer", "intelligence"], input_schema=schema({"approved_run_id": text("Freigegebene Produktentwicklung"), "product_id": text("Produkt-ID"), "launch_objective": text("Launch-Ziel")}, ["approved_run_id", "product_id", "launch_objective"]), approval_summary="Founder-Freigabe vor Aktivierung.", external_action="product_launch", live_limitation="Launch-Planung ist live möglich. Veröffentlichung wartet auf konfigurierte Shopify-, Social- und Community-Adapter."),
    ProcessDefinition(id="content-campaign", name="Content-Kampagne", description="Ziel, Botschaft, Kanäle und Inhalte gemeinsam erarbeiten.", owner_department_id="marketing", participant_department_ids=["operations", "customer", "intelligence", "commerce"], input_schema=schema({"campaign_objective": text("Kampagnenziel"), "audience": text("Zielgruppe")}, ["campaign_objective", "audience"]), approval_summary="Founder-Freigabe vor Veröffentlichung.", external_action="social_publish", live_limitation="Inhalte werden live vorbereitet. Social-Publishing ist ohne Adapter nicht verfügbar."),
    ProcessDefinition(id="customer-feedback", name="Kundenfeedback → Learning", description="Feedback einordnen, Auswirkungen bewerten und Wissen sichern.", owner_department_id="customer", participant_department_ids=["operations", "product", "marketing", "commerce", "intelligence"], input_schema=schema({"source": text("Feedback-Quelle", "Manuell"), "raw_feedback": text("Originalfeedback"), "customer_context": {"type": "object", "title": "Kundenkontext (JSON)", "default": {}}}, ["source", "raw_feedback"]), approval_summary="Konsequenzielle Änderungen benötigen Founder-Freigabe. Antworten bleiben Entwürfe."),
    ProcessDefinition(id="market-intelligence", name="Markt → strategischer Insight", description="Signale, Interpretationen und strategische Entscheidungen trennen.", owner_department_id="intelligence", participant_department_ids=["operations", "product", "marketing", "commerce", "customer"], input_schema=schema({"watch_topic": text("Recherchethema"), "geography": text("Markt / Region", "Global")}, ["watch_topic"]), approval_summary="Handeln, weiter untersuchen, beobachten oder archivieren. Ohne Quellen werden Evidenzlücken benannt."),
]


def organization(agents) -> Organization:
    nodes = [OrganizationNode(id="amancio", kind="human", display_name="Amancio", role="Founder / Owner", mission="Richtung setzen und konsequenzielle Entscheidungen verantworten.")]
    for agent in agents.load().values():
        nodes.append(OrganizationNode(id=agent.id, kind="agent", display_name=agent.name, role=agent.role, mission=agent.mission, parent_id="amancio", department_ids=[d.id for d in DEPARTMENTS if agent.id in d.member_ids]))
    result = Organization(nodes=nodes, departments=DEPARTMENTS)
    validate_organization(result)
    return result


def validate_organization(value: Organization):
    nodes = {n.id: n for n in value.nodes}
    if len(nodes) != len(value.nodes):
        raise ValueError("Duplicate organization identities")
    departments = {d.id for d in value.departments}
    if len(departments) != len(value.departments):
        raise ValueError("Duplicate department identities")
    for node in value.nodes:
        seen = {node.id}
        parent = node.parent_id
        while parent:
            if parent not in nodes or parent in seen:
                raise ValueError("Unresolved or cyclic reporting relationship")
            seen.add(parent)
            parent = nodes[parent].parent_id
        if not set(node.department_ids) <= departments:
            raise ValueError("Unresolved department reference")
    for department in value.departments:
        if any(member not in nodes or nodes[member].kind != "agent" for member in department.member_ids):
            raise ValueError("Unresolved department membership")
