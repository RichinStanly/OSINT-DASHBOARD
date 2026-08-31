"""
Report export.

Produces investigation exports in JSON, CSV (as a zip of tables), and
Markdown. PDF export is attempted via reportlab if installed; if not
available, PDF export is gracefully skipped and the UI is told so —
the app never crashes over a missing optional dependency.
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from datetime import datetime


def export_json(investigation: dict, sources: list[dict], entities: list[dict],
                 relationships: list[dict], events: list[dict], topics: list[dict],
                 report: dict | None) -> bytes:
    """Export the full investigation as a single structured JSON document."""
    payload = {
        "investigation": _json_safe(investigation),
        "sources": [_json_safe(s) for s in sources],
        "entities": [_json_safe(e) for e in entities],
        "relationships": [_json_safe(r) for r in relationships],
        "timeline_events": [_json_safe(ev) for ev in events],
        "topics": [_json_safe(t) for t in topics],
        "report": _json_safe(report) if report else None,
        "exported_at": datetime.utcnow().isoformat(),
    }
    return json.dumps(payload, indent=2, default=str).encode("utf-8")


def _json_safe(obj: dict) -> dict:
    safe = {}
    for k, v in obj.items():
        if isinstance(v, datetime):
            safe[k] = v.isoformat()
        else:
            safe[k] = v
    return safe


def export_csv_bundle(sources: list[dict], entities: list[dict],
                       relationships: list[dict], events: list[dict],
                       topics: list[dict]) -> bytes:
    """Export all tables as CSVs bundled into a single zip archive."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("sources.csv", _rows_to_csv(sources))
        zf.writestr("entities.csv", _rows_to_csv(entities))
        zf.writestr("relationships.csv", _rows_to_csv(relationships))
        zf.writestr("timeline_events.csv", _rows_to_csv(events))
        zf.writestr("topics.csv", _rows_to_csv(topics))
    return buffer.getvalue()


def _rows_to_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    output = io.StringIO()
    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        clean_row = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in row.items()}
        writer.writerow(clean_row)
    return output.getvalue()


def export_markdown(investigation: dict, sources: list[dict], entities: list[dict],
                     relationships: list[dict], events: list[dict], topics: list[dict],
                     report: dict | None) -> str:
    """Export a human-readable Markdown research report."""
    lines = []
    lines.append(f"# Research Report: {investigation['name']}")
    lines.append("")
    lines.append(f"**Subject:** {investigation['subject']}  ")
    lines.append(f"**Research depth:** {investigation['depth']}  ")
    lines.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ")
    if investigation.get("is_demo"):
        lines.append("**⚠ DEMO DATA** — this investigation uses sample data, not live research.  ")
    lines.append("")

    if report:
        lines.append("## Executive Summary")
        lines.append(report.get("executive_summary", "_Not available._"))
        lines.append("")

        lines.append("## Key Findings")
        for item in json.loads(report.get("key_findings") or "[]"):
            lines.append(f"- {item}")
        lines.append("")

        lines.append("## Major Events")
        for item in json.loads(report.get("major_events") or "[]"):
            lines.append(f"- {item}")
        lines.append("")

        lines.append("## Relationships")
        for item in json.loads(report.get("relationships_summary") or "[]"):
            lines.append(f"- {item}")
        lines.append("")

        lines.append("## Emerging Themes")
        for item in json.loads(report.get("emerging_themes") or "[]"):
            lines.append(f"- {item}")
        lines.append("")

        lines.append("## Source Notes")
        lines.append(report.get("source_notes", ""))
        lines.append("")

        lines.append("## Limitations")
        lines.append(report.get("limitations", ""))
        lines.append("")

    lines.append("## Key Entities")
    lines.append("")
    lines.append("| Entity | Type | Mentions |")
    lines.append("|---|---|---|")
    for e in entities[:30]:
        lines.append(f"| {e['name']} | {e['entity_type']} | {e['frequency']} |")
    lines.append("")

    lines.append("## Sources")
    lines.append("")
    for s in sources:
        pub = s.get("published_at")
        pub_str = pub.strftime("%Y-%m-%d") if isinstance(pub, datetime) else "Unknown date"
        lines.append(f"- [{s['title']}]({s['url']}) — {s['domain']} ({s['source_type']}, {pub_str})")
    lines.append("")

    return "\n".join(lines)


def export_pdf(markdown_text: str, title: str) -> bytes | None:
    """Attempt to render a simple PDF report from the markdown text.

    Returns None if reportlab is not installed — PDF export is an
    optional convenience, not a hard requirement.
    """
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.enums import TA_LEFT
    except ImportError:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=LETTER,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14, alignment=TA_LEFT)
    h1_style = styles["Heading1"]
    h2_style = styles["Heading2"]

    story = []
    for raw_line in markdown_text.split("\n"):
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 8))
            continue
        escaped = (
            line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        if line.startswith("# "):
            story.append(Paragraph(escaped[2:], h1_style))
        elif line.startswith("## "):
            story.append(Paragraph(escaped[3:], h2_style))
        elif line.startswith("- "):
            story.append(Paragraph(f"• {escaped[2:]}", body_style))
        else:
            story.append(Paragraph(escaped, body_style))

    doc.build(story)
    return buffer.getvalue()
