# SailabAlert — Project Memory

> **"Sailab"** (سیلاب) means *flood* in Urdu.
> SailabAlert is a flood and landslide early warning system for Pakistan.

---

## Project Overview

| Field | Detail |
|---|---|
| **Project Name** | SailabAlert |
| **Type** | Early Warning System |
| **Domain** | Disaster Risk Reduction / Geospatial / IoT |
| **Target Country** | Pakistan |
| **Hazards Covered** | Floods, Landslides |
| **Created** | 2026-09-05 |
| **Last Updated** | 2026-09-05 |

---

## Mission

Provide timely, reliable, and accessible flood and landslide early warnings to communities, emergency responders, and authorities across Pakistan — reducing loss of life and property through data-driven alerts.

---

## Key Stakeholders

- Affected communities (rural & urban, Urdu/local-language users)
- National Disaster Management Authority (NDMA)
- Provincial DMAs (PDMAs)
- Pakistan Meteorological Department (PMD)
- First responders and rescue services
- Development partners / NGOs

---

## Core Features (Planned / In Progress)

- [ ] Real-time river gauge and rainfall monitoring
- [ ] Landslide susceptibility mapping
- [ ] Multi-channel alert delivery (SMS, app push, web, sirens)
- [ ] Urdu-language interface and alerts
- [ ] Historical event archive and analytics dashboard
- [ ] Integration with PMD and NDMA data feeds
- [ ] Community-level risk scoring
- [ ] Offline-capable mobile app for low-connectivity areas

---

## Tech Stack (Confirmed)

| Layer | Technology |
|---|---|
| Frontend | Streamlit (Python) — Streamlit Community Cloud (free tier) |
| ML | scikit-learn — Random Forest Classifier |
| AI Agent | Groq API (`llama-3.3-70b-versatile`, console.groq.com, OpenAI-compatible) |
| Visualization | Plotly (charts) + Folium (interactive map) |
| Data | Synthetic dataset (see model.py); real datasets future scope |
| Hosting / Cloud | Streamlit Community Cloud (free tier) |

---

## Architecture Notes

*(To be filled as the system design evolves.)*

---

## Data Sources

- Pakistan Meteorological Department (PMD) — rainfall, forecasts
- NDMA / PDMAs — flood zone maps, historical data
- NASA GSFC / USGS — satellite rainfall estimates (GPM, MODIS)
- River gauge networks (WAPDA, IRSA)
- UN OCHA — humanitarian shapefiles for Pakistan

---

## Geographic Scope

High-priority regions for Pakistan flood and landslide risk:

- **Khyber Pakhtunkhwa (KP)** — flash floods, landslides (Swat, Chitral, Dir)
- **Balochistan** — flash floods (Quetta, Lasbela, Jhal Magsi)
- **Sindh** — riverine flooding (Indus floodplain)
- **Punjab** — Chenab, Jhelum, Ravi river systems
- **Gilgit-Baltistan** — glacial lake outburst floods (GLOFs), landslides
- **Azad Kashmir** — landslides, flash floods

### Folium Map — Pinned Cities (confirmed)

| City | Province | Risk Context |
|---|---|---|
| Karachi | Sindh | Coastal flooding, urban flash floods |
| Lahore | Punjab | Ravi river flooding |
| Peshawar | KPK | Flash floods, Kabul river |
| Multan | Punjab | Chenab/Sutlej river flooding |
| Sialkot | Punjab | Chenab river, flash floods |
| Sukkur | Sindh | Indus river — major flood corridor |

---

## Key Decisions & Design Choices

| Date | Decision | Rationale |
|---|---|---|
| 2026-09-05 | Deployment: Streamlit Community Cloud | Free, easy for CV/scholarship demo |
| 2026-09-05 | AI model: Groq `llama-3.3-70b-versatile` | Fast inference, free tier, OpenAI-compatible |
| 2026-09-05 | Urdu: test RTL in Streamlit; fall back to English-only if broken | Streamlit RTL support is limited; note as future scope if needed |
| 2026-09-05 | Map cities: Karachi, Lahore, Peshawar, Multan, Sialkot, Sukkur | Mix of river-adjacent and flood-prone cities |

---

## Open Questions

- Urdu RTL rendering in Streamlit — to be tested (may become future scope)
- Alert simulation UX design for Step 4

---

## Related Resources

- [NDMA Pakistan](https://ndma.gov.pk/)
- [Pakistan Meteorological Department](https://www.pmd.gov.pk/)
- [UN Sendai Framework for DRR](https://www.undrr.org/implementing-sendai-framework)
- [Global Flood Awareness System (GloFAS)](https://global-flood.emergency.copernicus.eu/)
- [NASA GPM Rainfall Data](https://gpm.nasa.gov/)
- [Groq API Docs](https://console.groq.com/docs)
- [Streamlit Community Cloud](https://streamlit.io/cloud)

---

## Changelog

| Date | Entry |
|---|---|
| 2026-09-05 | Project memory file created. Project initialized. |
| 2026-09-05 | Tech stack confirmed. Pinned cities added. Deployment target set. |
| 2026-09-05 | model.py created — synthetic data generation + Random Forest Classifier (Step 1). |
