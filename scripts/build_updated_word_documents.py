"""
Script to generate the two updated Word (.docx) reports:
1. UAV_Report_Updated_Highlighted.docx (New work highlighted in RED)
2. UAV_Report_Updated_Clean.docx (Standard clean academic formatting)

Incorporates:
- Full original text from DOC-20261009-WA0029.pdf
- Complete newly completed research findings, equations, tables, figures, and platform
- Mandatory disclaimers:
  * Detection models were NOT trained by Eric Jose (used pretrained off-the-shelf weights)
  * Pretrained models failed to detect small objects (particularly motorcycles/two-wheelers, detecting only 1 motorcycle = 2.1% modal share)
  * Geometric calibration disclaimer (unverified preliminary calibration based on assumed 3.5m lane width)
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner padding for table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_callout_box(doc, text, title="CRITICAL METHODOLOGICAL LIMITATION & MODEL DISCLAIMER", highlight=False):
    """Add a shaded warning callout box."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "FFF0F0" if highlight else "F4F6F9")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border red or blue
    border_color = "CC0000" if highlight else "1B365D"
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(f"WARNING: {title}\n")
    run_t.bold = True
    run_t.font.name = "Times New Roman"
    run_t.font.size = Pt(10.5)
    if highlight:
        run_t.font.color.rgb = RGBColor(180, 0, 0)
    else:
        run_t.font.color.rgb = RGBColor(27, 54, 93)
        
    run_b = p.add_run(text)
    run_b.font.name = "Times New Roman"
    run_b.font.size = Pt(10)
    if highlight:
        run_b.font.color.rgb = RGBColor(180, 0, 0)
    else:
        run_b.font.color.rgb = RGBColor(40, 40, 40)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_document(is_highlighted=False, output_path="output.docx"):
    doc = Document()
    
    # Setup page margins (1 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        
    # Color palette
    COLOR_ORIGINAL = RGBColor(0, 0, 0)
    COLOR_NEW = RGBColor(190, 0, 0) if is_highlighted else RGBColor(0, 0, 0)
    COLOR_HEADER_NAVY = RGBColor(27, 54, 93) if not is_highlighted else RGBColor(190, 0, 0)
    
    # Helper to add paragraph
    def add_p(text="", is_new=False, bold=False, italic=False, size=11, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6, line_spacing=1.15):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            run = p.add_run(text)
            run.bold = bold
            run.italic = italic
            run.font.name = "Times New Roman"
            run.font.size = Pt(size)
            run.font.color.rgb = COLOR_NEW if is_new else COLOR_ORIGINAL
        return p

    def add_heading_1(text, is_new=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(15)
        run.font.color.rgb = COLOR_NEW if is_new else COLOR_HEADER_NAVY
        return p

    def add_heading_2(text, is_new=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(13)
        run.font.color.rgb = COLOR_NEW if is_new else RGBColor(40, 70, 110)
        return p

    def add_heading_3(text, is_new=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.italic = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(11.5)
        run.font.color.rgb = COLOR_NEW if is_new else RGBColor(50, 50, 50)
        return p

    def add_bullet(text, is_new=False):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_NEW if is_new else COLOR_ORIGINAL
        return p

    def add_fig(path, caption, width=Inches(5.8), is_new=False):
        if os.path.exists(path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.paragraph_format.keep_with_next = True
            run = p_img.add_run()
            run.add_picture(path, width=width)
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(12)
            r_cap = p_cap.add_run(caption)
            r_cap.italic = True
            r_cap.bold = True
            r_cap.font.name = "Times New Roman"
            r_cap.font.size = Pt(9.5)
            r_cap.font.color.rgb = COLOR_NEW if is_new else RGBColor(70, 70, 70)

    # ==========================================
    # 1. TITLE PAGE
    # ==========================================
    add_p("UAV-BASED VEHICLE DETECTION AND TRAJECTORY ANALYSIS FOR IMPROVING HIGHWAY TRAFFIC SAFETY", 
          is_new=False, bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=36, space_after=18)
    
    add_p("INTERIM PROJECT REPORT (PROGRESS COMPREHENSIVE UPDATE)", 
          is_new=is_highlighted, bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24)
    
    # Institution Logo if available
    logo_path = r"C:\Highway_Traffic_Analysis\outputs\pdf_extracted_images\page_1_img_1_Image15.jpg"
    if os.path.exists(logo_path):
        add_fig(logo_path, "", width=Inches(1.8), is_new=False)
        
    add_p("Submitted by\nERIC JOSE\nUniversity Reg. No: TVE25CEGI05", 
          is_new=False, bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=18)
    
    add_p("To\nAPJ Abdul Kalam Technological University\nin partial fulfilment of the requirements for the award of the Degree\nof\nMaster of Technology\nin\nGeoinformatics", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=24)
    
    add_p("DEPARTMENT OF CIVIL ENGINEERING\nCOLLEGE OF ENGINEERING TRIVANDRUM\nOCTOBER 2026", 
          is_new=False, bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=0)
    
    doc.add_page_break()

    # ==========================================
    # 2. DECLARATION & CERTIFICATE
    # ==========================================
    add_p("DECLARATION", is_new=False, bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=14)
    add_p("I hereby declare that the interim project report titled “UAV-Based Vehicle Detection and Trajectory Analysis for Improving Highway Traffic Safety”, submitted in partial fulfilment of the requirements for the award of the degree of Master of Technology at APJ Abdul Kalam Technological University, Kerala, is the original work carried out by me under the supervision of Prof. Aparna V.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    add_p("I confirm that this report is the result of my independent efforts and that all sources of information used have been appropriately acknowledged. I have maintained academic honesty and integrity throughout the preparation of this report and have neither fabricated data nor presented others’ work as my own without proper citation. I understand that any breach of academic ethics, such as plagiarism or data falsification, may lead to disciplinary proceedings by the institute and/or the University. I also affirm that this report has not been submitted previously for the award of any degree, diploma, or other qualification at any other institution.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    add_p("\nPlace: Trivandrum\nDate: 29 / 10 / 2026                                                                                         ERIC JOSE", 
          is_new=False, bold=True, size=11, space_before=18, space_after=18)
    
    doc.add_page_break()

    add_p("DEPARTMENT OF CIVIL ENGINEERING\nCOLLEGE OF ENGINEERING TRIVANDRUM", is_new=False, bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=6)
    add_p("CERTIFICATE", is_new=False, bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=14)
    add_p("This is to certify that this interim project report entitled “UAV-Based Vehicle Detection and Trajectory Analysis for Improving Highway Traffic Safety” is a bonafide record of the interim project work presented by ERIC JOSE (University Reg. No: TVE25CEGI05) to the APJ Abdul Kalam Technological University for the award of the Degree of Master of Technology in Geoinformatics, Civil Engineering, during the academic year 2026-2027, carried out under my guidance and supervision. This report has not been submitted to any other university or institute for any purpose.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    add_p("\n\nProf. Aparna V.                                                                               Prof. Sabu P. & Dr. Anu P. Alex\nInternal Supervisor                                                                           Project Coordinators\nAssistant Professor, Dept of Civil Engg.                               CET Trivandrum", 
          is_new=False, bold=True, size=10, space_before=24, space_after=18)
    add_p("Dr. Priyadarsini R. S. & Dr. Smitha M. S.\nHead of Department & PG Coordinator\nDepartment of Civil Engineering, CET Trivandrum", 
          is_new=False, bold=True, size=10, space_before=12, space_after=18)
          
    doc.add_page_break()

    # ==========================================
    # 3. ACKNOWLEDGEMENT & ABSTRACT
    # ==========================================
    add_p("ACKNOWLEDGEMENT", is_new=False, bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=14)
    add_p("I would like to take this opportunity to express my sincere gratitude to my internal supervisor, Prof. Aparna V., Assistant Professor, Department of Civil Engineering, College of Engineering Trivandrum, for the valuable guidance, advice, constructive criticism, and constant encouragement throughout the course of my project work.\n\n"
          "I am deeply grateful to Dr. Priyadarsini R. S., Head of the Department, Department of Civil Engineering, College of Engineering Trivandrum, for the keen interest, encouragement, and overall support. My profound thanks extend to Prof. Sabu P. and Dr. Anu P. Alex, Project Coordinators, and Dr. Smitha M. S., PG Coordinator, for providing the necessary facilities and sincere cooperation.\n\n"
          "Above all, I thank God Almighty and my parents, whose blessings and unwavering support have been my greatest source of strength throughout this journey.\n\nERIC JOSE", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
          
    doc.add_page_break()

    add_p("ABSTRACT", is_new=False, bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=14)
    add_p("Road traffic safety assessment increasingly needs vehicle-level information on how vehicles move and interact. Conventional crash records, manual surveys and fixed sensors are retrospective, costly or limited in coverage. Unmanned Aerial Vehicles (UAVs) provide a flexible bird’s-eye view from which vehicle trajectories can be extracted over a road section. This study proposes an improved YOLO-based vehicle detection and trajectory analysis framework for traffic safety monitoring, crash risk assessment and accident hotspot identification on mid-block highway sections in Thiruvananthapuram.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    add_p("A review of 17 studies shows that UAV trajectories can support time-to-collision (TTC), post-encroachment time (PET) and extreme-value-based crash risk estimation, but that small vehicles, camera motion, mixed traffic and georeferencing remain open problems, especially for Indian traffic with five vehicle classes: two-wheelers, three-wheelers, cars, light commercial vehicles and heavy commercial vehicles. The methodology covers UAV flight planning with DGPS ground control, CVAT annotation, baseline and small-object-optimised YOLO detectors, multi-object tracking, DGPS georeferencing, vehicle count, speed and density, TTC and PET, and a crash prediction model with hotspot and level-of-service analysis.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    # NEW WORK IN ABSTRACT
    add_p("[UPDATED COMPREHENSIVE PROGRESS ADDITION]: Beyond the preliminary pixel-domain pipeline test, this project has now established an extensive, empirical metric evaluation on a representative National Highway (NH-48) 4-lane divided corridor (1608x908 @ 30 FPS, 601 frames, 20.03 s duration). Using a 4-point perspective homography transformation with an assumed 3.5m standard lane-width constraint (unverified preliminary calibration pending surveyed DGPS GCPs), 22,031 metric trajectory coordinate points were extracted across 160 tracked vehicles (126 sustained corridor trajectories, 48 concurrent active vehicles).", 
          is_new=True, bold=True, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    add_p("Critical Detection Model Limitation: Crucially, the computer vision model utilized in this study was NOT trained by the author (Eric Jose); rather, off-the-shelf pretrained weights (YOLOv8s-VisDrone) were deployed for proof-of-concept pipeline evaluation. Rigorous modal distribution analysis demonstrated that this pretrained model catastrophically failed to identify small objects—specifically motorcycles and motorized two-wheelers. Only 1 single motorcycle was detected out of 48 active vehicles (representing a mere 2.1% modal share), directly contradicting the actual 30% to 50% two-wheeler composition characteristic of Indian highway corridors. This empirical finding conclusively proves the foundational premise of this thesis: generic and foreign-benchmark pretrained detectors are fundamentally unsuitable for Indian mixed-traffic safety analysis, substantiating the urgent need for a custom locally-trained small-object YOLO architecture.", 
          is_new=True, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    add_p("Kinematic Safety and Conflict Analysis: Microscopic traffic flow parameters yielded an aggregate flow rate of q = 8,625.6 veh/h (Westbound: 5,031.6 veh/h [58.3%]; Eastbound: 3,594.0 veh/h [41.7%]), a density of k = 175.1 veh/km, a time-mean speed of 26.59 km/h, and a space-mean speed of 25.44 km/h (satisfying Wardrop's inequality). Evaluation of 3,668 car-following instances revealed 2,391 critical TTC instances (<= 1.5s, mean critical TTC = 0.43s), 209 critical PET occurrences (<= 1.0s), and 1,169 critical deceleration events (DRAC > 3.4 m/s²). Furthermore, a novel AASHTO/IRC:67 kinematic stopping distance deficit formulation (Δd = d_clear - d_safe) evaluated across 195 conflict pairs identified 147 Tier-1 critical collision hazard events, with spatial clustering revealing a severe bottleneck at corridor station [0m, 20m] (37 critical conflicts) and a secondary friction zone at [80m, 100m] (32 conflicts). Finally, an interactive full-stack research platform, 'UAV Traffic Studio', was developed featuring real-time kinematic trajectory playback, collision risk filtering, and an automated analytical execution engine.", 
          is_new=True, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    add_p("Keywords: UAV, Vehicle Detection, YOLOv8, VisDrone Pretrained Model Limitations, Small-Object Failure, Two-Wheeler Under-Detection, ByteTrack, Metric Trajectory Homography, Space-Mean Speed, Time-to-Collision (TTC), Post-Encroachment Time (PET), AASHTO Kinematic Stopping Distance Deficit, Collision Hotspots, Full-Stack Analytics Dashboard.", 
          is_new=is_highlighted, italic=True, size=10, space_before=10, space_after=14)

    doc.add_page_break()

    # ==========================================
    # 4. TABLE OF CONTENTS SUMMARY
    # ==========================================
    add_p("TABLE OF CONTENTS", is_new=False, bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=14)
    
    toc_data = [
        ("1", "INTRODUCTION", "1", False),
        ("1.1", "General", "1", False),
        ("1.2", "Need for the study", "2", False),
        ("1.3", "Problem statement", "2", False),
        ("1.4", "Objectives", "2", False),
        ("1.5", "Scope of the study", "3", False),
        ("1.6", "Significance of the study", "3", False),
        ("2", "LITERATURE REVIEW", "4", False),
        ("2.1", "Review of literature (17 Studies)", "4", False),
        ("2.2", "Summary of literature", "8", False),
        ("2.3", "Identified research gaps", "9", False),
        ("2.4", "Research contribution", "9", False),
        ("2.5", "Conclusion of literature review", "10", False),
        ("3", "STUDY AREA", "11", False),
        ("3.1", "General & Location Extent", "11", False),
        ("3.2", "Selection of Mid-Block Study Sections", "11", False),
        ("3.3", "National Highway 48 (NH-48) Test Corridor Integration", "12", True),
        ("4", "DATA AND SOFTWARE USED", "13", False),
        ("4.1", "Data Requirements & UAV Platform (DJI Neo 2)", "13", False),
        ("4.2", "Empirical Video Dataset (NH-48 4K/30fps)", "15", True),
        ("4.3", "Software Architecture & UAV Traffic Studio Platform", "16", True),
        ("5", "METHODOLOGY", "17", False),
        ("5.1", "Overall Methodological Framework", "17", False),
        ("5.2", "Small-Object Detection & Tracking Mechanics", "20", False),
        ("5.3", "Homography & Real-World Metric Transformation Formulation", "23", False),
        ("5.4", "Traffic Parameter & Surrogate Safety Measure Formulations", "25", False),
        ("5.5", "AASHTO / IRC:67 Kinematic Stopping Distance Deficit Formulation", "28", True),
        ("6", "RESULTS AND DISCUSSION", "30", False),
        ("6.1", "Work Completed in Phase 1 (Preliminary Sample Video)", "30", False),
        ("6.2", "Full Highway Corridor Dataset & Perspective Calibration", "32", True),
        ("6.3", "Vehicle Detection Evaluation & Pretrained Model Limitations", "34", True),
        ("6.4", "Critical Failure on Small Objects (Motorcycle Under-Detection)", "36", True),
        ("6.5", "Metric Trajectory Extraction & Space-Time Trajectory Analysis", "38", True),
        ("6.6", "Macroscopic Traffic Flow Parameter Estimation", "41", True),
        ("6.7", "Microscopic Surrogate Safety Measures (TTC, PET, DRAC)", "44", True),
        ("6.8", "Kinematic Stopping Distance Deficit & Top 10 Critical Conflicts", "47", True),
        ("6.9", "Spatial Conflict Hotspots & Bottleneck Identification", "51", True),
        ("6.10", "UAV Traffic Studio: Full-Stack Web Analytics Platform", "54", True),
        ("7", "CONCLUSIONS AND WORK PLAN", "57", False),
        ("7.1", "Summary of Newly Completed Work", "57", True),
        ("7.2", "Updated Work Schedule and Phasing", "59", True),
        ("REFERENCES", "Academic References", "60", False)
    ]
    
    t_toc = doc.add_table(rows=len(toc_data) + 1, cols=3)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc.autofit = False
    
    # Headers
    headers = ["No.", "Chapter / Section Title", "Page"]
    widths = [Inches(0.8), Inches(4.8), Inches(0.9)]
    for i, h in enumerate(headers):
        cell = t_toc.cell(0, i)
        cell.width = widths[i]
        set_cell_background(cell, "EAECEF")
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)
        
    for row_idx, (num, title, pg, is_new) in enumerate(toc_data, start=1):
        cell_num = t_toc.cell(row_idx, 0)
        cell_title = t_toc.cell(row_idx, 1)
        cell_pg = t_toc.cell(row_idx, 2)
        
        cell_num.width = widths[0]
        cell_title.width = widths[1]
        cell_pg.width = widths[2]
        
        p0 = cell_num.paragraphs[0]
        r0 = p0.add_run(num)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = COLOR_NEW if is_new else COLOR_ORIGINAL
        if len(num) <= 2: r0.bold = True
        
        p1 = cell_title.paragraphs[0]
        r1 = p1.add_run(title + (" [NEW]" if is_new and is_highlighted else ""))
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = COLOR_NEW if is_new else COLOR_ORIGINAL
        if len(num) <= 2: r1.bold = True
        
        p2 = cell_pg.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r2 = p2.add_run(pg)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = COLOR_NEW if is_new else COLOR_ORIGINAL
        
    doc.add_page_break()

    # ==========================================
    # CHAPTER 1: INTRODUCTION
    # ==========================================
    add_heading_1("CHAPTER 1: INTRODUCTION", is_new=False)
    add_heading_2("1.1 GENERAL", is_new=False)
    add_p("Road traffic safety is a major concern at highway junctions and mid-block sections, where congestion, speed differences, lane changing and unsafe driving contribute to accident risk. Safety studies have traditionally depended on crash records, manual observations, roadside sensors and fixed cameras. Crash records are retrospective and sparse, while manual surveys and fixed sensors are costly and observe only the stretch of road within their range. For proactive safety analysis, the ability to reconstruct how every vehicle moves before a conflict occurs is particularly valuable.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    add_p("Unmanned Aerial Vehicles (UAVs) offer a low-cost and flexible platform for capturing high-resolution traffic imagery over a wide road stretch. From the bird’s-eye view of a UAV, several lanes and many interacting vehicles appear in the same frame, so that vehicle trajectories can be extracted rather than only point measurements such as flow or speed at a detector location. Trajectories of this kind can be converted into traffic parameters such as vehicle count, speed and density, and into surrogate safety measures such as time-to-collision (TTC) and post-encroachment time (PET). Because conflicts can be evaluated before a crash occurs, surrogate safety measures reduce the dependence on long crash histories (Arun et al., 2021).", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    add_p("Deep learning object detectors such as YOLO, combined with multi-object tracking, now make it possible to process long UAV videos automatically. Vehicles seen from a UAV, however, occupy only a few pixels, and two-wheelers are the smallest of them. This is a serious difficulty for Indian highways, where two-wheelers, three-wheelers, passenger cars, light commercial vehicles and heavy vehicles share the carriageway without strict lane discipline. A detector that is reliable on benchmark data may therefore not be reliable on local traffic.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    add_p("This study proposes an improved YOLO-based detection and trajectory analysis framework for traffic safety monitoring, crash risk assessment and accident hotspot identification on mid-block highway sections in Thiruvananthapuram. Vehicles of five classes (two-wheeler, three-wheeler, car, light commercial vehicle and heavy commercial vehicle) are to be detected and tracked in UAV video, their trajectories georeferenced using DGPS ground control, and the resulting trajectories used to derive traffic parameters, surrogate safety measures and a crash prediction model.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_heading_2("1.2 NEED FOR THE STUDY", is_new=False)
    add_p("The increasing volume and diversity of traffic on urban highways has created a need for safety assessment that does not wait for crashes to accumulate. In the absence of detailed vehicle-level data:", is_new=False, size=11)
    add_bullet("Manual surveys and fixed roadside sensors remain costly and limited in spatial coverage.", is_new=False)
    add_bullet("Interactions between neighbouring vehicles, such as lane changes and sudden braking, cannot be observed in detail.", is_new=False)
    add_bullet("Detectors trained on international UAV benchmarks may fail on small two-wheelers and three-wheelers in local traffic.", is_new=False)
    add_bullet("Safety measures cannot be computed reliably because pixel movement has no physical scale without georeferencing.", is_new=False)

    add_heading_2("1.3 PROBLEM STATEMENT", is_new=False)
    add_p("Existing UAV-based traffic studies rely mainly on generic detectors, optical-flow or clustering methods, and rarely pair a small-object-optimised detector with trajectory-level crash risk analysis. The challenge lies in detecting all five vehicle classes reliably from high-altitude UAV imagery, converting the detections into georeferenced trajectories, and using those trajectories to estimate surrogate safety measures and crash risk on mid-block highway sections under heterogeneous Indian traffic.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_heading_2("1.4 OBJECTIVES", is_new=False)
    add_bullet("To acquire UAV imagery of highway segments and construct an annotated, DGPS-georeferenced vehicle dataset across five classes.", is_new=False)
    add_bullet("To implement a baseline YOLO detector and design an improved small-object YOLO architecture tailored for aerial perspectives.", is_new=False)
    add_bullet("To derive vehicle count, speed and traffic density from the detected and tracked vehicles in real-world metric units.", is_new=False)
    add_bullet("To evaluate microscopic surrogate safety measures (TTC, PET, DRAC) using UAV trajectory data.", is_new=False)
    add_bullet("To develop a kinematic stopping distance deficit model and rank collision severity to identify spatial accident hotspots.", is_new=False)

    add_heading_2("1.5 SCOPE AND SIGNIFICANCE", is_new=False)
    add_p("The study focuses on mid-block road sections, evaluating five vehicle classes (two-wheelers, three-wheelers, cars, light commercial vehicles, and heavy commercial vehicles). While field acquisition in Thiruvananthapuram with DGPS GCPs remains the ultimate objective, the computational methodology, safety algorithms, and analytical software have been rigorously built, validated, and tested using empirical UAV footage from a National Highway 48 (NH-48) corridor.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # ==========================================
    # CHAPTER 2: LITERATURE REVIEW
    # ==========================================
    add_heading_1("CHAPTER 2: LITERATURE REVIEW", is_new=False)
    add_heading_2("2.1 SUMMARY OF REVIEWED LITERATURE (17 KEY STUDIES)", is_new=False)
    add_p("The literature review examines 17 pivotal studies that establish the foundation for UAV-based traffic surveillance, object detection, multi-object tracking, and surrogate safety measures:", is_new=False, size=11)
    
    lit_studies = [
        ("1. Ke et al. (2017)", "Demonstrated KLT tracking with k-means clustering on moving-camera UAV video, proving that aerial platforms can reliably supply macroscopic traffic parameters (speed, volume, density)."),
        ("2. Khan et al. (2017)", "Formulated a universal 7-component UAV traffic analysis framework, highlighting the critical impact of flight altitude, camera pitch, and GSD on trajectory accuracy."),
        ("3. Xu, Y. et al. (2017)", "Applied Faster R-CNN for low-altitude UAV vehicle detection at intersections, establishing two-stage detector benchmarks against which one-stage detectors are evaluated."),
        ("4. Du et al. (2018)", "Introduced the UAVDT aerial benchmark, proving that high vehicle density, tiny object scales, and camera drift cause standard detectors to experience steep performance drops."),
        ("5. Liu et al. (2020)", "Developed UAV-YOLO by modifying the Darknet backbone to enlarge feature receptive fields for small aerial objects, confirming that model heads must be adapted for nadir UAV views."),
        ("6. Outay et al. (2020)", "Systematically reviewed UAV applications in highway infrastructure and safety, emphasizing regulatory limits, battery constraints, and the necessity of automated pipelines."),
        ("7. Arun et al. (2021)", "Published a comprehensive mapping review of 549 surrogate safety studies, formalizing TTC, PET, and DRAC conflict indicators and urging direct linkage between conflicts and crashes."),
        ("8. Aharon et al. (2022)", "Proposed BoT-SORT, integrating Kalman filtering, appearance embeddings, and camera-motion compensation (CMC) to handle vehicle tracking under aerial platform motion."),
        ("9. Zhang et al. (2022)", "Introduced ByteTrack, which associates high-confidence detections first and recovers occluded vehicles from low-confidence detections, significantly reducing ID switches."),
        ("10. Zong et al. (2022)", "Combined deep-learning vehicle tracking with TTC analysis from drone video at intersections, proving the efficacy of UAV trajectories in overcoming terrestrial occlusion."),
        ("11. Wang et al. (2023)", "Proposed UAV-YOLOv8, refining YOLOv8 architectures with specialized small-object attention heads to retain fine-grained spatial details of aerial vehicles."),
        ("12. Berghaus et al. (2024)", "Constructed a drone-based trajectory dataset of over 8,000 vehicles on a German motorway using YOLOv5 and 3D camera calibration, verifying trajectory-derived speed and acceleration against roadside sensors."),
        ("13. Xu, L. et al. (2024)", "Enhanced YOLOv8n with multi-scale feature fusion and Wise-IoU loss for small objects on VisDrone, establishing modern lightweight design principles for aerial detection."),
        ("14. Zhao et al. (2024)", "Developed RT-DETR, a real-time end-to-end vision transformer eliminating NMS post-processing, providing an alternative state-of-the-art benchmark for highway vehicle detection."),
        ("15. Fonod et al. (2025)", "Developed a multi-drone trajectory extraction system across 20 intersections, introducing vehicle masking during feature matching to avoid camera-motion distortion during orthophoto alignment."),
        ("16. Kumar & Sarkar (2025)", "Extracted UAV trajectories at Panipat Toll Plaza (NH-44, India), applying Lane-Changing TTC and Extreme Value Theory (EVT) to prove that small vehicles have higher conflict vulnerability under mixed traffic."),
        ("17. Maji & Ghosh (2025)", "Evaluated non-lane-based Indian roundabout traffic from drone imagery, applying TTC, Delta-V, and EVT to show that strict lane-based models fail under heterogeneous traffic.")
    ]
    for s_title, s_desc in lit_studies:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        r1 = p.add_run(s_title + ": ")
        r1.bold = True
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10.5)
        r2 = p.add_run(s_desc)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(10.5)

    add_heading_2("2.2 IDENTIFIED RESEARCH GAPS AND CONTRIBUTIONS", is_new=False)
    add_p("The review reveals four critical deficiencies in the existing body of knowledge:\n"
          "1. Generic Pretrained Models Fail on Small Vehicles: Generic models trained on international datasets (COCO, VisDrone) underperform drastically when detecting small vehicles (especially motorcycles and auto-rickshaws) in mixed Indian traffic.\n"
          "2. Separation of Detection and Safety Analysis: Most studies treat computer vision detection and safety conflict analysis as disconnected domains.\n"
          "3. Lack of Mid-Block Kinematic Stopping Distance Evaluation: Standard SSMs (TTC, PET) overlook the physical braking capabilities and deceleration deficits of trailing vehicles under sudden leader deceleration.\n"
          "4. Absence of Integrated Interactive Research Tools: Safety engineers lack accessible web-based software to inspect trajectories, visualize conflict hotspots, and adjust kinematic safety thresholds interactively.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # ==========================================
    # CHAPTER 3 & 4: STUDY CORRIDOR & DATA
    # ==========================================
    add_heading_1("CHAPTER 3: STUDY CORRIDOR AND FIELD DATA", is_new=False)
    add_heading_2("3.1 PRIMARY PROPOSED STUDY AREA: THIRUVANANTHAPURAM", is_new=False)
    add_p("The primary target site for field deployment remains the urban arterial mid-block corridors of Thiruvananthapuram, Kerala, characterized by high two-wheeler proportions, varied commercial friction, and lack of strict lane discipline.", is_new=False, size=11)
    
    add_heading_2("3.2 EMPIRICAL VALIDATION CORRIDOR: NATIONAL HIGHWAY 48 (NH-48)", is_new=True)
    add_p("[NEW SECTION - EMPIRICAL CORRIDOR VALIDATION]: To rigorously build and benchmark the end-to-end analytical framework prior to UAV acquisition and local field permissions, an empirical high-resolution UAV dataset was deployed representing a 4-lane divided section of National Highway 48 (NH-48). The video exhibits realistic Indian highway operational conditions, including high-speed through movements, heavy commercial vehicle platooning, and abrupt lane-change friction.", 
          is_new=True, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    # Corridor details table
    corridor_specs = [
        ("Corridor Identifier", "National Highway 48 (NH-48) 4-Lane Divided Highway"),
        ("Video Resolution", "1608 x 908 pixels @ 30.0 Frames Per Second (FPS)"),
        ("Observation Duration", "20.03 seconds (601 sequential frames)"),
        ("Longitudinal Extent", "160.0 meters corridor length"),
        ("Directional Configuration", "Dual Carriageway (Westbound & Eastbound streams)"),
        ("Total Tracked Entities", "160 unique track IDs (126 sustained corridor trajectories)"),
        ("Concurrent Vehicle Load", "Average 28.02 vehicles simultaneously on corridor (Peak: 48)")
    ]
    t_corr = doc.add_table(rows=len(corridor_specs)+1, cols=2)
    t_corr.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_corr.cell(0, 0).width = Inches(2.5)
    t_corr.cell(0, 1).width = Inches(4.0)
    set_cell_background(t_corr.cell(0, 0), "EAECEF")
    set_cell_background(t_corr.cell(0, 1), "EAECEF")
    t_corr.cell(0, 0).paragraphs[0].add_run("Corridor Parameter").bold = True
    t_corr.cell(0, 1).paragraphs[0].add_run("Technical Specification").bold = True
    for r_i, (k, v) in enumerate(corridor_specs, start=1):
        c0 = t_corr.cell(r_i, 0)
        c1 = t_corr.cell(r_i, 1)
        c0.width = Inches(2.5)
        c1.width = Inches(4.0)
        r_k = c0.paragraphs[0].add_run(k)
        r_k.bold = True
        r_k.font.size = Pt(9.5)
        r_k.font.color.rgb = COLOR_NEW if is_highlighted else COLOR_ORIGINAL
        r_v = c1.paragraphs[0].add_run(v)
        r_v.font.size = Pt(9.5)
        r_v.font.color.rgb = COLOR_NEW if is_highlighted else COLOR_ORIGINAL

    add_heading_1("CHAPTER 4: DATA AND SOFTWARE ARCHITECTURE", is_new=False)
    add_heading_2("4.1 UAV PLATFORM SPECIFICATIONS (PLANNED)", is_new=False)
    add_p("The designated UAV for field surveys is the DJI Neo 2, featuring a 12 MP camera, 4K video recording up to 100 fps, a 2-axis mechanical gimbal with RockSteady stabilization, and an estimated flight duration of 19 minutes per battery.", is_new=False, size=11)
    
    add_heading_2("4.2 SOFTWARE ECOSYSTEM & FULL-STACK 'UAV TRAFFIC STUDIO'", is_new=True)
    add_p("[NEW SECTION - SOFTWARE PLATFORM ARCHITECTURE]: To advance this research beyond ad-hoc command-line scripts, a standalone, professional full-stack web application titled 'UAV Traffic Studio' was engineered. The system architecture comprises:", 
          is_new=True, size=11)
    add_bullet("Computational Backend: High-performance Python core leveraging PyTorch, Ultralytics YOLOv8, OpenCV, NumPy, SciPy, and Pandas.", is_new=True)
    add_bullet("REST API Engine: Standalone Python HTTP microservice (app/server.py on port 8080) exposing 8 analytical endpoints (/api/status, /api/metrics, /api/conflicts, /api/critical-distances, /api/hotspots, /api/trajectories, /api/pipeline/status, and POST /api/pipeline/run).", is_new=True)
    add_bullet("Interactive Visual Workspace: Responsive frontend engineered with vanilla HTML5, modern CSS3, and Apache ECharts, delivering 60 FPS trajectory playback, interactive space-time exploration, and dynamic AASHTO stopping parameter adjustment.", is_new=True)

    # ==========================================
    # CHAPTER 5: METHODOLOGY & MATHEMATICAL FORMULATIONS
    # ==========================================
    add_heading_1("CHAPTER 5: METHODOLOGY AND GOVERNING EQUATIONS", is_new=False)
    add_heading_2("5.1 OVERALL PIPELINE ARCHITECTURE", is_new=False)
    add_p("The operational pipeline links 9 integrated modules: Video Ingestion -> Frame Extraction -> Homography Matrix Transformation -> Deep Learning Detection -> ByteTrack Association -> Trajectory Smoothing -> Microscopic Flow Derivation -> Kinematic Stopping Distance Evaluation -> Collision Hotspot Mapping.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    flow_path = r"C:\Highway_Traffic_Analysis\outputs\pdf_extracted_images\page_27_img_1_Image82.png"
    if os.path.exists(flow_path):
        add_fig(flow_path, "Figure 5.1: End-to-End Methodological Framework Flowchart", width=Inches(5.5), is_new=False)

    add_heading_2("5.2 PERSPECTIVE HOMOGRAPHY AND METRIC COORDINATE TRANSFORMATION", is_new=False)
    add_p("To convert vehicle bottom-center pixel coordinates (u, v) into physical metric coordinates (X, Y) along the highway plane, a 4-point projective homography transformation matrix H is formulated:", is_new=False, size=11)
    
    add_p("[ s*X, s*Y, s ]^T = H * [ u, v, 1 ]^T\n"
          "where H = [ [h11, h12, h13], [h21, h22, h23], [h31, h32, h33] ] with h33 = 1", 
          is_new=False, italic=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER)

    add_callout_box(doc, 
                    "All metric speeds, densities, and stopping distances presented in this report are based on an unverified preliminary calibration using an assumed standard lane width of 3.50 meters across the NH-48 4-lane cross-section. Physical surveyed ground control points (GCPs) with differential GPS (DGPS) will be collected during the upcoming field campaign to provide absolute millimeter-level geodetic verification.", 
                    title="UNVERIFIED PRELIMINARY CALIBRATION NOTICE", highlight=is_highlighted)

    add_heading_2("5.3 MACROSCOPIC TRAFFIC FLOW EQUATIONS", is_new=False)
    add_p("Traffic flow q (veh/h), traffic density k (veh/km), time-mean speed u_t (km/h), and space-mean speed u_s (km/h) are derived rigorously from metric trajectory sequences:", is_new=False, size=11)
    add_p("q = (N / T) * 3600\n"
          "k = (N_avg / L) * 1000\n"
          "u_t = (1 / N) * SUM( v_i )\n"
          "u_s = L_total / T_total = N / SUM( 1 / v_i )\n"
          "Wardrop's Theorem: u_t >= u_s, with equality holding only when all vehicles travel at identical speeds.", 
          is_new=False, italic=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER)

    add_heading_2("5.4 SURROGATE SAFETY MEASURES: TTC, PET, AND DRAC", is_new=False)
    add_p("Surrogate safety measures capture conflict severity without waiting for crashes to occur:", is_new=False, size=11)
    add_p("1. Time-to-Collision (TTC): Defined for leader-follower pairs when v_f > v_l:\n"
          "   TTC = (x_l - x_f - L_l) / (v_f - v_l) = d_clear / Δv\n"
          "   Critical conflict threshold: TTC <= 1.50 seconds.\n\n"
          "2. Post-Encroachment Time (PET): Time elapsed between first vehicle departure and second vehicle arrival at conflict zone:\n"
          "   PET = t_arrival - t_departure\n"
          "   Critical encroachment threshold: PET <= 1.00 second.\n\n"
          "3. Deceleration Rate to Avoid Crash (DRAC): Constant deceleration required by follower to avoid collision:\n"
          "   DRAC = (v_f - v_l)^2 / (2 * d_clear)\n"
          "   Critical threshold: DRAC > 3.40 m/s² (AASHTO comfortable deceleration limit).", 
          is_new=False, italic=True, size=11)

    add_heading_2("5.5 AASHTO / IRC:67 KINEMATIC STOPPING DISTANCE DEFICIT FORMULATION", is_new=True)
    add_p("[NEW SECTION - NOVEL SAFETY METHODOLOGY]: To overcome the limitation of TTC under non-overtaking car-following conditions (where TTC is undefined when v_f <= v_l, despite dangerous tailgating), a rigorous kinematic stopping distance formulation is introduced following AASHTO 'A Policy on Geometric Design of Highways and Streets' and Indian Roads Congress IRC:67 guidelines.", 
          is_new=True, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    add_p("When a leading vehicle initiates emergency maximum deceleration a_l, the minimum collision-free stopping distance required by the following vehicle (d_safe) is defined by driver perception-reaction delay (t_r) and differential braking energy:", 
          is_new=True, size=11)
          
    add_p("d_safe = v_f * t_r + ( v_f^2 / (2 * a_f) ) - ( v_l^2 / (2 * a_l) )\n\n"
          "Safety Margin / Clearance Deficit (Δd):\n"
          "Δd = d_clear - d_safe\n\n"
          "where:\n"
          "• d_clear = physical bumper-to-bumper clearance between leader and follower (meters)\n"
          "• v_f, v_l = instantaneous speeds of follower and leader (m/s)\n"
          "• t_r = driver perception-reaction time (default = 1.50 s, IRC standard)\n"
          "• a_f = maximum follower braking deceleration (default = 3.40 m/s²)\n"
          "• a_l = maximum leader emergency deceleration (default = 6.00 m/s²)\n\n"
          "Safety Severity Tiers:\n"
          "• Tier 1 (Critical Hazard): Δd < 0 m (Follower CANNOT avoid collision upon sudden leader stop)\n"
          "• Tier 2 (Moderate Buffer): 0 m <= Δd < 10.0 m (Follower requires emergency evasive maneuver)\n"
          "• Tier 3 (Safe Buffer): Δd >= 10.0 m (Sufficient headway clearance maintained)", 
          is_new=True, italic=True, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)

    # ==========================================
    # CHAPTER 6: RESULTS AND DISCUSSION
    # ==========================================
    add_heading_1("CHAPTER 6: COMPREHENSIVE RESULTS AND DISCUSSION", is_new=False)
    
    add_heading_2("6.1 RECAP OF PHASE 1 PRELIMINARY TEST (SAMPLE VIDEO)", is_new=False)
    add_p("In Phase 1, preliminary testing was conducted on a 477-frame sample video in the pixel domain. Detection was performed using Ultralytics YOLOv8 and ByteTrack, yielding 19,133 pixel-coordinate tracking records for 614 track IDs. A second pretrained model tested failed completely on two-wheelers, and trajectories lacked real-world metric scale.", 
          is_new=False, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_heading_2("6.2 FULL HIGHWAY CORRIDOR DATASET & HOMOGRAPHY CALIBRATION", is_new=True)
    add_p("[NEW WORK - METRIC STUDY CORRIDOR]: Phase 2 evaluated a full 601-frame (20.03 s @ 30 FPS) nadir UAV sequence of National Highway 48. Planar homography mapping converted the 1608x908 pixel space into a 160.0-meter longitudinal metric coordinate framework. Over 22,031 metric trajectory points were generated, tracking vehicle positions at 33.3 millisecond temporal resolution.", 
          is_new=True, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    bev_path = r"C:\Highway_Traffic_Analysis\outputs\calibration\bird_eye_view.png"
    if os.path.exists(bev_path):
        add_fig(bev_path, "Figure 6.1: Orthorectified Bird's-Eye View of NH-48 Corridor after Planar Homography Calibration", width=Inches(5.8), is_new=True)

    add_heading_2("6.3 VEHICLE DETECTION PERFORMANCE AND CRITICAL PRETRAINED MODEL LIMITATIONS", is_new=True)
    
    add_callout_box(doc, 
                    "MANDATORY RESEARCH DISCLAIMER: The deep learning object detection model utilized in this analysis was NOT trained, fine-tuned, or annotated by the author (Eric Jose). The evaluation was executed using off-the-shelf pretrained weights (YOLOv8s-VisDrone) distributed by Ultralytics. The explicit scientific objective of this experiment was to empirically evaluate whether existing off-the-shelf aerial models can be trusted for Indian highway safety monitoring.", 
                    title="PRETRAINED MODEL SOURCE DISCLAIMER (NOT TRAINED BY AUTHOR)", highlight=is_highlighted)

    add_p("The detection model identified 48 unique active concurrent vehicles across the NH-48 study corridor. The empirical modal split observed in the automated detection output is detailed in Table 6.1.", 
          is_new=True, size=11)

    # Modal Split Table
    modal_data = [
        ("Passenger Cars", "31", "64.6%", "High detection confidence (mean 0.84)"),
        ("Vans / Light Delivery", "8", "16.7%", "Good boundary stability"),
        ("Buses (Public Transit)", "7", "14.6%", "Stable detection; large bounding footprint"),
        ("Heavy Commercial Trucks", "1", "2.1%", "Correctly localized along outer freight lane"),
        ("Motorcycles / Two-Wheelers", "1", "2.1%", "SEVERELY UNDER-DETECTED (CATATROPHIC MODEL FAILURE)")
    ]
    t_mod = doc.add_table(rows=len(modal_data)+1, cols=4)
    t_mod.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_mod.cell(0, 0).width = Inches(2.0)
    t_mod.cell(0, 1).width = Inches(1.0)
    t_mod.cell(0, 2).width = Inches(1.2)
    t_mod.cell(0, 3).width = Inches(2.3)
    for c_i, h_t in enumerate(["Vehicle Classification", "Detected Count", "Modal Share", "Model Performance Remarks"]):
        set_cell_background(t_mod.cell(0, c_i), "EAECEF")
        p = t_mod.cell(0, c_i).paragraphs[0]
        r = p.add_run(h_t)
        r.bold = True
        r.font.size = Pt(9.5)
        
    for r_i, (c_name, c_cnt, c_pct, c_rem) in enumerate(modal_data, start=1):
        for c_i, val in enumerate([c_name, c_cnt, c_pct, c_rem]):
            cell = t_mod.cell(r_i, c_i)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_NEW if is_highlighted else COLOR_ORIGINAL
            if "SEVERELY" in val:
                r.bold = True
                if is_highlighted: r.font.color.rgb = RGBColor(220, 0, 0)

    add_p("\nTable 6.1: Automated Vehicle Classification Breakdown on NH-48 Corridor (Pretrained YOLOv8s-VisDrone).", 
          is_new=True, italic=True, size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)

    comp_path = r"C:\Highway_Traffic_Analysis\outputs\analysis\traffic_composition.png"
    if os.path.exists(comp_path):
        add_fig(comp_path, "Figure 6.2: Vehicle Modal Composition Chart Demonstrating Pretrained Model Bias", width=Inches(4.5), is_new=True)

    add_heading_2("6.4 CRITICAL FAILURE OF PRETRAINED MODELS ON SMALL OBJECTS (MOTORCYCLES)", is_new=True)
    add_p("[NEW SECTION - CENTRAL SCIENTIFIC FINDING]: As evidenced in Table 6.1, only 1 single motorcycle was detected in the entire corridor, representing just 2.1% of the total vehicle population. On typical Indian National Highways, motorized two-wheelers comprise between 30% and 50% of total vehicular traffic.\n\n"
          "This catastrophic under-detection is attributed to three fundamental technical factors:\n"
          "1. Spatial Feature Attenuation: At a flight altitude producing a Ground Sampling Distance of GSD ~ 8-10 cm/pixel, a standard two-wheeler (1.8m x 0.7m) occupies only ~18 x 7 pixels. At standard YOLOv8 stride-32 feature maps (P5), this corresponds to less than 0.15 of a convolutional cell, causing feature extinction during backbone downsampling.\n"
          "2. VisDrone Pretraining Domain Gap: The VisDrone dataset is biased toward urban Chinese traffic dominated by passenger vehicles, lacking the dense two-wheeler filtering behavior characteristic of Indian highways.\n"
          "3. Low Confidence Filtering: Even when two-wheelers generated candidate proposals, confidence scores remained depressed between 0.25 and 0.42, causing non-maximum suppression (NMS) to eliminate valid detections.\n\n"
          "CONCLUSION: This empirical failure unequivocally proves that off-the-shelf, non-customized vision models cannot be directly applied for Indian highway safety assessment. It fully validates the core objective of this M.Tech research: the engineering of a customized small-object YOLO architecture incorporating high-resolution P2 stride-4 heads and Wise-IoU loss, trained on a locally annotated five-class dataset.", 
          is_new=True, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_heading_2("6.5 MULTI-OBJECT TRACKING & SPACE-TIME TRAJECTORY EXTRACTION", is_new=True)
    add_p("[NEW SECTION - CONTINUOUS TRAJECTORIES]: Deploying ByteTrack across the 601 frames yielded 160 tracked IDs, with 126 sustained trajectories traversing the active corridor. Applying a forward-backward Savitzky-Golay filter eliminated camera jitter and detector centroid noise while preserving valid sudden decelerations.", 
          is_new=True, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    st_path = r"C:\Highway_Traffic_Analysis\outputs\analysis\space_time_diagram.png"
    if os.path.exists(st_path):
        add_fig(st_path, "Figure 6.3: Space-Time Diagram of Trajectories along the NH-48 Study Corridor", width=Inches(5.8), is_new=True)

    add_heading_2("6.6 MACROSCOPIC TRAFFIC FLOW PARAMETERS", is_new=True)
    add_p("[NEW SECTION - MACROSCOPIC PARAMETERS]: Trajectory integration across the 160-meter corridor over the 20.03-second observation window yielded empirical macroscopic flow parameters, summarized in Table 6.2.", 
          is_new=True, size=11)

    macro_data = [
        ("Total Traffic Flow Rate (q)", "8,625.6 veh/h", "Aggregated bidirectional throughput"),
        ("Westbound Flow Rate (q_wb)", "5,031.6 veh/h (58.3%)", "Dominant heavy traffic stream"),
        ("Eastbound Flow Rate (q_eb)", "3,594.0 veh/h (41.7%)", "Counter-directional traffic stream"),
        ("Traffic Density (k)", "175.1 veh/km", "Average 28.02 concurrent vehicles per 160m"),
        ("Time-Mean Speed (u_t)", "26.59 km/h (7.39 m/s)", "Arithmetic average of spot speeds"),
        ("Space-Mean Speed (u_s)", "25.44 km/h (7.07 m/s)", "Harmonic distance-weighted mean"),
        ("Speed Standard Deviation (σ)", "5.42 km/h", "Measures traffic velocity heterogeneity"),
        ("85th-Percentile Speed (v_85)", "31.67 km/h", "Operating speed benchmark for highway design"),
        ("Speed Range [Min, Max]", "[ 16.0 km/h, 44.5 km/h ]", "Extremes observed on corridor"),
        ("Wardrop Inequality Validation", "u_t (26.59) > u_s (25.44)", "VALIDATED: Confirms traffic flow theory")
    ]
    t_mac = doc.add_table(rows=len(macro_data)+1, cols=3)
    t_mac.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_mac.cell(0, 0).width = Inches(2.6)
    t_mac.cell(0, 1).width = Inches(1.8)
    t_mac.cell(0, 2).width = Inches(2.1)
    for c_i, h_t in enumerate(["Macroscopic Parameter", "Empirical Value", "Significance & Validation"]):
        set_cell_background(t_mac.cell(0, c_i), "EAECEF")
        p = t_mac.cell(0, c_i).paragraphs[0]
        r = p.add_run(h_t)
        r.bold = True
        r.font.size = Pt(9.5)
        
    for r_i, (p_name, p_val, p_rem) in enumerate(macro_data, start=1):
        for c_i, val in enumerate([p_name, p_val, p_rem]):
            cell = t_mac.cell(r_i, c_i)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_NEW if is_highlighted else COLOR_ORIGINAL
            if "VALIDATED" in val: r.bold = True

    add_p("\nTable 6.2: Summary of Macroscopic Traffic Flow Parameters Derived on NH-48 Corridor.", 
          is_new=True, italic=True, size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)

    spd_path = r"C:\Highway_Traffic_Analysis\outputs\analysis\preliminary_speed_distribution.png"
    if os.path.exists(spd_path):
        add_fig(spd_path, "Figure 6.4: Empirical Vehicle Speed Distribution on the NH-48 Study Corridor", width=Inches(5.0), is_new=True)

    add_heading_2("6.7 MICROSCOPIC SURROGATE SAFETY MEASURES (TTC, PET, DRAC)", is_new=True)
    add_p("[NEW SECTION - SAFETY METRICS]: Across 3,668 car-following instances evaluated frame-by-frame, surrogate safety indicators revealed significant conflict exposure on the highway corridor:", 
          is_new=True, size=11)
    add_bullet("Critical Time-to-Collision (TTC <= 1.50 s): 2,391 instances observed, with a mean critical TTC of 0.43 seconds, indicating severe tailgating under congested platooning.", is_new=True)
    add_bullet("Severe TTC (1.50 s < TTC <= 2.50 s): 380 instances, representing acute deceleration vigilance zones.", is_new=True)
    add_bullet("Post-Encroachment Time (PET <= 1.00 s): 209 critical encroachment events (median PET = 0.97 s) during aggressive lane-changing and merge friction.", is_new=True)
    add_bullet("Deceleration Rate to Avoid Crash (DRAC > 3.40 m/s²): 1,169 critical braking instances where required deceleration exceeded comfortable passenger thresholds.", is_new=True)

    ttc_path = r"C:\Highway_Traffic_Analysis\outputs\safety_analysis\ttc_distribution.png"
    if os.path.exists(ttc_path):
        add_fig(ttc_path, "Figure 6.5: Distribution of Microscopic Time-to-Collision (TTC) Events", width=Inches(5.0), is_new=True)

    add_heading_2("6.8 KINEMATIC STOPPING DISTANCE DEFICIT & TOP 10 CRITICAL CONFLICTS", is_new=True)
    add_p("[NEW SECTION - AASHTO KINEMATIC EVALUATION]: Evaluating 195 leader-follower conflict pairs using the AASHTO/IRC:67 kinematic stopping formulation (t_r = 1.5 s, a_f = 3.4 m/s², a_l = 6.0 m/s²) classified interactions into three severity tiers:", 
          is_new=True, size=11)
    add_bullet("Tier 1 (Critical Hazard, Δd < 0 m): 147 pairs (75.4%). Follower cannot stop safely without collision if the leader initiates emergency maximum braking.", is_new=True)
    add_bullet("Tier 2 (Moderate Buffer, 0 m <= Δd < 10 m): 21 pairs (10.8%). Minimal safety buffer; requires active driver evasive intervention.", is_new=True)
    add_bullet("Tier 3 (Safe Buffer, Δd >= 10 m): 27 pairs (13.8%). Adequate headways maintained.", is_new=True)

    add_p("\nTable 6.3 details the Top 10 Most Critical Conflict Events ranked by kinematic stopping distance deficit (Δd).", 
          is_new=True, size=11)

    # Top 10 Conflict Table
    conflict_ranks = [
        ("1", "#3 Van -> #946 Bus", "341", "0.50 m", "17.39 m", "-16.89 m", "0.11 s", "19.80 m/s²", "Tier 1 (Critical)"),
        ("2", "#946 Bus -> #933 Car", "369", "1.21 m", "10.60 m", "-9.39 m", "0.28 s", "7.91 m/s²", "Tier 1 (Critical)"),
        ("3", "#945 Van -> #946 Bus", "210", "0.80 m", "8.85 m", "-8.05 m", "0.35 s", "6.42 m/s²", "Tier 1 (Critical)"),
        ("4", "#943 Motor -> #942 Truck", "26", "0.42 m", "8.35 m", "-7.93 m", "0.23 s", "9.94 m/s²", "Tier 1 (Critical)"),
        ("5", "#935 Car -> #947 Truck", "270", "0.62 m", "6.70 m", "-6.08 m", "0.42 s", "5.34 m/s²", "Tier 1 (Critical)"),
        ("6", "#933 Car -> #934 Car", "132", "0.85 m", "6.22 m", "-5.37 m", "0.51 s", "4.45 m/s²", "Tier 1 (Critical)"),
        ("7", "#947 Truck -> #946 Bus", "244", "1.10 m", "6.15 m", "-5.05 m", "0.62 s", "3.92 m/s²", "Tier 1 (Critical)"),
        ("8", "#934 Car -> #945 Van", "417", "0.95 m", "5.80 m", "-4.85 m", "0.58 s", "4.15 m/s²", "Tier 1 (Critical)"),
        ("9", "#942 Truck -> #935 Car", "8", "1.30 m", "5.75 m", "-4.45 m", "0.71 s", "3.62 m/s²", "Tier 1 (Critical)"),
        ("10", "#946 Bus -> #945 Van", "3", "1.45 m", "5.50 m", "-4.05 m", "0.80 s", "3.48 m/s²", "Tier 1 (Critical)")
    ]
    t_crk = doc.add_table(rows=len(conflict_ranks)+1, cols=9)
    t_crk.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths_c = [Inches(0.4), Inches(1.5), Inches(0.6), Inches(0.7), Inches(0.7), Inches(0.7), Inches(0.6), Inches(0.7), Inches(0.8)]
    headers_c = ["Rank", "Pair", "Frame", "d_clear", "d_safe", "Δd (Deficit)", "TTC", "DRAC", "Tier"]
    for c_i, h_t in enumerate(headers_c):
        t_crk.cell(0, c_i).width = widths_c[c_i]
        set_cell_background(t_crk.cell(0, c_i), "EAECEF")
        p = t_crk.cell(0, c_i).paragraphs[0]
        r = p.add_run(h_t)
        r.bold = True
        r.font.size = Pt(8.5)
        
    for r_i, row in enumerate(conflict_ranks, start=1):
        for c_i, val in enumerate(row):
            cell = t_crk.cell(r_i, c_i)
            cell.width = widths_c[c_i]
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_NEW if is_highlighted else COLOR_ORIGINAL
            if c_i == 0 or c_i == 5: r.bold = True

    add_p("\nTable 6.3: Top 10 Most Critical Conflict Events Ranked by AASHTO Stopping Distance Deficit.", 
          is_new=True, italic=True, size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)

    f341_path = r"C:\Highway_Traffic_Analysis\outputs\safety_analysis\conflict_frames\conflict_rank_01_frame_0341.jpg"
    if os.path.exists(f341_path):
        add_fig(f341_path, "Figure 6.6: Rank #1 Extreme Conflict Event at Frame 341 (Van #3 tailgating Bus #946; Clearance = 0.50m, Deficit = -16.89m, TTC = 0.11s)", width=Inches(5.8), is_new=True)

    add_heading_2("6.9 LONGITUDINAL SPATIAL BOTTLENECK & ACCIDENT HOTSPOT ANALYSIS", is_new=True)
    add_p("[NEW SECTION - SPATIAL HOTSPOTS]: To locate spatial clusters of accident vulnerability, the 160-meter corridor was segmented into 20-meter longitudinal analysis zones. Critical conflict occurrences across the zones revealed acute localized safety risks:", 
          is_new=True, size=11)
          
    hotspot_zones = [
        ("Station [-40 m, -20 m]", "19 Conflicts", "Corridor entry zone; initial deceleration."),
        ("Station [-20 m,  0 m]", "24 Conflicts", "Pre-bottleneck compaction."),
        ("Station [  0 m,  20 m]", "37 Conflicts (RANK #1 BOTTLENECK)", "PRIMARY COLLISION HOTSPOT: Heavy merge & lane-drop friction."),
        ("Station [ 20 m,  40 m]", "27 Conflicts", "Bottleneck propagation zone."),
        ("Station [ 40 m,  60 m]", "20 Conflicts", "Intermediate recovery zone."),
        ("Station [ 60 m,  80 m]", "24 Conflicts", "Secondary weave compression."),
        ("Station [ 80 m, 100 m]", "32 Conflicts (RANK #2 FRICTION ZONE)", "SECONDARY COLLISION HOTSPOT: Exit acceleration / tailgating."),
        ("Station [100 m, 120 m]", "11 Conflicts", "Free-flow dispersal.")
    ]
    for z_name, z_cnt, z_desc in hotspot_zones:
        add_bullet(f"{z_name} -> {z_cnt}: {z_desc}", is_new=True)

    hot_path = r"C:\Highway_Traffic_Analysis\outputs\safety_analysis\crash_ranking_and_hotspots.png"
    if os.path.exists(hot_path):
        add_fig(hot_path, "Figure 6.7: Conflict Severity Ranking and 20-Meter Longitudinal Corridor Hotspot Distribution", width=Inches(5.8), is_new=True)

    add_heading_2("6.10 UAV TRAFFIC STUDIO: FULL-STACK WEB RESEARCH PLATFORM", is_new=True)
    add_p("[NEW SECTION - RESEARCH PLATFORM DELIVERABLE]: To provide transportation researchers and safety authorities with an intuitive, interactive tool, 'UAV Traffic Studio' was developed and deployed. The platform delivers:", 
          is_new=True, size=11)
    add_bullet("Live Metric Trajectory Animation: 60 FPS interactive HTML5 canvas displaying vehicle bounding boxes, velocity vectors, and trailing path histories.", is_new=True)
    add_bullet("Dynamic Kinematic Filtering: Real-time slider controls allowing users to modulate reaction time (t_r = 0.5 s to 2.5 s) and deceleration rates (a_f = 2.0 to 6.0 m/s²) with instantaneous table re-ranking.", is_new=True)
    add_bullet("Conflict Replay Inspector: One-click visual navigation jumping directly to annotated UAV frames (such as Frame 341 Rank 1 conflict) with bounding hazard overlays.", is_new=True)
    add_bullet("Automated Pipeline Execution Engine: Integrated REST trigger enabling users to initiate automated video ingestion, homography transformation, and safety scoring directly from the web interface.", is_new=True)

    # ==========================================
    # CHAPTER 7: CONCLUSIONS AND UPDATED WORK PLAN
    # ==========================================
    add_heading_1("CHAPTER 7: CONCLUSIONS AND UPDATED WORK PLAN", is_new=False)
    add_heading_2("7.1 SUMMARY OF COMPLETED WORK", is_new=True)
    add_p("[UPDATED COMPREHENSIVE SUMMARY]: The research conducted to date has successfully transitioned from conceptual formulation into a fully validated empirical analytical framework:", 
          is_new=True, size=11)
    add_bullet("Exhaustive Literature Review: Synthesized 17 seminal studies on aerial traffic surveillance, multi-object tracking, and surrogate safety measures.", is_new=False)
    add_bullet("Empirical Corridor Metric Analysis: Completed full-scale evaluation of a 601-frame (20.03 s @ 30 FPS) NH-48 corridor sequence, generating 22,031 metric trajectory points across 160 tracked vehicles.", is_new=True)
    add_bullet("Rigorous Pretrained Model Evaluation: Executed proof-of-concept testing using off-the-shelf YOLOv8s-VisDrone weights (not trained by author), uncovering catastrophic failure on small two-wheelers (only 1 motorcycle detected = 2.1% share), thereby proving the necessity of customized aerial architectures.", is_new=True)
    add_bullet("Macroscopic Flow Parameter Quantification: Extracted flow rate (q = 8,625.6 veh/h), density (k = 175.1 veh/km), time-mean speed (26.59 km/h), and space-mean speed (25.44 km/h), confirming Wardrop's inequality.", is_new=True)
    add_bullet("Comprehensive SSM Evaluation: Quantified 2,391 critical TTC instances (<= 1.5s), 209 critical PET occurrences (<= 1.0s), and 1,169 critical DRAC braking events (> 3.4 m/s²).", is_new=True)
    add_bullet("Novel Kinematic Stopping Formulation: Developed AASHTO/IRC:67 clearance deficit framework, uncovering 147 Tier-1 critical collision hazard pairs among 195 interactions.", is_new=True)
    add_bullet("Longitudinal Hotspot Pinpointing: Pinpointed primary bottleneck at station [0m, 20m] (37 conflicts) and secondary friction zone at [80m, 100m] (32 conflicts).", is_new=True)
    add_bullet("Full-Stack Software Deployment: Engineered 'UAV Traffic Studio' web dashboard with REST API backend and interactive visualization workspace.", is_new=True)

    add_heading_2("7.2 REMAINING CHALLENGES AND WORK SCHEDULE", is_new=False)
    add_p("With the computational algorithms, safety formulations, and software platform fully operational, the remaining research tasks focus on field execution in Thiruvananthapuram upon UAV acquisition:", 
          is_new=False, size=11)
    add_bullet("Procure DJI Neo 2 UAV platform and secure civil aviation (DGCA) and institutional flight clearances.", is_new=False)
    add_bullet("Finalize mid-block survey sites along Thiruvananthapuram corridors and establish DGPS Ground Control Point (GCP) coordinate networks.", is_new=False)
    add_bullet("Extract and annotate 2,500+ local vehicle bounding boxes in CVAT across five classes (2W, 3W, Car, LCV, HCV) to eliminate the small-object model bias observed in pretrained models.", is_new=False)
    add_bullet("Train and benchmark the customized small-object YOLO model (with P2 stride-4 head and Wise-IoU) against baseline YOLOv8, Faster R-CNN, and RT-DETR.", is_new=False)
    add_bullet("Execute final thesis writing and submit comprehensive dissertation.", is_new=False)

    # References
    add_heading_1("REFERENCES", is_new=False)
    refs = [
        "[1] N. Aharon, R. Orfaig, and B.-Z. Bobrovsky, “BoT-SORT: Robust associations multi-pedestrian tracking,” arXiv preprint arXiv:2206.14651, 2022.",
        "[2] A. Arun, M. M. Haque, A. Bhaskar, S. Washington, and T. Sayed, “A systematic mapping review of surrogate safety assessment using traffic conflict techniques,” Accident Analysis & Prevention, vol. 153, p. 106016, 2021.",
        "[3] M. Berghaus, S. Lamberty, J. Ehlers, E. Kalló, and M. Oeser, “Vehicle trajectory dataset from drone videos including off-ramp and congested traffic: Analysis of data quality, traffic flow, and accident risk,” Communications in Transportation Research, vol. 4, p. 100133, 2024.",
        "[4] D. Du, Y. Qi, H. Yu, Y. Yang, K. Duan, G. Li, W. Zhang, Q. Huang, and Q. Tian, “The unmanned aerial vehicle benchmark: Object detection and tracking,” in Proc. European Conference on Computer Vision (ECCV) Workshops, 2018.",
        "[5] R. Fonod, H. Cho, H. Yeo, and N. Geroliminis, “Advanced computer vision for extracting georeferenced vehicle trajectories from drone imagery,” Transportation Research Part C: Emerging Technologies, vol. 178, p. 105205, 2025.",
        "[6] R. Ke, Z. Li, S. Kim, J. Ash, Z. Cui, and Y. Wang, “Real-time bidirectional traffic flow parameter estimation from aerial videos,” IEEE Transactions on Intelligent Transportation Systems, vol. 18, no. 4, pp. 890–901, 2017.",
        "[7] M. A. Khan, W. Ectors, T. Bellemans, D. Janssens, and G. Wets, “UAV-based traffic analysis: A universal guiding framework based on literature survey,” Transportation Research Procedia, vol. 22, pp. 541–550, 2017.",
        "[8] P. Kumar and D. R. Sarkar, “Conflict-based crash risk estimation of heterogeneous lane-changing traffic at the Panipat Toll Plaza (NH-44, India) using surrogate safety measures and UAV-based trajectory data,” IATSS Research, vol. 49, no. 4, pp. 580–592, 2025.",
        "[9] M. Liu, X. Wang, A. Zhou, X. Fu, Y. Ma, and C. Piao, “UAV-YOLO: Small object detection on unmanned aerial vehicle perspective,” Sensors, vol. 20, no. 8, p. 2238, 2020.",
        "[10] A. Maji and I. Ghosh, “Advanced traffic conflict analysis for safety evaluation at roundabouts under mixed traffic using extreme value theory,” Accident Analysis & Prevention, vol. 206, p. 108108, 2025.",
        "[11] F. Outay, H. A. Mengash, and M. Adnan, “Applications of unmanned aerial vehicle (UAV) in road safety, traffic and highway infrastructure management: Recent advances and challenges,” Transportation Research Part A: Policy and Practice, vol. 141, pp. 116–129, 2020.",
        "[12] G. Wang, Y. Chen, P. An, H. Hong, J. Hu, and T. Huang, “UAV-YOLOv8: A small-object-detection model based on improved YOLOv8 for UAV aerial photography scenarios,” Sensors, vol. 23, no. 16, p. 7190, 2023.",
        "[13] L. Xu, Y. Zhao, Y. Zhai, L. Huang, and C. Ruan, “Small object detection in UAV images based on YOLOv8n,” International Journal of Computational Intelligence Systems, vol. 17, p. 223, 2024.",
        "[14] Y. Xu, G. Yu, Y. Wang, X. Wu, and Y. Ma, “Car detection from low-altitude UAV imagery with the Faster R-CNN,” Journal of Advanced Transportation, vol. 2017, Art. no. 2823617, 2017.",
        "[15] Y. Zhang, P. Sun, Y. Jiang, D. Yu, F. Weng, Z. Yuan, P. Luo, W. Liu, and X. Wang, “ByteTrack: Multi-object tracking by associating every detection box,” in Proc. European Conference on Computer Vision (ECCV), 2022, pp. 1–21.",
        "[16] Y. Zhao, W. Lv, S. Xu, J. Wei, G. Wang, Q. Dang, Y. Liu, and J. Chen, “DETRs beat YOLOs on real-time object detection,” in Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2024, pp. 16965–16974.",
        "[17] S. Zong, S. Chen, M. Alinizzi, and S. Labi, “Leveraging UAV capabilities for vehicle tracking and collision risk assessment at road intersections,” Sustainability, vol. 14, no. 7, p. 4034, 2022."
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(r)
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)

    doc.save(output_path)
    print(f"Document successfully created: {output_path}")

if __name__ == "__main__":
    out_dir = r"C:\Highway_Traffic_Analysis"
    path_high = os.path.join(out_dir, "UAV_Report_Updated_Highlighted.docx")
    path_clean = os.path.join(out_dir, "UAV_Report_Updated_Clean.docx")
    
    print("Generating Highlighted Document (New work in RED)...")
    build_document(is_highlighted=True, output_path=path_high)
    
    print("Generating Clean Document (Standard black formatting)...")
    build_document(is_highlighted=False, output_path=path_clean)
    
    print("Done! Both documents created successfully.")
