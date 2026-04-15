"""
Generate the MNC Patrol Effort Technical Guide as a PDF using ReportLab.
Run with: python3 generate_technical_guide.py
Output: mnc_patrol_effort_technical_guide.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from datetime import date

OUTPUT_FILE = "mnc_patrol_effort_technical_guide.pdf"

# ── Colour palette ─────────────────────────────────────────────────────────────
GREEN_DARK  = colors.HexColor("#115631")
GREEN_MID   = colors.HexColor("#2d6a4f")
AMBER       = colors.HexColor("#e7a553")
SLATE       = colors.HexColor("#3d3d3d")
LIGHT_GREY  = colors.HexColor("#f5f5f5")
MID_GREY    = colors.HexColor("#cccccc")
WHITE       = colors.white

# ── Styles ─────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def _style(name, parent="Normal", **kw):
    s = ParagraphStyle(name, parent=styles[parent], **kw)
    styles.add(s)
    return s

TITLE    = _style("DocTitle",    fontSize=26, leading=32, textColor=GREEN_DARK,
                  spaceAfter=6,  alignment=TA_CENTER, fontName="Helvetica-Bold")
SUBTITLE = _style("DocSubtitle", fontSize=13, leading=18, textColor=SLATE,
                  spaceAfter=4,  alignment=TA_CENTER)
META     = _style("Meta",        fontSize=9,  leading=13, textColor=colors.grey,
                  alignment=TA_CENTER, spaceAfter=2)
H1       = _style("H1", fontSize=15, leading=20, textColor=GREEN_DARK,
                  spaceBefore=18, spaceAfter=6, fontName="Helvetica-Bold")
H2       = _style("H2", fontSize=12, leading=16, textColor=GREEN_MID,
                  spaceBefore=12, spaceAfter=4, fontName="Helvetica-Bold")
H3       = _style("H3", fontSize=10, leading=14, textColor=SLATE,
                  spaceBefore=8,  spaceAfter=3, fontName="Helvetica-Bold")
BODY     = _style("Body", fontSize=9, leading=14, textColor=SLATE,
                  spaceAfter=6, alignment=TA_JUSTIFY)
BULLET   = _style("BulletItem", fontSize=9, leading=14, textColor=SLATE,
                  spaceAfter=3, leftIndent=14, firstLineIndent=-10, bulletIndent=4)
CODE     = _style("InlineCode", fontSize=8, leading=12, fontName="Courier",
                  backColor=LIGHT_GREY, textColor=colors.HexColor("#c0392b"),
                  spaceAfter=4, leftIndent=10, rightIndent=10, borderPad=3)
NOTE     = _style("Note", fontSize=8.5, leading=13,
                  textColor=colors.HexColor("#555555"),
                  backColor=colors.HexColor("#fff8e1"),
                  leftIndent=10, rightIndent=10, spaceAfter=6, borderPad=4)


def hr():                return HRFlowable(width="100%", thickness=1, color=MID_GREY, spaceAfter=6)
def p(text, style=BODY): return Paragraph(text, style)
def h1(text):            return Paragraph(text, H1)
def h2(text):            return Paragraph(text, H2)
def h3(text):            return Paragraph(text, H3)
def sp(n=6):             return Spacer(1, n)
def bullet(text):        return Paragraph(f"• {text}", BULLET)
def note(text):          return Paragraph(f"<b>Note:</b> {text}", NOTE)

def c(text):
    return Paragraph(str(text), BODY)

def make_table(data, col_widths, header_row=True):
    wrapped = [[c(cell) if isinstance(cell, str) else cell for cell in row]
               for row in data]
    t = Table(wrapped, colWidths=col_widths, repeatRows=1 if header_row else 0)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0 if header_row else -1), GREEN_DARK),
        ("TEXTCOLOR",     (0, 0), (-1, 0 if header_row else -1), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0 if header_row else -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ("GRID",          (0, 0), (-1, -1), 0.4, MID_GREY),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
    ]))
    return t


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(A4[0] / 2, 1.5 * cm,
                             f"MNC Patrol Effort — Technical Guide  |  Page {doc.page}")
    canvas.restoreState()


# ── Document ───────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT_FILE,
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=2.5*cm,
)

W = A4[0] - 4*cm   # usable width

story = []

# ══════════════════════════════════════════════════════════════════════════════
# COVER
# ══════════════════════════════════════════════════════════════════════════════
story += [
    sp(60),
    p("MNC Patrol Effort", TITLE),
    p("Technical Guide", SUBTITLE),
    sp(4),
    p("Patrol trajectory mapping, effort summaries, and coverage analysis "
      "for Mara North Conservancy", SUBTITLE),
    sp(4),
    p(f"Generated {date.today().strftime('%B %d, %Y')}", META),
    p("Workflow id: <b>mnc_patrol_effort</b>", META),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 1. OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("1. Overview"),
    hr(),
    p("The <b>mnc_patrol_effort</b> workflow fetches <b>patrol_info</b> events "
      "and linked patrol observations from EarthRanger for a specified time "
      "window. It converts observations into relocations and trajectories, "
      "splits by transport type (foot, vehicle, motorbike), and produces "
      "per-type effort summaries, trajectory maps, and a combined patrol "
      "coverage grid."),
    sp(4),
    p("The workflow delivers:"),
    bullet("<b>total_events_recorded_by_date.csv</b> / "
           "<b>total_events_recorded_by_type.csv</b> — all event counts for "
           "the period"),
    bullet("<b>total_events_recorded.html/.png</b> — daily events line chart"),
    bullet("<b>patrol_purpose_summary.csv</b> — patrol count and distance by "
           "patrol purpose"),
    bullet("<b>patrol_relocations.geoparquet</b> — full observation dataset "
           "with patrol metadata"),
    bullet("<b>foot_patrol_efforts.csv</b> / <b>vehicle_patrol_efforts.csv</b> "
           "/ <b>motorbike_patrol_efforts.csv</b> — per-type effort summaries"),
    bullet("<b>foot_patrol_trajectories.geojson</b> / "
           "<b>vehicle_patrol_trajectories.geojson</b> / "
           "<b>motor_patrol_trajectories.geojson</b> — trajectory GeoJSON files"),
    bullet("<b>foot_patrols_map.html/.png</b> / <b>vehicle_patrols_map.html/.png</b> "
           "/ <b>motorbike_patrols_map.html/.png</b> — trajectory maps"),
    bullet("<b>patrol_trajectories.geoparquet</b> — merged trajectory dataset "
           "(foot + vehicle + motorbike)"),
    bullet("<b>overall_patrol_efforts.csv</b> — per-ranger summary"),
    bullet("<b>patrol_coverage_map.html/.png</b> — 1 000 m grid-cell visit "
           "density map"),
    bullet("<b>patrol_coverage.csv</b> — patrol occupancy percentage per "
           "conservancy region"),
    sp(6),
    h2("Output summary"),
    make_table(
        [
            ["Output file", "Description"],
            ["total_events_recorded_by_date.csv",
             "Daily event counts (all non-excluded types)"],
            ["total_events_recorded_by_type.csv",
             "Daily event counts broken down by event type"],
            ["total_events_recorded.html / .png",
             "Line chart of daily event totals"],
            ["patrol_purpose_summary.csv",
             "Patrol count and distance km grouped by patrol purpose"],
            ["patrol_relocations.geoparquet",
             "All patrol observations with full patrol metadata"],
            ["foot_patrol_efforts.csv",
             "Foot patrol metrics: count, distance, duration, average speed"],
            ["foot_patrol_trajectories.geojson",
             "Foot patrol trajectory line geometries (filtered columns)"],
            ["foot_patrols_map.html / .png",
             "Foot trajectory map coloured by patrol type"],
            ["vehicle_patrol_efforts.csv",
             "Vehicle patrol metrics: count, distance, duration, average speed"],
            ["vehicle_patrol_trajectories.geojson",
             "Vehicle patrol trajectory line geometries (filtered columns)"],
            ["vehicle_patrols_map.html / .png",
             "Vehicle trajectory map coloured by patrol type"],
            ["motorbike_patrol_efforts.csv",
             "Motorbike patrol metrics: count, distance, duration, average speed"],
            ["motor_patrol_trajectories.geojson",
             "Motorbike patrol trajectory line geometries (filtered columns)"],
            ["motorbike_patrols_map.html / .png",
             "Motorbike trajectory map coloured by patrol type"],
            ["patrol_trajectories.geoparquet",
             "Merged foot + vehicle + motorbike trajectories"],
            ["overall_patrol_efforts.csv",
             "Per-ranger patrol count, distance km, duration hrs"],
            ["patrol_coverage_map.html / .png",
             "Grid-cell visit density map (RdYlGn_r, equal-interval 5 bins)"],
            ["patrol_coverage.csv",
             "Patrol occupancy percentage per conservancy region"],
        ],
        [6*cm, W - 6*cm],
    ),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 2. DEPENDENCIES
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("2. Dependencies"),
    hr(),
    h2("2.1  Python packages"),
    make_table(
        [
            ["Package", "Version", "Channel"],
            ["ecoscope-workflows-core",        "0.22.17.*", "ecoscope-workflows"],
            ["ecoscope-workflows-ext-ecoscope","0.22.17.*", "ecoscope-workflows"],
            ["ecoscope-workflows-ext-custom",  "0.0.45.*",  "ecoscope-workflows-custom"],
            ["ecoscope-workflows-ext-ste",     "0.0.19.*",  "ecoscope-workflows-custom"],
            ["ecoscope-workflows-ext-mep",     "0.0.14.*",  "ecoscope-workflows-custom"],
            ["ecoscope-workflows-ext-mnc",     "0.0.8.*",   "ecoscope-workflows-custom"],
        ],
        [6.5*cm, 3*cm, W - 9.5*cm],
    ),
    sp(6),
    h2("2.2  Connections"),
    make_table(
        [
            ["Connection", "Task", "Purpose"],
            ["EarthRanger", "set_er_connection",
             "Fetch event records and patrol observations; passed to "
             "get_events, get_patrol_values, and "
             "custom_get_patrol_observations_from_patrols_df."],
            ["Dropbox (HTTP)", "fetch_and_persist_file",
             "Download MNC community conservancy boundary gpkg and MNC "
             "parcels gpkg. Downloads are skipped if the file already "
             "exists (overwrite_existing: false)."],
        ],
        [3.5*cm, 4.5*cm, W - 8*cm],
    ),
    sp(6),
    h2("2.3  Grouper"),
    p("The workflow uses an <b>empty grouper list</b> (groupers: []). "
      "All data are processed as a single undivided dataset. The grouper "
      "is threaded through temporal-index steps and the dashboard only — "
      "it produces no fan-out branching."),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 3. GEOSPATIAL ASSET PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("3. Geospatial Asset Pipeline"),
    hr(),
    p("Before any event data is fetched, the workflow downloads and prepares "
      "two GeoPackage boundary files used as background layers on all maps. "
      "These assets are shared across the foot, vehicle, motorbike, and "
      "coverage map sections."),
    sp(6),
    h2("3.1  MNC community conservancy boundary"),
    make_table(
        [
            ["Step", "Task / id", "Detail"],
            ["1", "fetch_and_persist_file\npersist_mnc_gpkg",
             "Download mnc_conservancy.gpkg from Dropbox. "
             "overwrite_existing: false — skipped on subsequent runs if "
             "the file is already present."],
            ["2", "load_df\nload_comm_shp",
             "Load the GeoPackage into a GeoDataFrame."],
            ["3", "split_gdf_by_column\nsplit_gdf_by_zone",
             "Split the loaded GDF into a dict keyed by the "
             "<b>grazing_zone</b> column value."],
            ["4", "ecoscope_workflows_ext_ste.tasks.annotate_gdf_dict_with_geom_type\n"
             "annotate_comm_gdf_dict",
             "Annotate each sub-GDF in the dict with its geometry type."],
            ["5", "create_deckgl_layers_from_gdf_dict\ncreate_mnc_styled_layers",
             "Build styled DeckGL layers for Conservancy, Conservancy Herd Zone, "
             "and Grazing Zones 1–4 with distinct fill colours."],
            ["6", "create_deckgl_layers_from_gdf_dict\ncreate_conservancy_boundaries",
             "Build a boundary-only layer (grey outline, no fill) used as a "
             "clean boundary overlay on all patrol maps."],
            ["7", "create_gdf_from_dict\nconservancy_gdf",
             "Extract the 'Conservancy' sub-GDF for use in the "
             "coverage occupancy calculation and text label."],
            ["8", "filter_df\noverall_grazing_zones",
             "Filter to rows where grazing_zone ≠ 'Conservancy' — "
             "the grazing zone polygons used to compute the global map zoom."],
            ["9", "create_custom_text_layer\nconservancy_text_layer",
             "Build a text label layer centred on each conservancy polygon "
             "(Calibri Bold, size 1 500 m, min 70 px)."],
        ],
        [0.5*cm, 4*cm, W - 4.5*cm],
    ),
    sp(6),
    h2("3.2  MNC parcels"),
    make_table(
        [
            ["Step", "Task / id", "Detail"],
            ["1", "fetch_and_persist_file\ndownload_mnc_parcels",
             "Download mnc_across_the_river_parcels.gpkg from Dropbox."],
            ["2", "load_df\nload_mnc_parcels",
             "Load the parcels GeoPackage."],
            ["3", "ecoscope_workflows_ext_ste.tasks.get_gdf_geom_type\n"
             "assign_mnc_geom",
             "Assign the geometry type to the parcels GDF."],
            ["4", "create_deckgl_layer_from_gdf\ncreate_mnc_parcels_layers",
             "Build a styled layer: dark-khaki fill (#bdb76b), opacity 0.15, "
             "labelled 'Parcels' in the legend."],
        ],
        [0.5*cm, 4*cm, W - 4.5*cm],
    ),
    sp(6),
    h2("3.3  Global map view state"),
    p("The task <b>view_state_deck_gdf</b> (id: <b>global_zoom_value</b>) "
      "computes a zoom level and centre point from the "
      "<b>overall_grazing_zones</b> GDF (grazing zone polygons only, "
      "pitch: 0, bearing: 0). This view state is reused unchanged "
      "for all patrol maps and the coverage map."),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 4. EVENT INGESTION PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("4. Event Ingestion Pipeline"),
    hr(),
    p("A single <b>get_events</b> call fetches all event types for the analysis "
      "period. The resulting DataFrame is used in two parallel branches: the "
      "events summary charts/tables (Section 5) and the patrol info / "
      "observations pipeline (Sections 6–11)."),
    sp(6),
    h2("4.1  Event retrieval"),
    make_table(
        [
            ["Parameter", "Value"],
            ["Task",             "get_events (id: get_events_data)"],
            ["event_types",      "[] — all event types are fetched"],
            ["Columns retained", "id, time, event_type, event_category, "
                                 "reported_by, serial_number, geometry, "
                                 "created_at, event_details, patrols"],
            ["include_details",      "true"],
            ["include_display_values", "false"],
            ["raise_on_empty",        "true"],
            ["include_null_geometry", "false"],
            ["include_updates",           "false"],
            ["include_related_events",    "false"],
        ],
        [5*cm, W - 5*cm],
    ),
    note("All event types are retrieved together in a single call. Downstream "
         "filter_df steps isolate the specific event types needed by each "
         "branch (patrol_info for the observations pipeline; all others for "
         "the events summary)."),
    sp(6),
    h2("4.2  Date extraction and temporal indexing"),
    make_table(
        [
            ["Step", "Task", "Detail"],
            ["1", "extract_column_as_type\nextract_event_date",
             "Extract the <b>time</b> column as <b>output_type: date</b>, "
             "writing the result into a new <b>date</b> column."],
            ["2", "add_temporal_index\nevents_temporal",
             "Add a temporal index keyed on the <b>date</b> column, "
             "using the empty grouper list. "
             "cast_to_datetime: true, format: mixed."],
        ],
        [0.5*cm, 4*cm, W - 4.5*cm],
    ),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 5. EVENTS SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("5. Events Summary"),
    hr(),
    p("This branch works from <b>events_temporal</b> and produces three output "
      "files summarising all events recorded in the period, excluding a small "
      "set of specialised event types."),
    sp(6),
    h2("5.1  Event type exclusion"),
    p("The task <b>exclude_row_values</b> (id: <b>filter_events</b>) removes "
      "rows where <b>event_type</b> is any of:"),
    bullet("distancecountwildlife_rep"),
    bullet("distancecountpatrol_rep"),
    bullet("airstrip_operations"),
    bullet("silence_source_rep"),
    note("These four types are handled by dedicated workflows "
         "(wildlife distance count, logistics) and are excluded here to "
         "avoid double-counting in the events summary."),
    sp(6),
    h2("5.2  Summaries and chart"),
    make_table(
        [
            ["Output", "Task / id", "Logic"],
            ["total_events_recorded_by_date.csv",
             "summarize_df\ntotal_events_recorded\n→ add_totals_row\nadd_total_events_row\n→ persist_df\npersist_tevents_df",
             "Group by <b>date</b>, count unique <b>id</b> → <b>no_of_events</b>. "
             "Add a 'Total' row. Persist as CSV."],
            ["total_events_recorded_by_type.csv",
             "summarize_df\ntotal_events_type_recorded\n→ persist_df\npersist_summary_event_type",
             "Group by <b>date</b> and <b>event_type</b>, count unique <b>id</b> "
             "→ <b>no_of_events</b>. Persist as CSV."],
            ["total_events_recorded.html / .png",
             "draw_line_chart\ndraw_events_chart\n→ persist_text\npersist_total_events\n→ html_to_png\nconvert_tevents_png",
             "Line chart: x = date, y = no_of_events, colour = lightsteelblue, "
             "no legend. device_scale_factor: 2.0, full_page: false."],
        ],
        [3.5*cm, 3.5*cm, W - 7*cm],
    ),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 6. PATROL PURPOSE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("6. Patrol Purpose Summary"),
    hr(),
    p("This branch isolates <b>patrol_info</b> events from "
      "<b>events_temporal</b>, flattens their event details, and produces a "
      "per-purpose summary table."),
    sp(6),
    make_table(
        [
            ["Step", "Task / id", "Detail"],
            ["1", "filter_df\nfilter_patrol_info_events",
             "Keep rows where event_type = 'patrol_info'."],
            ["2", "normalize_json_column\nnormalize_pi_values",
             "Flatten the <b>event_details</b> JSON column "
             "(skip_if_not_exists: true, sort_columns: true)."],
            ["3", "map_columns\nrename_patrol_info",
             "Rename flattened columns:\n"
             "event_details__patrolinfomation_participants → participants\n"
             "event_details__patrolinfomation_patrolpurpose → purpose\n"
             "event_details__patrolinfomation_personwhoauthorised → authorized_by\n"
             "event_details__patrolinfomation_transporttype → transport_type\n"
             "patrols → patrol_id"],
            ["4", "summarize_df\npatrol_info_summary",
             "Group by <b>purpose</b>. Aggregate:\n"
             "no_of_patrols = nunique(id)\n"
             "distance_km = sum(dist_meters) converted m → km"],
            ["5", "capitalize_text\ncapitalize_patrol_text",
             "Capitalize the <b>purpose</b> column values."],
            ["6", "add_totals_row\ninclude_pat_totals",
             "Add a 'Total' row labelled by the <b>purpose</b> column."],
            ["7", "persist_df\npersist_patrol_df",
             "Write to <b>patrol_purpose_summary.csv</b>."],
        ],
        [0.5*cm, 3.5*cm, W - 4*cm],
    ),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 7. PATROL OBSERVATIONS PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("7. Patrol Observations Pipeline"),
    hr(),
    p("Starting from the renamed patrol info DataFrame (id: "
      "<b>rename_patrol_info</b>), this pipeline enriches, expands, and "
      "fetches patrol observation points from EarthRanger, merges them with "
      "patrol metadata, and converts them into relocations for trajectory "
      "building."),
    sp(6),
    h2("7.1  Participant name mapping and patrol ID preparation"),
    make_table(
        [
            ["Step", "Task / id", "Detail"],
            ["1", "map_name_values\nrename_participants",
             "Apply site-specific name normalisation to the "
             "<b>participants</b> column."],
            ["2", "filter_non_empty_values\nfilter_null_patrols",
             "Remove rows where <b>patrol_id</b> is null or empty."],
            ["3", "replace_missing_with_label\nreplace_transport_unspecified",
             "Fill null values in <b>transport_type</b> with 'unspecified'."],
            ["4", "explode_multiple_columns\nexplode_patrol_columns",
             "Explode both <b>patrol_id</b> and <b>participants</b> columns "
             "(each row may link to multiple patrol IDs and participants). "
             "reset_index: true."],
        ],
        [0.5*cm, 3.5*cm, W - 4*cm],
    ),
    sp(6),
    h2("7.2  Fetching patrols and observations"),
    make_table(
        [
            ["Step", "Task / id", "Detail"],
            ["1", "get_patrol_values\nget_patrols_from_info",
             "Look up patrol records in EarthRanger for each patrol ID "
             "found in the <b>patrol_id</b> column. batch_size: 15."],
            ["2", "custom_get_patrol_observations_from_patrols_df\nget_patrol_obs",
             "Fetch patrol observation points for each patrol. "
             "include_patrol_details: true, raise_on_empty: true, "
             "sub_page_size: 150."],
        ],
        [0.5*cm, 3.5*cm, W - 4*cm],
    ),
    sp(6),
    h2("7.3  Merging patrol info and processing relocations"),
    make_table(
        [
            ["Step", "Task / id", "Detail"],
            ["1", "map_columns\ndrop_values_patrol_info",
             "From the exploded patrol info DataFrame, drop: geometry, "
             "reported_by, index, serial_number. Rename: "
             "authorized_by → authorized_by, event_details__updates → updates."],
            ["2", "merge_dataframes\nmerge_patrol_events_obs",
             "Left-join patrol observations (<b>get_patrol_obs</b>) with "
             "the cleaned patrol info (<b>drop_values_patrol_info</b>) on "
             "<b>patrol_id</b>. preserve_left_index: true."],
            ["3", "process_relocations\nobs_relocs",
             "Convert the merged observations to relocations, retaining: "
             "extra__id, extra__created_at, extra__subject_id, geometry, "
             "groupby_col, fixtime, junk_status, patrol_id, patrol_title, "
             "patrol_serial_number, patrol_start_time, patrol_end_time, "
             "patrol_type, patrol_status, patrol_subject, patrol_type__value, "
             "participants, purpose, transport_type. "
             "Filter sentinel coordinates: (180,90), (0,0), (1,1)."],
            ["4", "persist_df\npersist_relocs",
             "Write to <b>patrol_relocations.geoparquet</b>."],
        ],
        [0.5*cm, 3.5*cm, W - 4*cm],
    ),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 8. TRAJECTORY CONVERSION
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("8. Trajectory Conversion"),
    hr(),
    p("The relocations are split into three transport-type branches. Each "
      "branch converts relocations to trajectory segments using "
      "type-appropriate speed and distance filters, then adds a temporal "
      "index and renames columns."),
    sp(6),
    h2("8.1  Transport-type filtering"),
    make_table(
        [
            ["Branch", "Task / id", "Filter"],
            ["Foot",      "filter_df\nfilter_foot_patrols",
             "transport_type = 'foot'"],
            ["Vehicle",   "filter_df\nfilter_vehicle_patrols",
             "transport_type = 'vehicle'"],
            ["Motorbike", "filter_df\nfilter_motor_patrols",
             "transport_type = 'motorbike'"],
            ["Unspecified", "filter_df\nfilter_unspecified_patrols",
             "transport_type = 'unspecified' "
             "(retained for potential future use; not further processed)"],
        ],
        [2*cm, 3.5*cm, W - 5.5*cm],
    ),
    sp(6),
    h2("8.2  Trajectory segment filters"),
    make_table(
        [
            ["Parameter", "Foot", "Vehicle", "Motorbike"],
            ["min_length_meters",  "0.001",   "0.35",    "0.35"],
            ["max_length_meters",  "5 000",   "5 000",   "5 000"],
            ["max_time_secs",      "14 400",  "18 000",  "18 000"],
            ["min_time_secs",      "1",       "1",       "1"],
            ["max_speed_kmhr",     "9.0",     "100.0",   "100.0"],
            ["min_speed_kmhr",     "0.5",     "10.0",    "10.0"],
        ],
        [4*cm, (W - 4*cm)/3, (W - 4*cm)/3, (W - 4*cm)/3],
    ),
    note("Foot patrols use a tighter speed envelope (0.5–9 km/h) and shorter "
         "maximum duration (4 h vs 5 h) than vehicle and motorbike patrols, "
         "reflecting the expected pace of rangers on foot."),
    sp(6),
    h2("8.3  Temporal indexing and column renaming"),
    p("Each trajectory branch goes through two steps:"),
    make_table(
        [
            ["Step", "Task", "Detail"],
            ["1", "add_temporal_index\ntemporal_foot_traj / "
             "temporal_vehicle_traj / temporal_motor_traj",
             "Add temporal index on <b>segment_start</b> column. "
             "cast_to_datetime: true, format: mixed."],
            ["2", "map_columns\nrename_foot_trajs / rename_vehicle_trajs / "
             "rename_motor_trajs",
             "Drop: heading, extra__created_at, extra__id. "
             "Rename extra__* columns to clean names: "
             "patrol_start_time, patrol_end_time, patrol_id, "
             "patrol_serial_number, patrol_status, patrol_subject_name, "
             "patrol_title, patrol_type_id, patrol_type_value, subject_id."],
        ],
        [0.5*cm, 5*cm, W - 5.5*cm],
    ),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 9. PER-TYPE PATROL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("9. Per-Type Patrol Analysis"),
    hr(),
    p("Each of the three transport-type branches (foot, vehicle, motorbike) "
      "follows an identical pipeline structure: effort summary → colormap → "
      "column filter → GeoJSON → map layers → map render → HTML/PNG. "
      "The per-type colour column names differ between branches."),
    sp(6),
    h2("9.1  Effort summary"),
    make_table(
        [
            ["Step", "Task / id (foot example)", "Detail"],
            ["1", "summarize_df\nfoot_patrol_metrics",
             "Group by <b>patrol_type_value</b>. Aggregate:\n"
             "no_of_patrols = nunique(patrol_id)\n"
             "distance_km = sum(dist_meters) m → km\n"
             "duration_hrs = sum(timespan_seconds) s → h\n"
             "average_speed = mean(speed_kmhr)"],
            ["2", "add_totals_row\nadd_fp_metrics_totals",
             "Add a 'Total' row labelled by patrol_type_value."],
            ["3", "persist_df\npersist_foot_df",
             "Write to <b>foot_patrol_efforts.csv</b> "
             "(vehicle: vehicle_patrol_efforts.csv, "
             "motorbike: motorbike_patrol_efforts.csv)."],
        ],
        [0.5*cm, 3.5*cm, W - 4*cm],
    ),
    note("The same summarize_df / add_totals_row / persist_df pattern is "
         "applied identically to vehicle (ids: vehicle_patrol_metrics, "
         "add_vh_metrics_totals, persist_vehicle_df) and motorbike "
         "(motor_patrol_metrics, add_mb_metrics_totals, persist_motor_df)."),
    sp(6),
    h2("9.2  Colormap application and column filtering"),
    make_table(
        [
            ["Branch", "Task / id", "Input column", "Output column", "Colormap"],
            ["Foot",
             "apply_color_map\napply_footp_colormap",
             "patrol_type_value", "foot_patrol_colors", "tab20"],
            ["Vehicle",
             "apply_color_map\napply_vehicle_colormap",
             "patrol_type_value", "vehicle_patrol_colors", "tab20"],
            ["Motorbike",
             "apply_color_map\napply_motor_colormap",
             "patrol_type_value", "motor_patrol_colors", "tab20"],
        ],
        [2*cm, 3*cm, 3*cm, 3*cm, W - 11*cm],
    ),
    sp(4),
    p("After the colormap is applied, a <b>filter_columns</b> step retains "
      "only the columns needed for GeoJSON persistence, significantly reducing "
      "file size:"),
    make_table(
        [
            ["Branch", "Task / id", "Columns retained"],
            ["Foot",
             "filter_columns\nfilter_foot_trajs",
             "geometry, foot_patrol_colors, patrol_type_value"],
            ["Vehicle",
             "filter_columns\nfilter_vehicles_trajs",
             "geometry, vehicle_patrol_colors, patrol_type_value"],
            ["Motorbike",
             "filter_columns\nfilter_motor_trajs",
             "geometry, vehicle_patrol_colors, patrol_type_value"],
        ],
        [2*cm, 3*cm, W - 5*cm],
    ),
    note("The filter_columns task (exclude: null) keeps only the listed "
         "columns and drops everything else. The filtered DataFrame is the "
         "sole input to gdf_to_geojson; the full colormapped DataFrame "
         "is still passed to create_geojson_layer for legend and property "
         "lookups."),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 10. TRAJECTORY MAP PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("10. Trajectory Map Pipeline"),
    hr(),
    p("Each patrol type (foot, vehicle, motorbike) follows the same map "
      "pipeline after column filtering. The foot patrol pipeline is described "
      "here; vehicle and motorbike are identical except for the task IDs and "
      "colour column references."),
    sp(6),
    make_table(
        [
            ["Step", "Task / id (foot example)", "Detail"],
            ["1", "gdf_to_geojson\npersist_foot_geojson",
             "Persist the filtered trajectory GDF as "
             "<b>foot_patrol_trajectories.geojson</b>."],
            ["2", "create_geojson_layer\ngenerate_foot_layers",
             "Build a DeckGL GeoJSON layer. Colour source: "
             "properties.foot_patrol_colors. Line width 1.55 px, "
             "opacity 0.55. Legend: title = 'Patrol Type', "
             "label_column = patrol_type_value, "
             "color_column = foot_patrol_colors, sort: ascending. "
             "geodataframe = apply_footp_colormap.return (full dataset "
             "for legend enumeration), data_url = persist_foot_geojson.return."],
            ["3", "combine_deckgl_map_layers\ncombine_foot_layers",
             "Combine static layers (conservancy boundaries, parcels, text) "
             "with the foot trajectory group layer."],
            ["4", "draw_map\ndraw_foot_map",
             "Render the map using the ArcGIS hillshade tile layer, "
             "view state from global_zoom_value, max_zoom: 10, "
             "legend placement: bottom-right."],
            ["5", "rewrite_file_urls_for_screenshots\nrewrite_foot_patrol_urls",
             "Rewrite the GeoJSON file URL in the HTML so it can be "
             "resolved during headless screenshot rendering."],
            ["6", "persist_text\npersist_foot_urls",
             "Write the modified HTML to <b>foot_patrols_map.html</b>."],
            ["7", "html_to_png\nconvert_foot_png",
             "Render the HTML to <b>foot_patrols_map.png</b>. "
             "device_scale_factor: 2.0, wait_for_timeout: 40 000 ms, "
             "serve_local_files: true, full_page: false."],
        ],
        [0.5*cm, 4*cm, W - 4.5*cm],
    ),
    note("The serve_local_files: true flag on html_to_png is required because "
         "the GeoJSON data URL is a local file path. This flag is set on all "
         "three patrol map conversions."),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 11. COMBINED TRAJECTORIES AND OVERALL PATROL EFFORT
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("11. Combined Trajectories and Overall Patrol Effort"),
    hr(),
    p("After all three per-type trajectory branches complete, their raw "
      "trajectories (before column filtering) are merged into a single "
      "dataset for combined analysis."),
    sp(6),
    h2("11.1  Merging trajectories"),
    make_table(
        [
            ["Step", "Task / id", "Detail"],
            ["1", "ecoscope_workflows_ext_mnc.tasks.merge_multiple_df\nmerge_trajs",
             "Concatenate foot_trajs, vehicle_trajs, and motor_trajs "
             "(raw, pre-filter). ignore_index: true, sort: false."],
            ["2", "map_columns\nrename_combined_trajs",
             "Drop: heading, extra__created_at, extra__id. "
             "Rename extra__* columns to clean names (same mapping as "
             "per-type rename steps), plus "
             "extra__participants → participants."],
            ["3", "persist_df\npersist_trajectories_data",
             "Write merged trajectories to "
             "<b>patrol_trajectories.geoparquet</b>."],
        ],
        [0.5*cm, 4*cm, W - 4.5*cm],
    ),
    sp(6),
    h2("11.2  Overall patrol effort (per-ranger summary)"),
    make_table(
        [
            ["Step", "Task / id", "Detail"],
            ["1", "summarize_df\nranger_patrol_metrics",
             "Group by <b>participants</b>. Aggregate (2 d.p.):\n"
             "no_of_patrols = nunique(patrol_id) [0 d.p.]\n"
             "distance_km = sum(dist_meters) m → km [2 d.p.]\n"
             "duration_hrs = sum(timespan_seconds) s → h [2 d.p.]"],
            ["2", "replace_missing_with_label\nreplace_ranger_nulls",
             "Fill null values in <b>participants</b> with 'Unspecified'."],
            ["3", "add_totals_row\nadd_ranger_metrics_totals",
             "Add a 'Total' row labelled by participants."],
            ["4", "persist_df\npersist_total_df",
             "Write to <b>overall_patrol_efforts.csv</b>."],
        ],
        [0.5*cm, 3.5*cm, W - 4*cm],
    ),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 12. PATROL COVERAGE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("12. Patrol Coverage Analysis"),
    hr(),
    p("This section uses the combined renamed trajectories "
      "(<b>rename_combined_trajs</b>) to compute how uniformly rangers "
      "patrolled the conservancy during the period."),
    sp(6),
    make_table(
        [
            ["Step", "Task / id", "Detail"],
            ["1", "create_patrol_coverage_grid\npatrol_grid_visits",
             "Compute a 1 000 m square coverage grid. Each cell records "
             "<b>unique_patrol_count</b> — the number of distinct patrols "
             "that passed through it."],
            ["2", "apply_classification\napply_classification_grid",
             "Apply equal-interval classification to <b>unique_patrol_count</b> "
             "with k = 5 bins. Output column: <b>density_bins</b>. "
             "label_ranges: false, label_decimals: 1."],
            ["3", "apply_color_map\napply_grid_colormap",
             "Apply the <b>RdYlGn_r</b> colormap to <b>density_bins</b>, "
             "writing colours to <b>density_colors</b>."],
            ["4", "create_geojson_layer\ngenerate_grid_layers",
             "Build a DeckGL GeoJSON layer for the grid. Fill and line colour "
             "from density_colors (property reference). Opacity: 0.75, "
             "line colour: [0,0,0], data_url: null (embedded). "
             "Legend: title = 'Visits', label_column = density_bins, "
             "color_column = density_colors."],
            ["5", "combine_deckgl_map_layers\ncombine_grid_layers",
             "Combine static layers (conservancy boundaries, parcels, text) "
             "with the grid layer."],
            ["6", "draw_map\ndraw_grid_map",
             "Render the coverage map using the ArcGIS hillshade tile layer, "
             "view state from global_zoom_value, max_zoom: 10, "
             "legend placement: bottom-right."],
            ["7", "persist_text\npersist_grid_urls",
             "Write map HTML to <b>patrol_coverage_map.html</b>."],
            ["8", "html_to_png\nconvert_grid_png",
             "Render to <b>patrol_coverage_map.png</b>. "
             "device_scale_factor: 2.0, wait_for_timeout: 40 000 ms."],
            ["9", "compute_occupancy\ncompute_patrol_occupancy",
             "Calculate what percentage of the conservancy area (from "
             "<b>conservancy_gdf</b>) is covered by the patrol grid cells. "
             "crs: epsg:4326."],
            ["10", "round_values\nround_off_patrol",
             "Round <b>occupancy_percentage</b> to 2 decimal places."],
            ["11", "persist_df\npersist_occupancy_df",
             "Write to <b>patrol_coverage.csv</b>."],
        ],
        [0.5*cm, 4*cm, W - 4.5*cm],
    ),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 13. OUTPUT FILES
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("13. Output Files"),
    hr(),
    p("All files are written to <b>$ECOSCOPE_WORKFLOWS_RESULTS/</b>."),
    sp(6),
    h2("13.1  Events summary"),
    make_table(
        [
            ["File", "Format", "Description"],
            ["total_events_recorded_by_date.csv",  "CSV",
             "Daily event counts (all non-excluded types) with totals row"],
            ["total_events_recorded_by_type.csv",  "CSV",
             "Daily event counts by event_type"],
            ["total_events_recorded.html",          "HTML",
             "Interactive line chart of daily event totals"],
            ["total_events_recorded.png",           "PNG",
             "Static version of the events chart (2× DPI)"],
        ],
        [5.5*cm, 1.5*cm, W - 7*cm],
    ),
    sp(4),
    h2("13.2  Patrol purpose"),
    make_table(
        [
            ["File", "Format", "Description"],
            ["patrol_purpose_summary.csv", "CSV",
             "Patrol count and distance km by patrol purpose, with totals row"],
        ],
        [5.5*cm, 1.5*cm, W - 7*cm],
    ),
    sp(4),
    h2("13.3  Relocations"),
    make_table(
        [
            ["File", "Format", "Description"],
            ["patrol_relocations.geoparquet", "GeoParquet",
             "Full observation dataset: all patrol types, with patrol metadata "
             "columns (patrol_id, patrol_title, patrol_type, purpose, "
             "transport_type, participants, etc.)"],
        ],
        [5.5*cm, 1.5*cm, W - 7*cm],
    ),
    sp(4),
    h2("13.4  Foot patrols"),
    make_table(
        [
            ["File", "Format", "Description"],
            ["foot_patrol_efforts.csv",        "CSV",
             "patrol_type_value × no_of_patrols, distance_km, "
             "duration_hrs, average_speed. With totals row."],
            ["foot_patrol_trajectories.geojson", "GeoJSON",
             "Foot trajectory line geometries; properties: "
             "foot_patrol_colors, patrol_type_value"],
            ["foot_patrols_map.html",            "HTML",
             "Interactive foot patrol map (tab20 coloured by patrol type)"],
            ["foot_patrols_map.png",             "PNG",
             "Static version of the foot patrol map"],
        ],
        [5.5*cm, 1.5*cm, W - 7*cm],
    ),
    sp(4),
    h2("13.5  Vehicle patrols"),
    make_table(
        [
            ["File", "Format", "Description"],
            ["vehicle_patrol_efforts.csv",        "CSV",
             "patrol_type_value × no_of_patrols, distance_km, "
             "duration_hrs, average_speed. With totals row."],
            ["vehicle_patrol_trajectories.geojson", "GeoJSON",
             "Vehicle trajectory line geometries; properties: "
             "vehicle_patrol_colors, patrol_type_value"],
            ["vehicle_patrols_map.html",            "HTML",
             "Interactive vehicle patrol map (tab20 coloured by patrol type)"],
            ["vehicle_patrols_map.png",             "PNG",
             "Static version of the vehicle patrol map"],
        ],
        [5.5*cm, 1.5*cm, W - 7*cm],
    ),
    sp(4),
    h2("13.6  Motorbike patrols"),
    make_table(
        [
            ["File", "Format", "Description"],
            ["motorbike_patrol_efforts.csv",        "CSV",
             "patrol_type_value × no_of_patrols, distance_km, "
             "duration_hrs, average_speed. With totals row."],
            ["motor_patrol_trajectories.geojson", "GeoJSON",
             "Motorbike trajectory line geometries; properties: "
             "vehicle_patrol_colors, patrol_type_value"],
            ["motorbike_patrols_map.html",            "HTML",
             "Interactive motorbike patrol map (tab20 coloured by patrol type)"],
            ["motorbike_patrols_map.png",             "PNG",
             "Static version of the motorbike patrol map"],
        ],
        [5.5*cm, 1.5*cm, W - 7*cm],
    ),
    sp(4),
    h2("13.7  Combined trajectories and overall effort"),
    make_table(
        [
            ["File", "Format", "Description"],
            ["patrol_trajectories.geoparquet", "GeoParquet",
             "Merged foot + vehicle + motorbike trajectory dataset "
             "with renamed columns"],
            ["overall_patrol_efforts.csv", "CSV",
             "participants × no_of_patrols, distance_km, duration_hrs; "
             "nulls replaced with 'Unspecified'. With totals row."],
        ],
        [5.5*cm, 1.5*cm, W - 7*cm],
    ),
    sp(4),
    h2("13.8  Patrol coverage"),
    make_table(
        [
            ["File", "Format", "Description"],
            ["patrol_coverage_map.html", "HTML",
             "Interactive 1 000 m grid-cell visit density map (RdYlGn_r)"],
            ["patrol_coverage_map.png",  "PNG",
             "Static version of the coverage map"],
            ["patrol_coverage.csv",      "CSV",
             "Patrol occupancy percentage per conservancy region "
             "(2 decimal places)"],
        ],
        [5.5*cm, 1.5*cm, W - 7*cm],
    ),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 14. EXECUTION LOGIC AND SKIP CONDITIONS
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("14. Execution Logic and Skip Conditions"),
    hr(),
    p("All event-data tasks (from <b>get_events_data</b> onward) and all "
      "patrol-data tasks carry explicit <b>skipif</b> blocks with two "
      "conditions:"),
    make_table(
        [
            ["Condition", "Meaning"],
            ["any_is_empty_df",
             "Skip this task if any upstream DataFrame input is empty. "
             "Prevents errors when no events or patrols exist for the "
             "analysis period."],
            ["any_dependency_skipped",
             "Skip this task if any upstream task was itself skipped. "
             "Propagates the skip state through dependent branches without "
             "requiring explicit wiring."],
        ],
        [4*cm, W - 4*cm],
    ),
    sp(4),
    p("The geospatial asset pipeline tasks (Dropbox downloads, gpkg loading, "
      "layer building) do <b>not</b> carry skipif blocks — they run "
      "unconditionally on every workflow execution."),
    sp(4),
    p("The <b>merge_trajs</b> task (merging foot, vehicle, motorbike "
      "trajectories into the combined dataset) also does not carry a skipif "
      "block — it is always attempted. If any individual trajectory branch "
      "was skipped, that branch's output will simply be absent from the merge."),
    sp(4),
    note("The <b>filter_unspecified_patrols</b> branch filters observations "
         "with transport_type = 'unspecified' but does not have any downstream "
         "trajectory or map steps. Records with unspecified transport type "
         "are excluded from all trajectory maps and effort summaries."),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 15. SOFTWARE VERSIONS
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1("15. Software Versions"),
    hr(),
    make_table(
        [
            ["Package", "Version constraint", "Channel"],
            ["ecoscope-workflows-core",        "0.22.17.*",
             "https://repo.prefix.dev/ecoscope-workflows/"],
            ["ecoscope-workflows-ext-ecoscope","0.22.17.*",
             "https://repo.prefix.dev/ecoscope-workflows/"],
            ["ecoscope-workflows-ext-custom",  "0.0.45.*",
             "https://repo.prefix.dev/ecoscope-workflows-custom/"],
            ["ecoscope-workflows-ext-ste",     "0.0.19.*",
             "https://repo.prefix.dev/ecoscope-workflows-custom/"],
            ["ecoscope-workflows-ext-mep",     "0.0.14.*",
             "https://repo.prefix.dev/ecoscope-workflows-custom/"],
            ["ecoscope-workflows-ext-mnc",     "0.0.8.*",
             "https://repo.prefix.dev/ecoscope-workflows-custom/"],
        ],
        [5*cm, 3*cm, W - 8*cm],
    ),
]


# ── Build PDF ──────────────────────────────────────────────────────────────────
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"Written: {OUTPUT_FILE}")
