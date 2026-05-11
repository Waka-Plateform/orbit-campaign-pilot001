from fastapi import APIRouter, Response
from html import escape
from app.storage.cosmos import get_campaign

router = APIRouter(prefix="/api/console", tags=["console-main"])


@router.get("/main")
async def main():
    c = await get_campaign()
    campaign_id = c.get("campaign_id")
    return {
        "campaign_id": campaign_id,
        "name": c.get("name"),
        "status": c.get("status"),
        "objective": c.get("scope_brief", {}).get("objective"),
        "flow_svg_url": "/api/console/main/flow.svg",
        "channels": c.get("channels", {}),
    }


@router.get("/main/flow.svg")
async def flow_svg():
    c = await get_campaign()
    flow = c.get("scope_brief", {}).get("flow_graph") or c.get("flow", {}) or {}
    nodes = flow.get("nodes", []) if isinstance(flow, dict) else []
    edges = flow.get("edges", []) if isinstance(flow, dict) else []
    if not nodes:
        nodes = [
            {"id": "A", "type": "send_email_template", "label": "Email CGV"},
            {"id": "W1", "type": "wait", "label": "Attente 24h"},
            {"id": "C1", "type": "condition", "label": "Email rejeté ?"},
            {"id": "B", "type": "send_sms_template", "label": "SMS secours"},
            {"id": "END", "type": "end", "label": "Fin"},
        ]
    node_by_id = {str(n.get("id")): n for n in nodes}
    width = max(720, 170 * len(nodes) + 80)
    height = 220
    positions = {str(n.get("id")): (60 + i * 170, 80) for i, n in enumerate(nodes)}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Flow campagne">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#E8832A" /></marker></defs>',
        '<rect width="100%" height="100%" fill="#fff7f0"/>',
    ]
    if edges:
        iterable_edges = edges
    else:
        ids = [str(n.get("id")) for n in nodes]
        iterable_edges = [{"from": ids[i], "to": ids[i + 1]} for i in range(len(ids) - 1)]
    for e in iterable_edges:
        source = str(e.get("from") or e.get("source") or e.get("start") or "")
        target = str(e.get("to") or e.get("target") or e.get("end") or "")
        if source in positions and target in positions:
            x1, y1 = positions[source]
            x2, y2 = positions[target]
            parts.append(f'<line x1="{x1 + 120}" y1="{y1 + 30}" x2="{x2}" y2="{y2 + 30}" stroke="#E8832A" stroke-width="3" marker-end="url(#arrow)"/>')
    for node_id, (x, y) in positions.items():
        n = node_by_id.get(node_id, {"id": node_id})
        label = escape(str(n.get("label") or n.get("name") or node_id))
        kind = escape(str(n.get("type") or "step"))
        parts.append(f'<g data-node-id="{escape(node_id)}"><rect x="{x}" y="{y}" rx="14" ry="14" width="120" height="60" fill="#ffffff" stroke="#E8832A" stroke-width="2"/><text x="{x + 60}" y="{y + 27}" text-anchor="middle" font-family="Arial" font-size="13" font-weight="700" fill="#222">{label}</text><text x="{x + 60}" y="{y + 45}" text-anchor="middle" font-family="Arial" font-size="10" fill="#666">{kind}</text></g>')
    parts.append("</svg>")
    return Response("".join(parts), media_type="image/svg+xml")
