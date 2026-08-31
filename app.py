"""
OSINT Research Dashboard — main Streamlit application.

Run with: streamlit run app.py
"""
from __future__ import annotations

import json

import streamlit as st

from config.settings import settings
from core import database as db
from core import pipeline
from core.schemas import ResearchRequest
from reports import exporter
from ui import components
from ui.styles import inject_custom_css
from visualization import charts, graph, timeline as timeline_viz

st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()
db.init_db()

                                                                       
                              
                                                                       
if "active_investigation_id" not in st.session_state:
    st.session_state.active_investigation_id = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


def set_active_investigation(investigation_id: int | None) -> None:
    st.session_state.active_investigation_id = investigation_id


                                                                       
                                                
                                                                       
with st.sidebar:
    st.markdown("## 🛰️ OSINT Dashboard")
    st.caption(f"v{settings.APP_VERSION} · Educational research tool")

    st.markdown("---")
    st.markdown("### New Investigation")
    with st.form("new_investigation_form", clear_on_submit=True):
        subject_input = st.text_input("Research subject", placeholder="e.g. a public company or project")
        depth_input = st.selectbox("Research depth", ["quick", "standard", "deep"], index=1)
        demo_mode = st.checkbox("Use demo mode (no network required)", value=False)
        submitted = st.form_submit_button("Start Investigation", use_container_width=True)

    if submitted:
        if demo_mode:
            from core.demo_data import DEMO_SUBJECT

            inv_id = db.create_investigation(DEMO_SUBJECT, depth=depth_input, is_demo=True)
            pipeline.load_demo_investigation(inv_id)
            set_active_investigation(inv_id)
            st.session_state.page = "Dashboard"
            st.rerun()
        else:
            try:
                req = ResearchRequest(subject=subject_input, depth=depth_input)
                inv_id = db.create_investigation(req.subject, depth=req.depth, is_demo=False)
                set_active_investigation(inv_id)
                st.session_state.page = "Dashboard"
                st.session_state.trigger_research = inv_id
                st.rerun()
            except Exception as e:
                st.error(f"Invalid input: {e}")

    st.markdown("---")
    st.markdown("### Research History")
    investigations = db.list_investigations()

    if not investigations:
        st.caption("No investigations yet. Start one above.")
    else:
        for inv in investigations[:15]:
            is_active = inv["id"] == st.session_state.active_investigation_id
            label_prefix = "🟢 " if inv["status"] == "completed" else ("🟡 " if inv["status"] == "running" else "⚪ ")
            demo_suffix = " (demo)" if inv["is_demo"] else ""
            btn_label = f"{label_prefix}{inv['name']}{demo_suffix}"
            if st.button(btn_label, key=f"select_inv_{inv['id']}", use_container_width=True, type=("primary" if is_active else "secondary")):
                set_active_investigation(inv["id"])
                st.session_state.page = "Dashboard"
                st.rerun()

    if st.session_state.active_investigation_id:
        st.markdown("---")
        st.markdown("### Manage Investigation")
        current = db.get_investigation(st.session_state.active_investigation_id)
        if current:
            new_name = st.text_input("Rename", value=current["name"], key="rename_input")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Save name", use_container_width=True):
                    db.rename_investigation(current["id"], new_name)
                    st.rerun()
            with col_b:
                if st.button("Delete", use_container_width=True):
                    db.delete_investigation(current["id"])
                    set_active_investigation(None)
                    st.rerun()

    st.markdown("---")
    st.markdown("### Navigate")
    nav_options = [
        "Dashboard", "Sources", "Entity Explorer", "Relationship Graph",
        "Timeline", "Topics", "Research Summary", "Export",
    ]
    for opt in nav_options:
        if st.button(opt, key=f"nav_{opt}", use_container_width=True,
                     type=("primary" if st.session_state.page == opt else "secondary")):
            st.session_state.page = opt
            st.rerun()


                                                                       
                                                  
                                                                       
if st.session_state.get("trigger_research"):
    inv_id = st.session_state.pop("trigger_research")
    inv = db.get_investigation(inv_id)
    if inv:
        st.markdown(f"## Researching: {inv['subject']}")
        progress_bar = st.progress(0.0)
        status_text = st.empty()

        def _on_progress(message: str, fraction: float) -> None:
            progress_bar.progress(min(1.0, fraction))
            status_text.info(message)

        try:
            pipeline.run_research(inv_id, inv["subject"], inv["depth"], progress_callback=_on_progress)
            st.success("Research completed.")
        except Exception:
                                                                      
                                                                          
                                                                      
                                                                         
                                                                        
                                                            
            pass
        st.rerun()


                                                                       
              
                                                                       
active_id = st.session_state.active_investigation_id

if active_id is None:
    st.title("🛰️ OSINT Research Dashboard")
    st.markdown(
        "Enter a research subject in the sidebar to begin a new investigation, "
        "or select **Use demo mode** to explore the app instantly with a sample dataset "
        "and no network access required."
    )
    st.markdown("---")
    st.markdown("#### What this tool does")
    st.markdown(
        "- Collects publicly available information from Wikipedia, optional news APIs, and general web search\n"
        "- Extracts named entities, relationships, timeline events, and recurring topics\n"
        "- Scores source quality and highlights corroborated vs. uncertain claims\n"
        "- Builds an interactive relationship graph and chronological timeline\n"
        "- Generates a structured, source-traceable research summary\n"
        "- Exports investigations as JSON, CSV, Markdown, or PDF"
    )
    st.info(
        "This tool only collects **publicly available** information and respects robots.txt, "
        "rate limits, and site terms. It does not bypass authentication, CAPTCHAs, or access "
        "controls, and does not collect passwords or private data."
    )
else:
    investigation = db.get_investigation(active_id)
    if investigation is None:
        st.warning("Selected investigation no longer exists.")
        set_active_investigation(None)
        st.stop()

    sources = db.get_sources(active_id)
    entities = db.get_entities(active_id)
    relationships = db.get_relationships(active_id)
    events = db.get_timeline_events(active_id)
    topics = db.get_topics(active_id)
    report = db.get_report(active_id)

    if investigation["is_demo"]:
        components.demo_banner()

    st.title(investigation["name"])
    st.caption(
        f"Subject: {investigation['subject']} · Depth: {investigation['depth']} · "
        f"Status: {investigation['status']}"
    )

    if investigation["status"] == "running":
        st.info("This investigation is still running. Refresh in a moment.")
    elif investigation["status"] == "failed":
        st.error(
            "This investigation failed to collect usable sources. This can happen if "
            "the subject is too obscure, network access is unavailable, or all "
            "sources were blocked/unreachable. Try demo mode to explore the app, "
            "or try a different subject."
        )

    page = st.session_state.page

                                                                       
               
                                                                       
    if page == "Dashboard":
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Sources", len(sources))
        col2.metric("Entities", len(entities))
        col3.metric("Relationships", len(relationships))
        col4.metric("Timeline Events", len(events))
        cov_score, cov_label = components.coverage_score(len(sources), len(entities), len(relationships))
        col5.metric("Research Coverage", f"{cov_score}%", help=cov_label)

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(charts.render_source_type_chart(sources), use_container_width=True)
        with c2:
            st.plotly_chart(charts.render_entity_type_chart(entities), use_container_width=True)

        if report:
            st.markdown("### Executive Summary")
            st.write(report["executive_summary"])

                                                                       
             
                                                                       
    elif page == "Sources":
        st.markdown("### Sources")
        if not sources:
            st.caption("No sources collected yet.")
        else:
            col_filter1, col_filter2 = st.columns([2, 2])
            with col_filter1:
                type_filter = st.multiselect(
                    "Filter by type",
                    options=sorted({s["source_type"] for s in sources}),
                    default=[],
                )
            with col_filter2:
                sort_by = st.selectbox("Sort by", ["Relevance", "Quality", "Domain"])

            filtered = [s for s in sources if not type_filter or s["source_type"] in type_filter]
            if sort_by == "Relevance":
                filtered.sort(key=lambda s: s["relevance_score"], reverse=True)
            elif sort_by == "Quality":
                filtered.sort(key=lambda s: s["quality_score"], reverse=True)
            else:
                filtered.sort(key=lambda s: s["domain"])

            st.caption(f"Showing {len(filtered)} of {len(sources)} sources")
            for s in filtered:
                components.render_source_card(s)

            st.markdown("---")
            st.plotly_chart(charts.render_source_quality_chart(sources), use_container_width=True)

                                                                       
                     
                                                                       
    elif page == "Entity Explorer":
        st.markdown("### Entity Explorer")
        if not entities:
            st.caption("No entities extracted yet.")
        else:
            type_options = sorted({e["entity_type"] for e in entities})
            selected_types = st.multiselect("Filter by entity type", options=type_options, default=[])
            filtered_entities = [e for e in entities if not selected_types or e["entity_type"] in selected_types]

            st.caption(f"Showing {len(filtered_entities)} of {len(entities)} entities")
            source_by_id = {s["id"]: s for s in sources}
            for e in filtered_entities:
                src_ids = [int(x) for x in e["source_ids"].split(",") if x]
                components.render_entity_row(e, len(src_ids))
                                                                       
                                                                          
                                                                      
                                                                          
                                                                        
                                                                        
                unique_suffix = "".join("\u200c" if bit == "1" else "\u200b" for bit in format(int(e["id"]), "b"))
                with st.expander(f"Sources mentioning \"{e['name']}\"{unique_suffix}"):
                    for sid in src_ids:
                        src = source_by_id.get(sid)
                        if src:
                            st.markdown(f"- [{src['title']}]({src['url']}) ({src['domain']})")

                                                                       
                        
                                                                       
    elif page == "Relationship Graph":
        st.markdown("### Relationship Graph")
        st.caption(
            "Node size reflects mention frequency. Edge color reflects confidence: "
            "green = confirmed (co-occurs across multiple sources), "
            "yellow = inferred (single-source sentence co-occurrence), "
            "gray = uncertain (document-level co-occurrence only)."
        )
        fig = graph.render_graph_figure(entities, relationships)
        st.plotly_chart(fig, use_container_width=True)

        if relationships:
            st.markdown("### Explore a relationship")
            entity_names = sorted({r["source_entity"] for r in relationships} | {r["target_entity"] for r in relationships})
            selected_entity = st.selectbox("Select an entity to see its relationships and sources", entity_names)
            if selected_entity:
                related = [
                    r for r in relationships
                    if r["source_entity"] == selected_entity or r["target_entity"] == selected_entity
                ]
                source_by_id = {s["id"]: s for s in sources}
                for r in related:
                    other = r["target_entity"] if r["source_entity"] == selected_entity else r["source_entity"]
                    st.markdown(
                        f"**{selected_entity}** → **{other}** "
                        f"({r['relationship_type']}) {components.confidence_badge(r['confidence'])}",
                        unsafe_allow_html=True,
                    )
                    evidence_ids = [int(x) for x in r["evidence_source_ids"].split(",") if x]
                    for sid in evidence_ids:
                        src = source_by_id.get(sid)
                        if src:
                            st.caption(f"↳ Evidence: [{src['title']}]({src['url']})")

                                                                       
              
                                                                       
    elif page == "Timeline":
        st.markdown("### Timeline")
        st.caption(
            "Confidence reflects date precision: green = exact date, "
            "yellow = month-level, gray = year-only mention."
        )
        fig = timeline_viz.render_timeline_figure(events)
        st.plotly_chart(fig, use_container_width=True)

        source_by_id = {s["id"]: s for s in sources}
        st.markdown("### Event Details")
        for ev in events:
            date_str = ev["event_date"].strftime("%Y-%m-%d") if ev["date_precision"] == "day" else (
                ev["event_date"].strftime("%Y-%m") if ev["date_precision"] == "month" else ev["event_date"].strftime("%Y")
            )
            src = source_by_id.get(ev["source_id"]) if ev["source_id"] else None
            st.markdown(
                f"**{date_str}** {components.confidence_badge(ev['confidence'])} — {ev['description']}",
                unsafe_allow_html=True,
            )
            if src:
                st.caption(f"Source: [{src['title']}]({src['url']})")
            st.markdown("")

                                                                       
            
                                                                       
    elif page == "Topics":
        st.markdown("### Topics & Themes")
        if not topics:
            st.caption("No topics identified yet.")
        else:
            st.plotly_chart(charts.render_topic_frequency_chart(topics), use_container_width=True)
            source_by_id = {s["id"]: s for s in sources}
            for t in topics:
                with st.container():
                    st.markdown(
                        f'<div class="osint-card"><b>{t["label"]}</b> '
                        f'<span class="muted-text">— {t["frequency"]} source(s)</span></div>',
                        unsafe_allow_html=True,
                    )
                    if t["related_entities"]:
                        st.caption("Related entities: " + t["related_entities"].replace(",", ", "))
                    src_ids = [int(x) for x in t["source_ids"].split(",") if x]
                                                                            
                                                                           
                                                                      
                                                                                 
                    unique_suffix = "".join("\u200c" if bit == "1" else "\u200b" for bit in format(int(t["id"]), "b"))
                    with st.expander(f"Related sources{unique_suffix}"):
                        for sid in src_ids:
                            src = source_by_id.get(sid)
                            if src:
                                st.markdown(f"- [{src['title']}]({src['url']})")

                                                                       
                      
                                                                       
    elif page == "Research Summary":
        st.markdown("### Research Summary")
        if not report:
            st.caption("No report generated yet.")
        else:
            st.markdown("#### Executive Summary")
            st.write(report["executive_summary"])

            st.markdown("#### Key Findings")
            for item in json.loads(report["key_findings"] or "[]"):
                st.markdown(f"- {item}")

            st.markdown("#### Important Entities")
            top_entities = entities[:10]
            for e in top_entities:
                st.markdown(f"- **{e['name']}** ({e['entity_type']}) — {e['frequency']} mention(s)")

            st.markdown("#### Major Events")
            for item in json.loads(report["major_events"] or "[]"):
                st.markdown(f"- {item}")

            st.markdown("#### Relationships")
            for item in json.loads(report["relationships_summary"] or "[]"):
                st.markdown(f"- {item}")

            st.markdown("#### Emerging Themes")
            for item in json.loads(report["emerging_themes"] or "[]"):
                st.markdown(f"- {item}")

            st.markdown("#### Source Notes")
            st.write(report["source_notes"])

            st.markdown("#### Limitations")
            st.warning(report["limitations"])

                                                                       
            
                                                                       
    elif page == "Export":
        st.markdown("### Export Investigation")
        st.caption("Download this investigation's data and generated report in your preferred format.")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            json_bytes = exporter.export_json(investigation, sources, entities, relationships, events, topics, report)
            st.download_button(
                "Download JSON", data=json_bytes,
                file_name=f"investigation_{active_id}.json", mime="application/json",
                use_container_width=True,
            )

        with col2:
            csv_bytes = exporter.export_csv_bundle(sources, entities, relationships, events, topics)
            st.download_button(
                "Download CSV bundle", data=csv_bytes,
                file_name=f"investigation_{active_id}_csv.zip", mime="application/zip",
                use_container_width=True,
            )

        markdown_text = exporter.export_markdown(investigation, sources, entities, relationships, events, topics, report)
        with col3:
            st.download_button(
                "Download Markdown", data=markdown_text.encode("utf-8"),
                file_name=f"investigation_{active_id}.md", mime="text/markdown",
                use_container_width=True,
            )

        with col4:
            pdf_bytes = exporter.export_pdf(markdown_text, investigation["name"])
            if pdf_bytes:
                st.download_button(
                    "Download PDF", data=pdf_bytes,
                    file_name=f"investigation_{active_id}.pdf", mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.button("PDF unavailable", disabled=True, use_container_width=True,
                           help="Install 'reportlab' to enable PDF export.")

        st.markdown("---")
        st.markdown("### Markdown Preview")
        st.markdown(markdown_text)
