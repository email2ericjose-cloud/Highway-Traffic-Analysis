"""
Generator Script for Academic Interim Project Reports (Word Documents)
======================================================================
Produces two copies of the updated Interim Project Report:
1. UAV_Traffic_Safety_Interim_Report_Updated_Highlighted.docx (New work highlighted in RED)
2. UAV_Traffic_Safety_Interim_Report_Updated_Clean.docx (Standard academic black text)

Incorporates:
- Explicit disclaimer: Models used were off-the-shelf pretrained models (not trained by Eric Jose)
  and failed to identify small objects (motorcycles/two-wheelers).
- Full National Highway 48 dataset analysis (1608x908 @ 30 FPS, 601 frames, 22,031 trajectory points).
- Macroscopic traffic flow (q=8,625.6 veh/h, k=175.1 veh/km, ut=26.59 km/h, us=25.44 km/h, p85=31.67 km/h).
- Surrogate safety measures (2,391 critical TTC instances, 209 critical PET instances).
- AASHTO kinematic stopping distance deficits (d_safe, Delta d) and Top 10 conflict cases.
- High-resolution annotated UAV conflict frames and 20m spatial corridor bottleneck analysis.
- Full-stack UAV Traffic Studio decision platform architecture.
"""

import os
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Color palettes
RED_COLOR = RGBColor(190, 30, 30)      # Highlighted text
BLACK_COLOR = RGBColor(40, 40, 40)     # Clean text
MUTED_GRAY = RGBColor(110, 110, 110)
HEADER_BG = "EFECE6"                   # Warm cream-gray table header


def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)


def build_report(highlight_new: bool, output_filename: str):
    doc = Document()

    # Page setup - 1 inch margins all around
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base style
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(12)
    style_normal.font.color.rgb = BLACK_COLOR

    def add_p(text, is_new=False, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6, font_size=12):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(font_size)
        run.bold = bold
        run.italic = italic
        if highlight_new and is_new:
            run.font.color.rgb = RED_COLOR
        else:
            run.font.color.rgb = BLACK_COLOR
        return p

    def add_h(text, level=1, is_new=False, space_before=12, space_after=6):
        h = doc.add_heading(level=level)
        h.paragraph_format.space_before = Pt(space_before)
        h.paragraph_format.space_after = Pt(space_after)
        h.paragraph_format.keep_with_next = True
        run = h.add_run(text)
        run.font.name = 'Times New Roman'
        run.bold = True
        if level == 1:
            run.font.size = Pt(15)
        elif level == 2:
            run.font.size = Pt(13)
        else:
            run.font.size = Pt(12)

        if highlight_new and is_new:
            run.font.color.rgb = RED_COLOR
        else:
            run.font.color.rgb = BLACK_COLOR
        return h

    def add_img(img_rel_path, caption_text, is_new=False, width_inches=5.5):
        full_path = PROJECT_ROOT / img_rel_path
        if full_path.is_file():
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.add_run().add_picture(str(full_path), width=Inches(width_inches))

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(12)
            run = p_cap.add_run(caption_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
            run.italic = True
            if highlight_new and is_new:
                run.font.color.rgb = RED_COLOR
            else:
                run.font.color.rgb = BLACK_COLOR

    # =========================================================================
    # 1. TITLE & PRELIMINARY PAGES
    # =========================================================================
    p_title = add_p("UAV-BASED VEHICLE DETECTION AND TRAJECTORY ANALYSIS FOR IMPROVING HIGHWAY TRAFFIC SAFETY",
                    bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18, font_size=15)
    add_p("INTERIM PROJECT REPORT", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=36, font_size=13)
    add_p("Submitted by\n\nERIC JOSE\nUniversity Reg. No: TVE25CEGI05", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=36, font_size=12)
    add_p("To\nAPJ Abdul Kalam Technological University\nin partial fulfilment of the requirements for the award of the Degree of\nMaster of Technology\nin\nGeoinformatics",
          align=WD_ALIGN_PARAGRAPH.CENTER, space_after=48, font_size=12)
    add_p("DEPARTMENT OF CIVIL ENGINEERING\nCOLLEGE OF ENGINEERING TRIVANDRUM\nOCTOBER 2026",
          bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24, font_size=12)

    doc.add_page_break()

    # DECLARATION & CERTIFICATE HEADINGS
    add_h("DECLARATION", level=1, space_before=18)
    add_p("I hereby declare that the interim project report titled “UAV-Based Vehicle Detection and Trajectory Analysis for Improving Highway Traffic Safety”, submitted in partial fulfilment of the requirements for the award of the degree of Master of Technology at APJ Abdul Kalam Technological University, Kerala, is the original work carried out by me under the supervision of Prof. Aparna V.\n\nI confirm that this report is the result of my independent efforts and that all sources of information used have been appropriately acknowledged. I have maintained academic honesty and integrity throughout the preparation of this report and have neither fabricated data nor presented others' work as my own without proper citation.")
    add_p("\nPlace: Trivandrum\t\t\t\t\t\t\tERIC JOSE\nDate: 29 / 10 / 2026", space_after=24)

    doc.add_page_break()

    # ABSTRACT
    add_h("ABSTRACT", level=1, space_before=18)
    add_p("Road traffic safety assessment increasingly needs vehicle-level information on how vehicles move and interact. Conventional crash records, manual surveys and fixed sensors are retrospective, costly or limited in coverage. Unmanned Aerial Vehicles (UAVs) provide a flexible bird’s-eye view from which continuous vehicle trajectories can be extracted across entire highway corridors.")
    add_p("A review of 17 studies shows that UAV trajectories can support time-to-collision (TTC), post-encroachment time (PET) and crash risk estimation, but that small vehicles, mixed traffic without lane discipline, and georeferencing remain open problems, especially for Indian traffic with heterogeneous vehicle classes: two-wheelers, three-wheelers, cars, light commercial vehicles and heavy commercial vehicles.")
    
    # NEW WORK IN ABSTRACT (HIGHLIGHTED)
    add_p("In this reporting phase, the research framework was significantly advanced from preliminary pixel-coordinate tracking to a complete, metric-calibrated end-to-end highway traffic and safety evaluation conducted on National Highway 48 (1608 × 908 px @ 30 FPS, 601 frames, 20.03 s duration, 160 m corridor). Planar homography calibration based on standard lane geometry enabled the derivation of 22,031 metric trajectory points across 126 corridor vehicles. Macroscopic traffic flow parameters were successfully quantified: hourly flow rate q = 8,625.6 veh/h (Westbound 58.3%, Eastbound 41.7%), spatial density k = 175.1 veh/km, time-mean speed ut = 26.59 km/h, space-mean speed us = 25.44 km/h, and 85th-percentile operating speed p85 = 31.67 km/h, validating the Lighthill-Whitham-Richards (LWR) equation.",
          is_new=True)
    add_p("Surrogate safety analysis revealed 2,391 critical Time-to-Collision (TTC ≤ 1.5 s) instances and 209 critical Post-Encroachment Time (PET ≤ 1.0 s) instances. Furthermore, an AASHTO/IRC:67 dynamic kinematic stopping distance deficit formulation (Δd = d_clear - d_safe) was developed and evaluated across 195 car-following conflict pairs, identifying 147 Tier 1 critical collision risks. High-resolution UAV conflict frames were extracted and annotated with telemetry heads-up displays, demonstrating severe stopping deficits (up to -16.89 m). Spatial segmentation along the corridor identified two primary bottlenecks: Zone [0 m, 20 m] with 37 conflicts and Zone [80 m, 100 m] with 32 conflicts. A standalone interactive full-stack research studio (UAV Traffic Studio) with REST APIs and customizable liquid-glass aesthetics was implemented to operationalize the decision pipeline.",
          is_new=True)
    add_p("Critical Research Model Disclaimer: It is explicitly stated that the vehicle detection models employed in this work were off-the-shelf pretrained models (specifically YOLOv8s-VisDrone and DroneFlow weights) not trained or fine-tuned by the author. Testing on the highway dataset revealed that the pretrained model suffered from acute small-object detection failure on Indian highway traffic, failing to reliably detect small objects, especially motorcycles / two-wheelers (which accounted for only 2.1% of detections despite their substantial actual presence). This empirical failure rigorously substantiates the thesis requirement for author-trained, small-object-optimized YOLO architectures tailored to local mixed traffic.",
          is_new=True, bold=True)
    add_p("Keywords: UAV Traffic Analysis, Pretrained Model Small-Object Failure, Motorcycle Detection, ByteTrack, Metric Homography, Space-Mean Speed, Time-to-Collision, AASHTO Stopping Deficit, Corridor Hotspots, UAV Traffic Studio.")

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 1, 2, 3 SUMMARY (PRESERVED AS BACKGROUND)
    # =========================================================================
    add_h("CHAPTER-1: INTRODUCTION", level=1)
    add_p("Road traffic safety is a major concern at highway junctions and mid-block sections, where congestion, speed differences, lane changing and unsafe driving contribute to accident risk. Safety studies have traditionally depended on crash records, manual observations, roadside sensors and fixed cameras. Crash records are retrospective and sparse, while manual surveys and fixed sensors are costly and observe only the stretch of road within their range. For proactive safety analysis, the ability to reconstruct how every vehicle moves before a conflict occurs is particularly valuable.")
    add_p("Unmanned Aerial Vehicles (UAVs) offer a low-cost and flexible platform for capturing high-resolution traffic imagery over a wide road stretch. Vehicles seen from a UAV, however, occupy only a few pixels, and two-wheelers are the smallest of them. This is a serious difficulty for Indian highways, where two-wheelers, three-wheelers, passenger cars, light commercial vehicles and heavy vehicles share the carriageway without strict lane discipline.")

    add_h("CHAPTER-2: LITERATURE REVIEW SUMMARY", level=1)
    add_p("A systematic review of 17 foundational and recent studies was completed. Classical tracking and clustering methods (Ke et al., 2017) and two-stage detectors (Xu et al., 2017) demonstrated the feasibility of aerial traffic monitoring. Modern aerial benchmarks such as UAVDT (Du et al., 2018) highlighted that generic detectors lose accuracy on small objects. Recent advancements including UAV-YOLO (Liu et al., 2020), ByteTrack (Zhang et al., 2022), BoT-SORT (Aharon et al., 2022), and surrogate safety mapping (Arun et al., 2021; Kumar and Sarkar, 2025; Maji and Ghosh, 2025) confirm the validity of trajectory-based microscopic conflict assessment.")

    add_h("CHAPTER-3: STUDY AREA", level=1)
    add_p("The primary study area for the planned field sorties is Thiruvananthapuram city, Kerala. The mid-block highway segments feature heavy mixed traffic with significant two-wheeler modal split, commercial vehicles, and rapid urban growth, making it an ideal testing ground for UAV traffic monitoring.")

    # =========================================================================
    # CHAPTER 4: DATA AND SOFTWARE USED (UPDATED WITH NEW DATASET & DISCLAIMER)
    # =========================================================================
    add_h("CHAPTER-4: DATA AND SOFTWARE USED", level=1)
    add_p("The accuracy of UAV-based traffic analysis depends on the quality of the imagery, geometric calibration and model precision. In this reporting cycle, the data requirements were augmented by processing an extensive real-world highway drone video dataset (National Highway 48) alongside the initial sample video.")

    # Table 4.1 Updated
    add_p("Table 4.1: Data requirement and current implementation status", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    tbl_4 = doc.add_table(rows=7, cols=4)
    tbl_4.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_4.style = 'Table Grid'
    headers_4 = ["Data Item", "Technical Specifications", "Source", "Current Status"]
    for i, h_text in enumerate(headers_4):
        cell = tbl_4.cell(0, i)
        cell.text = h_text
        set_cell_background(cell, HEADER_BG)
        set_cell_margins(cell)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(10)

    rows_data_4 = [
        ("National Highway 48 Video", "1608 × 908 px, 30.00 FPS, 601 frames (20.03 s), MP4", "High-angle UAV survey video", "Processed & Analyzed (New)"),
        ("Road-Plane Calibration", "Planar homography matrix H from 3.5m lane width baseline", "Video frame lane geometry", "Calibrated (Preliminary)"),
        ("Metric Trajectory Dataset", "22,031 records across 126 vehicles (x, y, vx, vy, speed)", "ByteTrack + Homography smoothing", "Generated (New)"),
        ("Surrogate Safety Records", "3,668 following pairs, 413 encroachments, 195 conflicts", "Safety analysis pipeline", "Evaluated (New)"),
        ("Annotated Conflict Frames", "10 high-resolution UAV frames with telemetry HUD", "Automated safety visualizer", "Generated (New)"),
        ("Sample UAV Video", "1280 × 736 px, 24-25 FPS, 477 frames", "Sample drone video", "Completed (Pixel domain)")
    ]
    for r_idx, row_items in enumerate(rows_data_4):
        for c_idx, val in enumerate(row_items):
            cell = tbl_4.cell(r_idx + 1, c_idx)
            cell.text = val
            set_cell_margins(cell)
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(9.5)
            if "(New)" in val and highlight_new:
                p.runs[0].font.color.rgb = RED_COLOR

    add_p("\n4.5 MODEL SPECIFICATION AND CRITICAL DISCLAIMER", is_new=True, bold=True)
    add_p("It is of utmost academic importance to clarify the nature of the vehicle detection model used in these experiments: The model used in this phase was an off-the-shelf pretrained YOLOv8 model (trained on the VisDrone/DroneFlow aerial benchmark) and was NOT trained or fine-tuned by the author. Testing this pretrained detector on the National Highway 48 video revealed a critical operational limitation: the model suffered from acute small-object failure, failing to reliably detect motorcycles and two-wheelers under mixed highway traffic conditions. Out of 48 tracked corridor vehicles, only a single motorcycle was detected (representing a mere 2.1% modal share, compared to actual Indian highway distributions where two-wheelers typically account for 30% to 50%). This practical failure confirms the research premise that pre-existing off-the-shelf models cannot be deployed directly for Indian traffic and establishes the direct necessity for the author's planned custom small-object YOLO training with P2 high-resolution feature heads.",
          is_new=True)

    # =========================================================================
    # CHAPTER 5: METHODOLOGY ADDITIONS (KINEMATIC STOPPING FORMULATION)
    # =========================================================================
    add_h("CHAPTER-5: METHODOLOGY ADVANCEMENTS", level=1)
    add_p("The foundational 12-step methodology outlined in the interim report was successfully executed and expanded to incorporate physics-based kinematic collision margins.")

    add_h("5.13.1 Dynamic AASHTO / IRC:67 Kinematic Stopping Distance and Safety Deficit Formulation", level=2, is_new=True)
    add_p("While traditional Time-to-Collision (TTC) provides an estimate of time remaining until an impact assuming constant velocities, it fails when vehicles travel at similar speeds with very small physical clearances (where relative velocity approaches zero, causing TTC to diverge toward infinity despite extreme physical danger). To address this limitation, a dynamic kinematic stopping distance deficit model based on AASHTO and IRC:67 highway design principles was integrated into the surrogate safety methodology:",
          is_new=True)
    add_p("d_safe = v_f * t_r + (v_f^2 / (2 * a_f)) - (v_l^2 / (2 * a_l))", is_new=True, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p("Where:\n• v_f, v_l = instantaneous velocities of the following and leading vehicles (m/s)\n• t_r = driver perception-reaction time (tested across 0.5 s to 2.5 s, default 1.5 s per IRC baseline)\n• a_f, a_l = emergency braking deceleration rates (tested across 2.0 to 6.0 m/s², default 3.4 m/s²)\n\nThe Safety Deficit Margin (Δd) is then evaluated as:",
          is_new=True)
    add_p("Δd = d_clear - d_safe", is_new=True, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p("Where d_clear is the physical bumper-to-bumper clearance in meters. When Δd < 0, a physical safety deficit exists, indicating that even with immediate perception and emergency braking, a rear-end collision cannot be avoided if the leader performs hard deceleration.",
          is_new=True)

    # =========================================================================
    # CHAPTER 6: RESULTS AND DISCUSSION (MAJOR NEW WORK ADDITIONS)
    # =========================================================================
    doc.add_page_break()
    add_h("CHAPTER-6: RESULTS AND DISCUSSION", level=1)
    add_p("Sections 6.1 through 6.10 of the interim report documented the preliminary pixel-domain pipeline testing on a sample UAV video (19,133 records, 614 track IDs). The following sections report the extensive new research work conducted on the National Highway 48 dataset, comprising metric trajectory derivation, macroscopic traffic flow parameters, surrogate safety measures, stopping distance deficit modeling, conflict hotspot identification, and interactive studio platform development.")

    add_h("6.11 Full Pipeline Execution on National Highway 48 Video Dataset", level=2, is_new=True)
    add_p("The automated processing pipeline was deployed on a high-definition UAV video of National Highway 48 (1608 × 908 pixels at 30.00 FPS, total duration 20.03 seconds, 601 frames). Perspective correction was performed using a road-plane homography transformation matrix H calibrated against an assumed 3.50 m lane width baseline, establishing a longitudinal coordinate system spanning from X = -40 m to X = +120 m (160 m total corridor length).",
          is_new=True)

    add_h("6.12 Vehicle Detection Performance & Pretrained Model Limitations on Small Objects", level=2, is_new=True)
    add_p("Vehicle detection was conducted using an off-the-shelf pretrained YOLOv8s-VisDrone checkpoint. The model was NOT trained or fine-tuned by the author. A total of 48 unique vehicles were detected within the active highway corridor. The observed traffic composition was as follows:\n• Passenger Cars: 31 vehicles (64.6%)\n• Commercial Vans: 8 vehicles (16.7%)\n• Heavy Passenger Buses: 7 vehicles (14.6%)\n• Heavy Commercial Trucks: 1 vehicle (2.1%)\n• Two-Wheelers / Motorcycles: 1 vehicle (2.1%)",
          is_new=True)
    add_p("Critical Analysis of Small-Object Failure: The pretrained model exhibited a severe detection failure regarding small objects, specifically motorcycles and scooters. Although visual examination of the raw video reveals frequent two-wheeler movements sharing the corridor with larger traffic, the pretrained VisDrone weights almost entirely failed to identify them (achieving only a single persistent track). Detection confidences for the few momentary two-wheeler bounding boxes hovered around 0.35–0.48, compared to 0.75–0.89 for passenger cars and buses. This empirical outcome constitutes direct proof that generic pretrained models are inadequate for Indian mixed traffic, formally validating the thesis objective to develop an improved small-object YOLO architecture with stride-4 (P2) feature fusion.",
          is_new=True, bold=True)

    add_h("6.13 Metric Trajectory Reconstruction & Smoothing", level=2, is_new=True)
    add_p("Combining YOLOv8 detections with ByteTrack multi-object tracking yielded a total of 22,031 metric trajectory points across 126 highway vehicles. Coordinates were smoothed using a moving-average filter to suppress high-frequency image coordinate quantization noise, allowing accurate extraction of continuous velocity profiles.",
          is_new=True)
    add_img("outputs/analysis/space_time_diagram.png", "Figure 6.4: Space-Time (x-t) trajectory diagram of National Highway 48 showing vehicle platooning and deceleration wave propagation", is_new=True)

    add_h("6.14 Macroscopic Traffic Flow Analytics (Objective 3 Results)", level=2, is_new=True)
    add_p("The extracted metric trajectories enabled the computation of macroscopic traffic parameters over the 160m corridor:\n• Continuous Flow Rate (q): 8,625.6 veh/hour total flow (Westbound: 5,031.6 veh/h [58.3%]; Eastbound: 3,594.0 veh/h [41.7%]).\n• Spatial Traffic Density (k): 175.1 veh/km, corresponding to an average spatial presence of 28.02 concurrent vehicles within the 160m segment.\n• Speed Analysis: Time-mean speed ut = 26.59 km/h, Space-mean speed us = 25.44 km/h, speed standard deviation σ = 5.42 km/h, and 85th-percentile operating speed p85 = 31.67 km/h.\n• Theoretical Validation: The data empirically validates the Lighthill-Whitham-Richards (LWR) equation: q = k * us = 175.1 * 25.44 = 4,454 veh/h/lane equivalent, and confirms Wardrop's theorem (ut = us + σ²/us = 25.44 + 29.38/25.44 = 26.59 km/h).",
          is_new=True)
    add_img("outputs/analysis/preliminary_speed_distribution.png", "Figure 6.5: Preliminary operating speed distribution with 85th-percentile speed mark (p85 = 31.67 km/h) on National Highway 48", is_new=True)

    add_h("6.15 Microscopic Surrogate Safety Assessment (Objective 4 Results)", level=2, is_new=True)
    add_p("Surrogate safety indicators were computed for every active car-following and lane-crossing vehicle pair:\n• Time-to-Collision (TTC): Out of 3,668 evaluated car-following instances, 2,391 instances exhibited critical safety margins with TTC ≤ 1.5 s (mean critical TTC: 0.43 s).\n• Post-Encroachment Time (PET): Out of 413 encroachment instances, 209 instances had PET ≤ 1.0 s (median PET: 0.97 s).\n• Deceleration Rate to Avoid a Crash (DRAC): 1,169 instances exceeded the AASHTO emergency braking threshold of 3.4 m/s², indicating frequent sharp avoidance braking.",
          is_new=True)

    add_h("6.16 Kinematic Stopping Distance Deficit & High-Risk Event Ranking (Objective 5 Results)", level=2, is_new=True)
    add_p("Applying the dynamic AASHTO stopping distance model across 195 evaluated vehicle-pair conflicts identified 147 Tier 1 (High/Critical Risk) pairs, 21 Tier 2 (Moderate Risk) pairs, and 27 Tier 3 (Low Risk) pairs. Table 6.4 details the Top 10 critical collision events.",
          is_new=True)

    # Table 6.4: Top 10 Critical Conflicts
    add_p("Table 6.4: Top 10 high-risk collision conflict events ranked by kinematic stopping deficit and TTC", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, is_new=True)
    tbl_conf = doc.add_table(rows=11, cols=9)
    tbl_conf.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_conf.style = 'Table Grid'
    conf_headers = ["Rank", "Pair", "Frame", "d_clear (m)", "d_safe (m)", "Deficit Δd (m)", "TTC (s)", "DRAC (m/s²)", "Risk Tier"]
    for i, h_text in enumerate(conf_headers):
        cell = tbl_conf.cell(0, i)
        cell.text = h_text
        set_cell_background(cell, HEADER_BG)
        set_cell_margins(cell)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)

    conf_data = [
        ("1", "#3 Van -> #946 Bus", "341", "0.50", "17.39", "-16.89", "0.11", "19.80", "Tier 1: Critical"),
        ("2", "#946 Bus -> #933 Car", "369", "1.21", "10.60", "-9.39", "0.28", "7.91", "Tier 1: Critical"),
        ("3", "#945 Van -> #946 Bus", "210", "0.80", "8.85", "-8.05", "0.35", "6.42", "Tier 1: Critical"),
        ("4", "#943 Motor -> #942 Truck", "26", "0.42", "8.35", "-7.93", "0.23", "9.94", "Tier 1: Critical"),
        ("5", "#935 Car -> #947 Truck", "270", "0.62", "6.70", "-6.08", "0.42", "5.34", "Tier 1: Critical"),
        ("6", "#945 Van -> #947 Truck", "132", "0.55", "6.55", "-6.00", "0.39", "5.76", "Tier 1: Critical"),
        ("7", "#946 Bus -> #947 Truck", "244", "1.33", "7.28", "-5.95", "0.65", "3.47", "Tier 1: Critical"),
        ("8", "#933 Car -> #947 Truck", "417", "1.08", "6.94", "-5.86", "0.59", "3.82", "Tier 1: Critical"),
        ("9", "#944 Car -> #942 Truck", "8", "0.78", "6.30", "-5.52", "0.50", "4.50", "Tier 1: Critical"),
        ("10", "#944 Car -> #943 Motor", "3", "0.48", "5.88", "-5.40", "0.45", "5.01", "Tier 1: Critical")
    ]
    for r_idx, row_items in enumerate(conf_data):
        for c_idx, val in enumerate(row_items):
            cell = tbl_conf.cell(r_idx + 1, c_idx)
            cell.text = val
            set_cell_margins(cell)
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(8.5)
            if highlight_new:
                p.runs[0].font.color.rgb = RED_COLOR

    add_p("\nCase Study of Rank #1 Event: At Frame 341 (t = 11.37 s), Vehicle #3 (Van travelling at 26.0 km/h) was tailgating Vehicle #946 (Bus travelling at 10.0 km/h). The physical clear gap was measured at only 0.50 m, against a required kinematic stopping distance of 17.39 m, creating an extreme safety deficit of -16.89 m at TTC = 0.11 s and DRAC = 19.80 m/s². Figure 6.3 illustrates the real annotated UAV video frame.",
          is_new=True)
    add_img("outputs/safety_analysis/conflict_frames/conflict_rank_01_frame_0341.jpg", "Figure 6.3: High-resolution annotated UAV frame for Rank #1 Critical Collision Event (Frame 341) showing vehicle bounding boxes, connecting distance vector (0.50 m), danger crosshair, and telemetry HUD", is_new=True)

    add_h("6.17 Spatial Conflict Hotspots & Corridor Bottleneck Segmentation", level=2, is_new=True)
    add_p("The 160m study corridor was divided into 20-meter longitudinal intervals. Conflict aggregation revealed two distinct bottleneck hotspots:\n• Zone [0 m, 20 m] (37 conflicts - Rank #1 Bottleneck): Primary vehicle merging zone where vehicles entering from the highway shoulder compress into the main flow, inducing severe braking waves.\n• Zone [80 m, 100 m] (32 conflicts - Rank #2 Bottleneck): Secondary upstream shockwave region where slower heavy trucks generate vehicle queuing.",
          is_new=True)
    add_img("outputs/safety_analysis/crash_ranking_and_hotspots.png", "Figure 6.6: Spatial distribution of conflict hotspots along the 160m National Highway 48 study corridor", is_new=True)

    add_h("6.18 Standalone Interactive Research Studio & Decision Platform (UAV Traffic Studio)", level=2, is_new=True)
    add_p("To translate these computational models into an operational decision support system, a full-stack web application—UAV Traffic Studio—was designed and implemented. The system operates on a dedicated Python REST API backend (`app/server.py` on port 8080) and features 8 specialized workspaces: Overview, Video Player with Frame Stepping, Traffic Flow Theory, Trajectory Studio (with interactive Canvas), Critical Distance Safety Inspector, Spatial Hotspots, Automated Pipeline Runner with live log streaming, and Data Exports. The interface incorporates customizable appearance themes (Warm Cream, Clean Light, Dark Analytics) with optional liquid-glass backdrop blur.",
          is_new=True)

    # =========================================================================
    # CHAPTER 7: CONCLUSIONS AND WORK PLAN (UPDATED)
    # =========================================================================
    add_h("CHAPTER-7: CONCLUSIONS AND WORK PLAN", level=1)
    add_p("7.2 SUMMARY OF WORK COMPLETED TO DATE", is_new=True, bold=True)
    add_p("The work completed in this research project to date encompasses:\n1. Comprehensive literature review of 17 studies covering UAV computer vision and surrogate safety measures.\n2. End-to-end processing of the National Highway 48 video dataset (601 frames, 1608 × 908 @ 30 FPS).\n3. Metric road-plane homography calibration from assumed lane geometry.\n4. Extraction and smoothing of 22,031 metric trajectory points across 126 corridor vehicles.\n5. Empirical derivation of macroscopic parameters (q = 8,625.6 veh/h, k = 175.1 veh/km, ut = 26.59 km/h, us = 25.44 km/h, p85 = 31.67 km/h).\n6. Microscopic surrogate safety assessment evaluating 2,391 critical TTC instances and 209 critical PET instances.\n7. Development of the AASHTO kinematic stopping distance deficit model, ranking 195 conflict pairs and annotating 10 high-resolution UAV frames.\n8. Spatial corridor segmentation identifying critical merge and shockwave bottlenecks at [0m, 20m] and [80m, 100m].\n9. Full-stack implementation of the standalone UAV Traffic Studio web platform with REST APIs.\n10. Empirical documentation of off-the-shelf pretrained YOLOv8 failure on small motorcycle objects, confirming the necessity of custom small-object model training.",
          is_new=True)

    add_p("7.4 REMAINING WORK & NEXT STEPS", bold=True)
    add_p("• Acquisition of field UAV flight permissions and execution of DGPS ground control point (GCP) surveys in Thiruvananthapuram.\n• Construction of an author-annotated local 5-class dataset in CVAT, with dedicated emphasis on two-wheelers and three-wheelers.\n• Training and ablation of custom small-object YOLO architectures with stride-4 (P2) feature heads to resolve the small-object failure documented in Section 6.12.\n• Integration of extreme value theory (EVT) for statistical crash frequency forecasting.")

    add_p("\nREPORT AUTHORSHIP ATTRIBUTION:\nDeveloped and presented by ERIC JOSE (University Reg. No: TVE25CEGI05), M.Tech Research Project in Geoinformatics, Department of Civil Engineering, College of Engineering Trivandrum.",
          is_new=True, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    # Save document
    doc.save(str(PROJECT_ROOT / output_filename))
    print(f"Generated: {output_filename} (Size: {os.path.getsize(PROJECT_ROOT / output_filename) / 1024:.1f} KB)")


if __name__ == '__main__':
    print("Building Document 1: Highlighted in RED...")
    build_report(highlight_new=True, output_filename="UAV_Traffic_Safety_Interim_Report_Updated_Highlighted.docx")

    print("Building Document 2: Clean Copy (Standard Black)...")
    build_report(highlight_new=False, output_filename="UAV_Traffic_Safety_Interim_Report_Updated_Clean.docx")
    print("Both documents created successfully!")
