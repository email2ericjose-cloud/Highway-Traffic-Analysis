from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO
from pathlib import Path
from copy import deepcopy
import re

BASE = Path(r'C:/Users/ericj/Downloads/interim report.docx')
SRC_A = Path(r'C:/Highway_Traffic_Analysis/UAV_Traffic_Safety_Interim_Report_Updated_Highlighted.docx')
SRC_B = Path(r'C:/Highway_Traffic_Analysis/UAV_Report_Updated_Highlighted.docx')
OUT = Path(r'C:/Highway_Traffic_Analysis/UAV_Traffic_Safety_Project_Report_Revised.docx')
doc = Document(BASE)


def replace_para(prefix, new_text):
    for p in doc.paragraphs:
        if p.text.strip().startswith(prefix):
            old = p.runs[0] if p.runs else None
            for r in list(p.runs):
                p._p.remove(r._r)
            run = p.add_run(new_text)
            if old is not None:
                run.bold, run.italic, run.underline = old.bold, old.italic, old.underline
                if old.font.name:
                    run.font.name = old.font.name
                if old.font.size:
                    run.font.size = old.font.size
            return p
    return None


# Keep the original report layout as the base and revise it for a presentation report.
for p in doc.paragraphs:
    if 'INTERIM PROJECT REPORT' in p.text:
        replace_para(p.text, 'PROJECT REPORT')
    elif 'interim project report' in p.text.lower():
        replace_para(p.text, p.text.replace('interim project report', 'project report').replace('Interim project report', 'Project report'))
    elif 'interim report' in p.text.lower():
        replace_para(p.text, p.text.replace('interim report', 'project report').replace('Interim report', 'Project report'))
replace_para('A review of 17 studies shows that UAV trajectories can support',
    'A review of 17 studies shows that UAV trajectories can support time-to-collision (TTC), post-encroachment time (PET) and extreme-value-based crash risk estimation, while small vehicles, camera motion and mixed traffic remain open problems. The study develops a locally annotated five-class vehicle dataset and an improved YOLO-based detection and tracking workflow for mid-block highway safety analysis. A preliminary National Highway 48 (NH-48) video was also processed: an assumed 3.50 m lane width was used to estimate image scale, yielding metric trajectories and exploratory traffic and conflict measures. These NH-48 measurements are provisional until the road width is physically checked. The earlier sample-video test remains a separate pixel-coordinate pilot. The report presents the methodology, the two distinct video analyses and the work still required for the Thiruvananthapuram field study.')
replace_para('This study proposes an improved YOLO-based detection and trajectory analysis framework',
    'This study proposes an improved YOLO-based vehicle detection and trajectory analysis framework for traffic safety assessment, crash-risk indicators and conflict hotspot identification on mid-block highway sections in Thiruvananthapuram. Five vehicle classes will be manually annotated in extracted UAV video frames using CVAT running in Docker. The annotations will train and evaluate a small-object detector, which will later be packaged in a Docker inference workflow. Measured road or lane width provides the pixel-to-metre scale needed for speed and other distance-based measures; orthomosaic generation is not required. This project report presents the study plan, annotation and model-development work, preliminary pipeline checks and expected outputs.')
replace_para('Safety measures cannot be computed reliably because pixel movement',
    'Speed and distance cannot be computed reliably from pixel movement until the image scale is calibrated using a measured road or lane width.')
replace_para('To acquire UAV imagery of highway segments and construct an annotated, DGPS-georeferenced vehicle dataset across five classes',
    'To acquire UAV imagery of highway segments and construct an annotated five-class vehicle dataset, with metric scale established from measured road or lane width')
replace_para('A single UAV (DJI Neo 2, planned) operated in nadir view with DGPS ground control points',
    'A single UAV (DJI Neo 2, planned) operated in nadir view, with road or lane width measured on site to establish image scale')
replace_para('A locally relevant, DGPS-georeferenced UAV vehicle dataset for Thiruvananthapuram traffic',
    'A locally relevant, metric-scaled UAV vehicle dataset for Thiruvananthapuram traffic, calibrated using measured road geometry')
replace_para('This chapter lists all the data required to achieve the objectives, together with the type, source, technical details and status of each dataset, followed by the UAV platform and the software used.',
    'This chapter lists the data required to achieve the objectives, including UAV video, measured road geometry for image-scale calibration, annotations and validation data, together with the UAV platform and software used.')
replace_para('Datasets marked “To be collected” cannot be obtained until the UAV is purchased and the mid-block sections are selected.',
    'Datasets marked “To be collected” depend on selection of the mid-block sections and acquisition of the planned UAV.')
replace_para('Nadir (top-down) video of the selected mid-block sections will be recorded with the DJI Neo 2 at a fixed altitude.',
    'Nadir (top-down) video of the selected mid-block sections will be recorded with the DJI Neo 2 at a fixed altitude. The video is the primary input for detection, tracking and trajectory extraction. A measured road or lane width visible in the video will be used to establish the pixel-to-metre scale; no orthomosaic is required.')
replace_para('Ground control points (GCPs) will be marked on the road surface',
    'The physical width of a clearly visible road or lane section will be measured on site and recorded as the reference distance for image-scale calibration. The selected reference should lie on the same road plane as the tracked vehicles and be visible in the nadir video. Additional width checks at separate locations can be used to assess scale consistency.')
replace_para('Lane lines, road edges and centrelines will be digitised from the orthomosaic',
    'Lane lines, road edges and centrelines will be identified from the video frames and measured road geometry. They will support lane assignment, trajectory checks and conflict-location summaries in a local road coordinate system.')
replace_para('Generation of the orthomosaic and digitisation of road geometry',
    'Measurement of a visible road or lane width and calibration of pixel distances to metres')
replace_para('Conversion of georeferenced coordinates to a metric projected system (for example UTM zone 43N, EPSG:32643)',
    'Expression of calibrated positions in a local metric road coordinate system, with the longitudinal axis aligned to the road')
replace_para('Photogrammetry software for the orthomosaic and GIS software for mapping, hotspot and LOS analysis (to be finalised)',
    'GIS software for mapping and hotspot or LOS summaries (to be finalised); photogrammetric orthomosaic processing is not part of the required workflow')
replace_para('The UAV has not been purchased, so no field imagery or DGPS coordinates exist yet',
    'The UAV has not been purchased, so the planned field imagery and on-site road-width measurements are not yet available')
replace_para('The methodology is a UAV-based workflow that moves from field acquisition to detection, tracking, georeferenced trajectories',
    'The methodology is a UAV-based workflow that moves from field acquisition to detection, tracking, metric-scaled trajectories')
replace_para('The sample-video work reported in Chapter 6 does not change this methodology.',
    'The sample-video work and the preliminary NH-48 analysis reported in Chapter 6 are separate pipeline tests and do not replace the planned Thiruvananthapuram field study.')
replace_para('UAV flight planning and DGPS ground control (Section 5.4)',
    'UAV flight planning and road-width calibration (Section 5.4)')
replace_para('Frame extraction, stabilisation and orthomosaic processing (Section 5.6)',
    'Frame extraction, stabilisation and image-scale calibration (Section 5.6)')
replace_para('DGPS georeferencing of trajectories (Section 5.11)',
    'Metric scaling of trajectories using measured road width (Section 5.11)')
replace_para('Ground coordinates are needed before speed, distance, TTC or PET have any meaning',
    'Metric scale is needed before speed, distance, TTC or PET can be interpreted, because pixel movement alone has no physical units. A measured road or lane width visible in the nadir video provides the reference distance for converting pixel displacement to metres. The NH-48 analysis used an assumed 3.50 m lane width and is therefore provisional; the field study will use an actual measured width.')
replace_para('The road is treated as a plane, so an image point (u, v) maps to a ground point (E, N) by a homography estimated from at least four GCPs:',
    'The road is treated as a plane. Under a stable nadir view, an image point (u, v) is transformed into local road coordinates (X, Y) using a planar mapping whose scale is fixed by the measured road width. If perspective distortion is material, corresponding points along visible road markings and measured dimensions are used to estimate and check the planar transform:')
replace_para('Coordinates are expressed in a metric projected system (for example UTM zone 43N) and converted to latitude and longitude for GIS mapping.',
    'Coordinates are expressed in a local metric road system, with distance along the road as X and lateral offset as Y. Absolute latitude and longitude are not needed for speed estimation or corridor-level conflict analysis.')
replace_para('Trajectories are also overlaid on the lane boundaries of the orthomosaic.',
    'Trajectories are also checked against the lane boundaries identified in the video and measured road geometry.')
replace_para('The mid-block sections are still to be selected using the criteria in Table 3.1, and all field activities depend on this selection.',
    'The mid-block sections are still to be selected using the criteria in Table 3.1. Field activities also require the UAV and an on-site measurement of a visible road or lane width for metric scale calibration.')
replace_para('The UAV has not been purchased and the mid-block sections are yet to be selected, so field data collection with DGPS control is pending.',
    'The UAV has not been purchased and the mid-block sections are yet to be selected, so the planned Thiruvananthapuram field survey and measured road-width calibration are pending. A separate NH-48 analysis provides preliminary metric results based on an assumed lane width.')
replace_para('5.4 UAV FLIGHT PLANNING AND DGPS GROUND CONTROL','5.4 UAV FLIGHT PLANNING AND ROAD-WIDTH CALIBRATION')
replace_para('5.6 FRAME EXTRACTION, STABILISATION AND ORTHOMOSAIC','5.6 FRAME EXTRACTION, STABILISATION AND IMAGE-SCALE CALIBRATION')
replace_para('5.11 DGPS GEOREFERENCING OF TRAJECTORIES','5.11 METRIC SCALING OF TRAJECTORIES')
replace_para('The methodology is a UAV-based workflow that moves from field acquisition to detection, tracking, metric-scaled trajectories',
    'The methodology is a UAV-based workflow that moves from field acquisition to detection, tracking, metric-scaled trajectories and finally to traffic parameters and crash risk. Each step uses data from the previous one, so errors in an early stage can propagate: a missed vehicle breaks a trajectory, an identity switch joins two vehicles, and a coordinate error changes the relative position of two vehicles and therefore their TTC or PET. Detection, tracking, metric scaling and post-processing are therefore treated as one connected system. The sample-video and NH-48 tests reported in Chapter 6 are separate pipeline tests and do not replace the planned field study.')
replace_para('The work done so far is limited to a sample UAV video.',
    'The work so far includes two separate video analyses. A sample UAV video produced 19,133 tracking records for 614 track IDs in pixel coordinates. A separate 601-frame NH-48 video produced 22,031 preliminary metric trajectory points across 126 sustained trajectories, using an assumed 3.50 m lane width. The NH-48 scale has not been physically verified, so its speeds, distances, density and safety measures remain exploratory. The DJI Neo 2 has not been purchased and Thiruvananthapuram study sections remain unselected; field collection and on-site road-width measurement are pending.')
replace_para('Keywords: UAV, Vehicle Detection, YOLO, Small-Object Detection, Multi-Object Tracking, ByteTrack, Vehicle Trajectory, DGPS Georeferencing',
    'Keywords: UAV, Vehicle Detection, YOLO, Small-Object Detection, Multi-Object Tracking, ByteTrack, Vehicle Trajectory, Road-Width Calibration')
replace_para('In Thiruvananthapuram there is no locally annotated, DGPS-georeferenced UAV vehicle dataset',
    'In Thiruvananthapuram there is no locally annotated, metric-scaled UAV vehicle dataset')
replace_para('To evaluate microscopic surrogate safety measures, time-to-collision and post-encroachment time, using UAV DGPS trajectory data',
    'To evaluate microscopic surrogate safety measures, time-to-collision and post-encroachment time, using metric-scaled UAV trajectories')
replace_para('Multi-object tracking, georeferenced trajectories, and vehicle count, speed and density',
    'Multi-object tracking, metric-scaled trajectories, and vehicle count, speed and density')
replace_para('Acquisition of UAV imagery and construction of an annotated, DGPS-georeferenced vehicle dataset with five vehicle classes',
    'Acquisition of UAV imagery and construction of an annotated, metric-scaled vehicle dataset with five vehicle classes')
replace_para('Multi-object tracking and georeferenced trajectories from which vehicle count, speed and density are derived and validated',
    'Multi-object tracking and metric-scaled trajectories from which vehicle count, speed and density are derived and validated')
replace_para('The survey will be carried out on mid-block road sections of the city. No mid-block road section has been shortlisted or confirmed so far. Selecting the sections is the first pending step of the project, because flight planning, DGPS ground control and data collection all depend on it. The sections will be chosen using the criteria in Table 3.1.',
    'The survey will be carried out on mid-block road sections of the city. No mid-block road section has been shortlisted or confirmed so far. Selecting the sections is the first pending step because flight planning, measurement of a visible road or lane width and data collection all depend on it. The sections will be chosen using the criteria in Table 3.1.')
replace_para('UAV data acquisition with DGPS ground control will follow once the sections are selected and the UAV (DJI Neo 2) is purchased.',
    'UAV data acquisition with on-site road-width measurement will follow once the sections are selected and the UAV (DJI Neo 2) is purchased.')
replace_para('A need for a local, georeferenced dataset because published Indian studies of this kind are few',
    'A need for a local, metric-scaled dataset because published Indian studies of this kind are few')
replace_para('The accuracy of UAV-based traffic analysis depends on the quality of the imagery, the ground control and the annotations.',
    'The accuracy of UAV-based traffic analysis depends on the quality of the imagery, the measured road-width reference and the annotations.')
replace_para('4.2.2 DGPS Ground Control Points','4.2.2 Measured Road-Width Reference')
replace_para('The planned platform is the DJI Neo 2 (Figure 4.1). The drone has not yet been purchased, so UAV data acquisition with DGPS ground control has not yet taken place.',
    'The planned platform is the DJI Neo 2 (Figure 4.1). The drone has not yet been purchased, so UAV data acquisition and on-site road-width measurement have not yet taken place.')
replace_para('A nadir (top-down) view is used, with the UAV hovering over the road centreline, to limit perspective distortion; the view must keep every vehicle in frame long enough to form a trajectory. Ground control points are marked on the road surface and surveyed with DGPS in (X, Y, Z). At least four are needed; extra points are kept as independent check points. Berghaus et al. (2024) and Fonod et al. (2025) show that calibration and georeferencing must be planned as part of the measurement chain.',
    'A nadir (top-down) view is used, with the UAV hovering over the road centreline, to limit perspective distortion; the view must keep every vehicle in frame long enough to form a trajectory. A clearly visible road or lane width is measured on site and used as the metric reference. This calibration supports speed and distance calculations without requiring an orthomosaic or DGPS coordinates. Berghaus et al. (2024) and Fonod et al. (2025) show that calibration and trajectory quality checks must be planned as part of the measurement chain.')
replace_para('The output is raw MP4 video per sortie plus overlapping stills for the orthomosaic.',
    'The output is raw MP4 video per sortie plus selected frames for annotation and image-scale calibration; overlapping stills for an orthomosaic are not required.')
replace_para('For example, at 60 km/h a vehicle moves 0.67 m per frame at 25 fps',
    'For example, at 60 km/h a vehicle moves 0.67 m per frame at 25 fps and 0.33 m at 50 fps. With assumed sizes, a 4.5 m car keeps about 74% overlap at 25 fps, whereas a 2 m two-wheeler keeps only 50%, rising to 71% at 50 fps. Short vehicles such as two-wheelers therefore lose overlap fastest, which favours a higher frame rate. Because the flight time is about 19 minutes per battery, several sorties are planned across peak and off-peak periods, and altitude, time and weather are logged for each. The output is raw MP4 video per sortie plus selected frames for annotation and image-scale calibration; overlapping stills for an orthomosaic are not required. Ke et al. (2017) showed that speed, density and volume can be estimated from aerial video.')
replace_para('Overlapping stills are processed by photogrammetry (structure from motion) into an orthomosaic',
    'The measured road or lane width is used to calibrate pixel displacement to metres. Blurred or unusable frames are removed before annotation; no orthomosaic is needed for the speed calculation.')
replace_para('The matrix of coefficients h has eight independent values once it is normalised',
    'For a near-nadir view with limited perspective distortion, the pixel-to-metre scale is calculated as s = W_m / W_px, where W_m is the measured road or lane width in metres and W_px is its width in pixels in the stabilized frame. A pixel displacement d_px is converted to distance by d_m = s × d_px, and vehicle speed is v = d_m / Δt. If perspective variation is material, a planar homography may be estimated from visible road-marking correspondences; the measured width fixes its metric scale. Repeated width measurements at separate locations are used to check consistency. Absolute projected coordinates and independent DGPS control points are not required for the speed objective.')
replace_para('Ei, Ni = surveyed coordinates of check point i',
    'W_m = measured road or lane width in metres; W_px = corresponding width in pixels')
replace_para('E′i, N′i = coordinates of the same point obtained from the homography',
    's = pixel-to-metre scale; d_px = image displacement in pixels; d_m = calibrated distance in metres')
replace_para('n = number of check points',
    'Δt = frame interval in seconds; v = estimated speed in metres per second')
replace_para('The output is a table of ID, time, image position (u, v), ground position (E, N), class, speed, acceleration and lane.',
    'The output is a table of ID, time, image position (u, v), local metric position, class, speed, acceleration and lane.')
replace_para('The speed of each vehicle comes from the smoothed, georeferenced trajectories.',
    'The speed of each vehicle comes from the smoothed, metric-scaled trajectories.')
replace_para('Trajectories in real-world coordinates have not been found, because ground coordinates are not yet available',
    'Metric trajectories for the initial sample-video pilot have not been generated; the separate NH-48 test produced preliminary metric estimates using an assumed lane width')
replace_para('Tracking worked only in the pixel domain; without ground coordinates the results have no physical scale',
    'The initial sample-video tracking worked only in the pixel domain; without a measured scale those results have no physical distance or speed')
replace_para('Vehicle detection and tracking in the pixel domain have been completed on the sample video.',
    'Vehicle detection and tracking in the pixel domain have been completed on the sample video. Metric scale for that pilot is still unavailable, while the separate NH-48 analysis used an assumed lane width and remains provisional.')
replace_para('The sample-video work shows that the detection and tracking part of the workflow can be run end to end:',
    'The sample-video work shows that the detection and tracking part of the workflow can be run end to end:')
replace_para('The missing step is georeferencing, which depends on the purchase of the UAV, the selection of the sections and the DGPS survey.',
    'For the planned field study, the remaining calibration step is to measure a reliable road or lane width in the video scene after the UAV and sections are selected.')
replace_para('The UAV platform has been identified (DJI Neo 2) but not purchased, so UAV data acquisition with DGPS ground control has not yet taken place',
    'The UAV platform has been identified (DJI Neo 2) but not purchased, so the planned UAV data acquisition and on-site road-width measurement have not yet taken place')

# Update the project problem statement to use the metric scale actually required for speed.
replace_para('Existing UAV-based traffic studies rely mainly on generic detectors, optical-flow or clustering methods, and rarely pair a small-object-optimised detector with trajectory-level crash risk analysis.',
    'Existing UAV-based traffic studies rely mainly on generic detectors, optical-flow or clustering methods, and rarely pair a small-object-optimised detector with trajectory-level crash risk analysis. The challenge lies in detecting all five vehicle classes reliably from high-altitude UAV imagery, converting detections into metric-scaled trajectories, and using them to estimate safety measures on mid-block highways under heterogeneous traffic.')
replace_para('Trajectories have not been generated in real-world coordinates, because ground coordinates are not yet available',
    'The initial sample-video trajectories remain in pixels; a separate NH-48 analysis generated preliminary metric trajectories using an assumed lane width')
replace_para('A DGPS-georeferenced, annotated UAV vehicle dataset representative of Thiruvananthapuram traffic conditions',
    'An annotated, metric-scaled UAV vehicle dataset representative of Thiruvananthapuram traffic conditions')
replace_para('Purchase the UAV (DJI Neo 2) and carry out the field survey with DGPS ground control',
    'Purchase the UAV (DJI Neo 2), carry out the field survey and measure a reliable road or lane width for image-scale calibration')
replace_para('Apply DGPS georeferencing, then compute TTC, PET and the crash prediction model',
    'Apply road-width-based metric scaling, then compute TTC, PET and the crash prediction model')
replace_para('The study aims to show that UAV imagery, a small-object-optimised detector, multi-object tracking and DGPS georeferencing can be combined',
    'The study aims to show that UAV imagery, a small-object-optimised detector, multi-object tracking and road-width-based metric calibration can be combined')
replace_para('The remaining work depends on the field activities of selecting the sections, purchasing the UAV and carrying out the DGPS survey.',
    'The remaining work depends on selecting the sections, purchasing the UAV and measuring a reliable road or lane width in the video scene.')

# Replace stale references inside existing tables without changing their structure.
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                t = p.text
                nt = t.replace('DGPS ground control','measured road-width calibration')
                nt = nt.replace('DGPS coordinates','road-width measurements')
                nt = nt.replace('orthomosaic','calibrated video frames').replace('Orthomosaic','Calibrated video frames')
                nt = nt.replace('georeferenced trajectories','metric-scaled trajectories')
                if nt != t:
                    for r in list(p.runs):
                        p._p.remove(r._r)
                    p.add_run(nt)


def before(anchor, p):
    anchor._p.addprevious(p._p)


def addp(anchor, text, style='Normal'):
    p = doc.add_paragraph(text, style=style)
    before(anchor, p)
    return p


def heading(anchor, text, level=2):
    return addp(anchor, text, f'Heading {level}')


def table_before(anchor, headers, rows):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = doc.tables[0].style
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, val in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = str(val)
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for r in c.paragraphs[0].runs:
            r.bold = True
        shd = OxmlElement('w:shd')
        shd.set(qn('w:fill'), 'D9E2F3')
        c._tc.get_or_add_tcPr().append(shd)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    anchor._p.addprevious(t._tbl)
    return t


def caption(anchor, text):
    p = doc.add_paragraph(text, style='Caption' if 'Caption' in [s.name for s in doc.styles] else 'Normal')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    before(anchor, p)
    return p


def image_before(anchor, src, index, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    shape = src.inline_shapes[index]
    relid = shape._inline.xpath('.//a:blip')[0].get(qn('r:embed'))
    blob = src.part.related_parts[relid].blob
    p.add_run().add_picture(BytesIO(blob), width=Inches(5.9))
    before(anchor, p)
    caption(anchor, text)


def local_image_before(anchor, path, text, width=Inches(6.0)):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=width)
    before(anchor, p)
    caption(anchor, text)


def insert_plain_before(anchor, text):
    p = doc.add_paragraph(style='Normal')
    p.add_run(text)
    before(anchor, p)
    return p


# Record the current manual-annotation workflow and intended Docker inference deployment.
a = next(p for p in doc.paragraphs if p.text.strip().startswith('5.8 BASELINE YOLO TRAINING'))
addp(a, 'Current work is focused on preparing the local training set. CVAT is being run through Docker, and video frames extracted from the UAV footage are being labelled manually with bounding boxes for two-wheelers, three-wheelers, cars, light commercial vehicles and heavy commercial vehicles. The annotations will be checked for class and box consistency, then split by video or location into training, validation and held-out test sets. The labelled frames will be exported in YOLO format and used to fine-tune the detector, with special attention to recall and average precision for small vehicles. After evaluation, the trained weights are intended to be packaged in a Docker-based inference workflow to detect small vehicles in new video frames.')

# Add the proposed critical-limit comparison graph and distance definitions.
a = next(p for p in doc.paragraphs if p.text.strip().startswith('5.14 CRASH RISK ESTIMATION AND PREDICTION'))
heading(a, '5.13.2 LONGITUDINAL AND LATERAL CONFLICT GRAPHS', 3)
addp(a, 'Longitudinal conflicts are assessed when a following vehicle closes on a leader. Longitudinal TTC is the bumper-to-bumper gap divided by the closing speed, when the follower is faster than the leader. The planned graph plots TTC against time and marks 1.5 s as a provisional critical screening limit. The FHWA Surrogate Safety Assessment Model uses 1.5 s as a configurable TTC conflict threshold [18, 19]. It is a screening convention, not a universal boundary; the analysis will compare 1.0 s, 1.5 s and 2.0 s thresholds.')
addp(a, 'Lateral conflicts are assessed during lane changes or crossing paths with a two-dimensional TTC: the predicted time until the moving vehicle footprints first overlap under their estimated velocities. A second graph plots lateral or two-dimensional TTC against time with the same provisional 1.5 s line for comparison. Because lateral conflict thresholds depend on geometry and manoeuvre type, the line is an initial screening limit and will be checked through threshold sensitivity analysis rather than treated as a validated local crash boundary.')
addp(a, 'Critical distance is reported alongside TTC. For longitudinal following, the available distance is the bumper-to-bumper gap g; the required stopping distance is d_safe = v_f t_r + v_f²/(2a_f) − v_l²/(2a_l). The stopping-distance deficit is Δd = g − d_safe; a negative value means the available gap is shorter than the modelled safe distance under the selected reaction and braking assumptions. For a lateral or crossing conflict, critical distance is the along-path distance from each vehicle to the projected conflict point. Its time-to-conflict is that distance divided by the speed component directed toward the point. Distances, thresholds and parameter assumptions will be reported together.')
local_image_before(a, Path(r'C:/Highway_Traffic_Analysis/critical_ttc_concept.png'), 'Figure 5.2: Conceptual longitudinal and lateral TTC graphs with a provisional 1.5 s screening limit. Curves are illustrative, not measured results.')


# Add the NH-48 test corridor as a separate dataset from the planned city field study.
a = next(p for p in doc.paragraphs if p.text.strip().startswith('3.4 RELEVANCE OF THE STUDY AREA'))
heading(a, '3.4 PRELIMINARY NH-48 TEST CORRIDOR')
addp(a, 'A separate NH-48 UAV video was used to extend the pipeline test beyond the original sample-video pilot. This corridor is an analytical test dataset and is not the planned Thiruvananthapuram study site. It provides preliminary results for detection, metric trajectory extraction, traffic-flow analysis and safety measures. Its scale was estimated from an assumed 3.50 m lane width; the values must be treated as provisional until checked against a physically measured width. The NH-48 results demonstrate the workflow and do not replace field data collection at the selected mid-block sections.')
replace_para('3.4 RELEVANCE OF THE STUDY AREA','3.5 RELEVANCE OF THE STUDY AREA')
replace_para('3.5 SUMMARY','3.6 SUMMARY')

a = next(p for p in doc.paragraphs if p.text.strip().startswith('4.3 UAV PLATFORM'))
heading(a, '4.2.7 NH-48 UAV TEST VIDEO', 3)
addp(a, 'The additional NH-48 video contains 601 frames at 30 frames per second, with a resolution of 1608 × 908 pixels and a duration of 20.03 seconds. The analysed corridor spans approximately 160 m and includes eastbound and westbound traffic. The preliminary calibration used an assumed 3.50 m lane width rather than a field-measured reference, so reported speeds, distances, densities and stopping margins are exploratory and require verification. The original sample video described in Section 4.2.6 remains a separate pilot dataset.')
a = next(p for p in doc.paragraphs if p.text.strip().startswith('4.6 DATA LIMITATIONS'))
heading(a, '4.5.1 UAV TRAFFIC STUDIO SOFTWARE PLATFORM', 3)
addp(a, 'A standalone UAV Traffic Studio application was developed as a research interface for the NH-48 analysis. Its Python backend uses PyTorch, Ultralytics YOLOv8, OpenCV, NumPy, SciPy and pandas. A Python REST service exposes status, metrics, conflicts, critical distances, hotspots, trajectories and pipeline execution endpoints. The browser interface uses HTML5, CSS3 and Apache ECharts and provides trajectory playback, space-time exploration, adjustable stopping parameters, conflict replay, pipeline logs and data export. The reported implementation includes eight workspaces: Overview, Video Player, Traffic Flow Theory, Trajectory Studio, Critical Distance Safety Inspector, Spatial Hotspots, Automated Pipeline Runner and Data Exports. The platform is described in the source report as implemented; its operational status should be supported by a reproducible software demonstration.')

# Integrate the new kinematic safety method into Chapter 5.
a = next(p for p in doc.paragraphs if p.text.strip().startswith('5.14 CRASH RISK ESTIMATION AND PREDICTION'))
heading(a, '5.13.1 KINEMATIC STOPPING DISTANCE DEFICIT', 3)
addp(a, 'TTC assumes constant speeds and can become uninformative when a follower and leader travel at similar speeds despite having very little clearance. The NH-48 analysis therefore added a kinematic stopping-distance check. The required clearance for the following vehicle is estimated as:')
addp(a, 'd_safe = v_f t_r + v_f²/(2a_f) − v_l²/(2a_l)')
addp(a, 'The safety deficit is Δd = d_clear − d_safe, where d_clear is the bumper-to-bumper clearance; v_f and v_l are follower and leader speeds; t_r is perception-reaction time; and a_f and a_l are their assumed braking decelerations. A negative Δd indicates that the follower’s calculated stopping requirement exceeds the available clearance under the selected assumptions. Results depend on calibration and parameter choices and should be interpreted as conflict indicators, not confirmed crashes.')
addp(a, 'The preliminary NH-48 analysis used t_r = 1.5 s, a_f = 3.4 m/s² and a_l = 6.0 m/s², with sensitivity ranges for reaction time and braking deceleration. These are analysis assumptions; the final study should report sensitivity to them.')

# New NH-48 results, inserted before Chapter 7. The previous pilot sections remain unchanged.
ch7 = next(p for p in doc.paragraphs if p.text.strip().startswith('CHAPTER-7'))
src = Document(SRC_B)
replace_para('CHAPTER-1\nINTRODUCTION', '1 INTRODUCTION')
replace_para('CHAPTER-2\nLITERATURE REVIEW', '2 LITERATURE REVIEW')
replace_para('CHAPTER-3\nSTUDY AREA', '3 STUDY AREA')
replace_para('CHAPTER-4\nDATA AND SOFTWARE USED', '4 DATA AND SOFTWARE USED')
replace_para('CHAPTER-5\nMETHODOLOGY', '5 METHODOLOGY')
replace_para('CHAPTER-6\nRESULTS AND DISCUSSION', '6 WORK DONE AND EXPECTED RESULTS')
replace_para('CHAPTER-7\nCONCLUSIONS AND WORK PLAN', '7 CONCLUSIONS AND WORK PLAN')
for p in doc.paragraphs:
    if p.text.strip()[:1].isdigit() and p.text.strip().split(' ', 1)[0] in {'1','2','3','4','5','6','7'} and ('INTRODUCTION' in p.text or 'LITERATURE REVIEW' in p.text or 'STUDY AREA' in p.text or 'DATA AND SOFTWARE USED' in p.text or 'METHODOLOGY' in p.text or 'WORK DONE AND EXPECTED RESULTS' in p.text or 'CONCLUSIONS AND WORK PLAN' in p.text):
        p.style = 'Heading 1'
replace_para('6.1 GENERAL', '6.1 WORK COMPLETED AND EXPECTED RESULTS')
replace_para('6.2 WORK COMPLETED TILL DATE', '6.2 WORK COMPLETED TO DATE')
replace_para('6.4 VEHICLE DETECTION RESULTS', '6.4 VEHICLE DETECTION OBSERVATIONS')
replace_para('6.5 MULTI-OBJECT TRACKING RESULTS', '6.5 MULTI-OBJECT TRACKING OUTPUT')
replace_para('6.6 TRACKING OUTPUT IN THE PIXEL DOMAIN', '6.6 PIXEL-COORDINATE PILOT OUTPUT')
heading(ch7, '6.11 NH-48 DATASET AND PRELIMINARY CALIBRATION')
addp(ch7, 'A separate 601-frame NH-48 sequence (1608 × 908 pixels, 30 fps, 20.03 s) was processed over an approximately 160 m corridor. The pipeline generated 22,031 metric trajectory points across 126 sustained corridor trajectories from 160 track IDs. Metric scaling used an assumed 3.50 m lane width. These derived values are preliminary because the width was not physically measured for this analysis; they should not be presented as verified field measurements. The principal measurement requirement for the planned study is a reliable road or lane width in the UAV scene, which supplies the pixel-to-metre scale for speed estimation.')
addp(ch7, 'The average concurrent vehicle load was reported as 28.02, with a peak of 48 vehicles.')
addp(ch7, 'The original sample-video pilot remains separate: it produced 19,133 pixel-coordinate tracking records for 614 track IDs and has no metric calibration. The different frame counts and tracking totals describe two datasets and must not be combined.')
caption(ch7, 'Table 6.4: NH-48 video and trajectory dataset characteristics')
table_before(ch7, ['Parameter', 'NH-48 preliminary result'], [
    ('Video resolution and frame rate', '1608 × 908 pixels at 30 fps'), ('Duration and frames', '20.03 s; 601 frames'),
    ('Analysed corridor length', 'Approximately 160 m'), ('Traffic direction', 'Eastbound and westbound streams'),
    ('Track IDs and sustained trajectories', '160 IDs; 126 sustained corridor trajectories'), ('Metric trajectory points', '22,031'),
    ('Calibration basis', 'Assumed 3.50 m lane width; not field-verified')])
image_before(ch7, src, 2, 'Figure 6.3: Preliminary road-plane view of the NH-48 corridor after image-scale calibration')

heading(ch7, '6.12 VEHICLE DETECTION AND PRETRAINED MODEL LIMITATIONS')
addp(ch7, 'The NH-48 test used off-the-shelf YOLOv8s-VisDrone weights. The model was not trained or fine-tuned by the author. The detection output contained 48 unique vehicles: 31 passenger cars, 8 vans or light delivery vehicles, 7 buses, 1 heavy commercial truck and 1 motorcycle. The observed motorcycle share was 2.1%. This is an indication of small-object under-detection in the tested video, but the automated class distribution is not a reliable estimate of true traffic composition because the detector itself missed objects. The source documents report higher detection confidence for larger vehicles and lower confidence for the few motorcycle detections. The result motivates local annotation and small-object model training; it does not establish the true traffic share of each class.')
caption(ch7, 'Table 6.5: Automated NH-48 vehicle classification from the pretrained model')
table_before(ch7, ['Vehicle class', 'Detected count', 'Share', 'Reported observation'], [
    ('Passenger cars', '31', '64.6%', 'Mean confidence 0.84'), ('Vans / light delivery', '8', '16.7%', 'Stable boundaries'),
    ('Buses', '7', '14.6%', 'Large bounding footprint'), ('Heavy commercial trucks', '1', '2.1%', 'Localized in outer lane'),
    ('Motorcycles / two-wheelers', '1', '2.1%', 'Severely under-detected')])
image_before(ch7, src, 3, 'Figure 6.4: Automated vehicle classification chart showing the pretrained model output')
addp(ch7, 'The source documents attribute the failure to small image size at UAV altitude, domain differences between benchmark data and Indian mixed traffic, and low-confidence filtering. They report motorcycle confidence values in the approximate 0.25–0.48 range. These explanations are hypotheses from the analysis, not independently isolated causal effects. The planned custom detector will test a stride-4 P2 head, multi-scale feature fusion and Wise-IoU against the baseline on the same locally annotated test set.')
addp(ch7, 'The updated interim report estimates that, at a GSD of about 8–10 cm per pixel, a 1.8 m × 0.7 m two-wheeler occupies roughly 18 × 7 pixels. It attributes missed detections to loss of fine features during stride-32 downsampling, a domain gap between VisDrone pretraining and Indian traffic, and low-confidence proposals (reported around 0.25–0.42) being filtered by non-maximum suppression. The 30–50% two-wheeler share cited in that source is contextual background, not a measured share for this video. These are explanations to test, not separately validated causal findings.')

heading(ch7, '6.13 TRACKING AND METRIC TRAJECTORY EXTRACTION')
addp(ch7, 'ByteTrack processed the 601 frames and produced 160 track IDs, of which 126 sustained trajectories traversed the analysed corridor. The source documents report 22,031 metric trajectory points. One report describes forward-backward Savitzky–Golay smoothing and another describes a moving-average filter; the exact filter configuration should be confirmed against the processing code before the method is finalized. The preliminary calibration used the assumed lane width noted in Section 6.11.')
image_before(ch7, src, 4, 'Figure 6.5: Space-time diagram of vehicle trajectories on the NH-48 corridor')

heading(ch7, '6.14 MACROSCOPIC TRAFFIC FLOW PARAMETERS')
addp(ch7, 'The NH-48 trajectory output was used to estimate flow, density and speed. The source reports total bidirectional flow of 8,625.6 veh/h, comprising 5,031.6 veh/h westbound and 3,594.0 veh/h eastbound. Reported density was 175.1 veh/km; time-mean speed was 26.59 km/h; space-mean speed was 25.44 km/h; speed standard deviation was 5.42 km/h; and the 85th-percentile speed was 31.67 km/h. Reported minimum and maximum speeds were 16.0 and 44.5 km/h. The values are preliminary because they depend on the assumed 3.50 m scale.')
addp(ch7, 'The source also reports Wardrop’s inequality, with time-mean speed greater than space-mean speed. However, reported total flow, density and space-mean speed do not reconcile directly under q = k u_s: 175.1 × 25.44 is approximately 4,454 veh/h, not 8,625.6 veh/h. The aggregation basis (direction, lane or corridor) must be checked before claiming a flow-theory validation.')
addp(ch7, 'The source’s lane-equivalent calculation reports q = k × u_s = 175.1 × 25.44 ≈ 4,454 veh/h, while its separate total bidirectional throughput is 8,625.6 veh/h. These may use different aggregation bases, but the directional and lane definitions need to be documented before the figures are compared.')
caption(ch7, 'Table 6.6: Preliminary macroscopic traffic parameters reported for NH-48')
table_before(ch7, ['Parameter', 'Reported value'], [
    ('Total bidirectional flow', '8,625.6 veh/h'), ('Westbound flow', '5,031.6 veh/h (58.3%)'), ('Eastbound flow', '3,594.0 veh/h (41.7%)'),
    ('Traffic density', '175.1 veh/km'), ('Time-mean speed', '26.59 km/h (7.39 m/s)'), ('Space-mean speed', '25.44 km/h (7.07 m/s)'),
    ('Speed standard deviation', '5.42 km/h'), ('85th-percentile speed', '31.67 km/h'), ('Observed speed range', '16.0–44.5 km/h')])
image_before(ch7, src, 5, 'Figure 6.6: Preliminary speed distribution and 85th-percentile speed on NH-48')

heading(ch7, '6.15 MICROSCOPIC SURROGATE SAFETY MEASURES')
addp(ch7, 'Across 3,668 evaluated car-following instances, 2,391 had TTC ≤ 1.50 s; the reported mean for these critical TTC instances was 0.43 s. A further 380 instances were reported in the 1.50–2.50 s range. Of 413 encroachment instances, 209 had PET ≤ 1.00 s, with a median PET of 0.97 s. The analysis also reported 1,169 instances with DRAC greater than 3.40 m/s². These are event or frame counts from the preliminary video analysis and should not be interpreted as independent crashes or a site-wide crash rate.')
image_before(ch7, src, 6, 'Figure 6.7: Distribution of preliminary microscopic TTC events')

heading(ch7, '6.16 KINEMATIC STOPPING DISTANCE DEFICIT AND CRITICAL EVENTS')
addp(ch7, 'The stopping-distance formulation was applied to 195 leader–follower conflict pairs using t_r = 1.5 s, a_f = 3.4 m/s² and a_l = 6.0 m/s². The source reports 147 Tier 1 pairs with Δd < 0 m, 21 Tier 2 pairs with 0 ≤ Δd < 10 m, and 27 Tier 3 pairs with Δd ≥ 10 m. The most severe listed case is frame 341: Van #3 followed Bus #946 with 0.50 m clearance, a reported safe distance of 17.39 m, deficit of −16.89 m, TTC of 0.11 s and DRAC of 19.80 m/s². This ranking depends on the preliminary image scale and selected driver/braking assumptions.')
addp(ch7, 'The two updated source reports disagree on several vehicle IDs and measurements in ranks 6–10 of their top-ten tables. The table below uses values from the full updated report; those rows should be checked against the raw analysis output before final submission.')
caption(ch7, 'Table 6.7: Ten highest-ranked NH-48 conflict events in the full updated report')
table_before(ch7, ['Rank','Pair (frame)','Clearance (m)','Safe distance (m)','Deficit (m)','TTC / DRAC / tier'], [
    ('1','#3 Van → #946 Bus (341)','0.50','17.39','−16.89','0.11 s / 19.80 m/s² / 1'), ('2','#946 Bus → #933 Car (369)','1.21','10.60','−9.39','0.28 s / 7.91 m/s² / 1'),
    ('3','#945 Van → #946 Bus (210)','0.80','8.85','−8.05','0.35 s / 6.42 m/s² / 1'), ('4','#943 Motor → #942 Truck (26)','0.42','8.35','−7.93','0.23 s / 9.94 m/s² / 1'),
    ('5','#935 Car → #947 Truck (270)','0.62','6.70','−6.08','0.42 s / 5.34 m/s² / 1'), ('6','#933 Car → #934 Car (132)','0.85','6.22','−5.37','0.51 s / 4.45 m/s² / 1'),
    ('7','#947 Truck → #946 Bus (244)','1.10','6.15','−5.05','0.62 s / 3.92 m/s² / 1'), ('8','#934 Car → #945 Van (417)','0.95','5.80','−4.85','0.58 s / 4.15 m/s² / 1'),
    ('9','#942 Truck → #935 Car (8)','1.30','5.75','−4.45','0.71 s / 3.62 m/s² / 1'), ('10','#946 Bus → #945 Van (3)','1.45','5.50','−4.05','0.80 s / 3.48 m/s² / 1')])
image_before(ch7, src, 7, 'Figure 6.8: Annotated frame for the highest-ranked conflict at frame 341')

heading(ch7, '6.17 SPATIAL CONFLICT HOTSPOTS')
addp(ch7, 'The 160 m NH-48 corridor was divided into 20 m longitudinal zones. The highest reported count was 37 conflicts in [0 m, 20 m], described as the primary merge or lane-drop bottleneck. A secondary zone at [80 m, 100 m] contained 32 conflicts. Counts for the remaining zones are listed below. These are preliminary conflict concentrations from one short video and do not establish crash hotspots.')
caption(ch7, 'Table 6.8: Conflict counts by 20 m NH-48 corridor zone')
table_before(ch7, ['Longitudinal zone (m)','Conflict count','Source interpretation'], [
    ('−40 to −20','19','Entry zone; initial deceleration'), ('−20 to 0','24','Pre-bottleneck compaction'), ('0 to 20','37','Primary merge / lane-drop zone'),
    ('20 to 40','27','Bottleneck propagation'), ('40 to 60','20','Intermediate recovery'), ('60 to 80','24','Secondary weave compression'),
    ('80 to 100','32','Secondary friction zone'), ('100 to 120','11','Free-flow dispersal')])
image_before(ch7, src, 8, 'Figure 6.9: Conflict counts and preliminary hotspots across the NH-48 corridor')

heading(ch7, '6.18 UAV TRAFFIC STUDIO')
addp(ch7, 'UAV Traffic Studio provides a browser-based interface for exploring the preliminary analysis. Reported features include 60 fps trajectory animation with bounding boxes, velocity vectors and path histories; adjustable reaction-time and deceleration controls that rerank stopping-distance events; replay of annotated frames such as the frame 341 conflict; and a REST-triggered pipeline for video ingestion, homography transformation and safety scoring. The interface also includes live pipeline logs and data exports. The software is a research deliverable; its analytical outputs retain the calibration and data limitations described above.')
addp(ch7, 'The reported REST endpoints are /api/status, /api/metrics, /api/conflicts, /api/critical-distances, /api/hotspots, /api/trajectories, /api/pipeline/status and POST /api/pipeline/run. The source report also describes Warm Cream, Clean Light and Dark Analytics themes, optional liquid-glass backdrop blur and a dedicated Python service at app/server.py on port 8080.')

heading(ch7, '6.19 EXPECTED RESULTS AND DELIVERABLES')
addp(ch7, 'The expected outcome is a locally annotated five-class UAV image dataset and a fine-tuned detector that improves small-vehicle detection, particularly two-wheelers, relative to the pretrained baseline on a held-out test set. Performance will be reported with class-wise precision, recall, F1 score, average precision and inference speed; improvement will be assessed from the measured test results, not assumed in advance.')
addp(ch7, 'The complete workflow is expected to connect manually labelled CVAT frames, YOLO model training, Docker-based inference, multi-object tracking, measured-width metric scaling and traffic-safety analysis. Outputs will include vehicle counts, speed and density summaries, longitudinal and lateral TTC graphs with provisional critical-limit lines, PET and DRAC summaries, critical-distance and stopping-distance-deficit tables, and spatial conflict maps. These are planned outputs; the Thiruvananthapuram field results will be reported after site selection, data collection and scale verification.')

# Add a concise consolidated status before the conclusion chapter.
addp(ch7, 'The current work includes two distinct video analyses: an initial pixel-domain pilot (19,133 records for 614 track IDs) and a preliminary NH-48 analysis (22,031 metric trajectory points across 126 sustained trajectories, based on an assumed 3.50 m lane width). The NH-48 traffic, safety and hotspot values are exploratory, and the traffic-flow aggregation and conflicting top-ten table entries require verification before they are treated as final findings.')

# Add the NH-48 progress items to the existing work summary.
expected = next(p for p in doc.paragraphs if p.text.strip().startswith('7.3 EXPECTED OUTCOMES'))
for item in [
    'A separate NH-48 sequence was analysed (601 frames; 160 track IDs; 126 sustained trajectories; 22,031 preliminary metric points). Its scale depends on an assumed 3.50 m lane width and remains unverified.',
    'The off-the-shelf YOLOv8s-VisDrone model recorded only one motorcycle among 48 detected vehicles (2.1%), indicating severe under-detection in this video.',
    'Preliminary NH-48 results include flow, density, speed, TTC, PET, DRAC and stopping-distance deficit estimates; the bidirectional flow aggregation requires reconciliation.',
    'A 20 m zone summary identified 37 conflicts in [0 m, 20 m] and 32 in [80 m, 100 m]; these are exploratory conflict concentrations from one short video.',
    'UAV Traffic Studio was developed with REST endpoints for pipeline execution, trajectory review, safety scoring and hotspot exploration.'
]:
    addp(expected, item)

# Replace the obsolete hand-typed contents pages with a live Word table of contents.
paras = list(doc.paragraphs)
toc_title = next(p for p in paras if p.text.strip() == 'CONTENTS')
tables_title = next(p for p in paras if p.text.strip() == 'LIST OF TABLES')
for p in paras[paras.index(toc_title)+1:paras.index(tables_title)]:
    p._element.getparent().remove(p._element)
toc = doc.add_paragraph()
fld = OxmlElement('w:fldSimple'); fld.set(qn('w:instr'), 'TOC \\o "1-3" \\h \\z \\u')
r = OxmlElement('w:r'); t = OxmlElement('w:t'); t.text = 'Updating contents'; r.append(t); fld.append(r); toc._p.append(fld)
tables_title._p.addprevious(toc._p)

# Add new rows to the correct table and figure lists, without inherited page-break formatting.
fighead = next(p for p in doc.paragraphs if p.text.strip() == 'LIST OF FIGURES')
chapter1 = next(p for p in doc.paragraphs if p.text.strip().startswith('1 INTRODUCTION'))
for text in [
    '6.4\tNH-48 video and trajectory dataset characteristics\t—',
    '6.5\tAutomated NH-48 vehicle classification\t—',
    '6.6\tPreliminary macroscopic traffic parameters\t—',
    '6.7\tTen highest-ranked NH-48 conflict events\t—',
    '6.8\tConflict counts by 20 m NH-48 corridor zone\t—']:
    insert_plain_before(fighead, text)
for text in [
    '5.2\tConceptual longitudinal and lateral TTC graphs with provisional critical limit\t—',
    '6.3\tPreliminary NH-48 road-plane view after image-scale calibration\t—',
    '6.4\tAutomated NH-48 vehicle classification chart\t—',
    '6.5\tSpace-time diagram of NH-48 vehicle trajectories\t—',
    '6.6\tPreliminary NH-48 speed distribution\t—',
    '6.7\tDistribution of preliminary microscopic TTC events\t—',
    '6.8\tAnnotated frame for the highest-ranked conflict\t—',
    '6.9\tConflict counts and preliminary hotspots across NH-48\t—']:
    insert_plain_before(chapter1, text)

# Replace static page placeholders in the figure and table lists with live page references.
def add_bookmark(paragraph, name, bookmark_id):
    start = OxmlElement('w:bookmarkStart'); start.set(qn('w:id'), str(bookmark_id)); start.set(qn('w:name'), name)
    end = OxmlElement('w:bookmarkEnd'); end.set(qn('w:id'), str(bookmark_id))
    paragraph._p.insert(1 if paragraph._p.pPr is not None else 0, start)
    paragraph._p.append(end)


def add_pageref(paragraph, bookmark):
    field = OxmlElement('w:fldSimple'); field.set(qn('w:instr'), f' PAGEREF {bookmark} \\h ')
    run = OxmlElement('w:r'); text = OxmlElement('w:t'); text.text = '1'; run.append(text); field.append(run)
    paragraph._p.append(field)


captions = {}
for p in doc.paragraphs:
    m = re.match(r'\s*(Table|Figure)\s+(\d+\.\d+)\s*:', p.text, re.I)
    if m:
        captions[(m.group(1).title(), m.group(2))] = p
next_bookmark_id = 20
for kind, title_text in [('Table', 'LIST OF TABLES'), ('Figure', 'LIST OF FIGURES')]:
    paras = list(doc.paragraphs)
    title = next(p for p in paras if p.text.strip() == title_text)
    start = paras.index(title) + 2
    end = next((i for i in range(start, len(paras)) if paras[i].text.strip() == 'LIST OF FIGURES' or paras[i].text.strip().startswith('1 INTRODUCTION')), len(paras))
    for p in paras[start:end]:
        m = re.match(r'\s*(\d+\.\d+)\t.*\t[^\t]+\s*$', p.text)
        if not m:
            continue
        number = m.group(1); target = captions.get((kind, number))
        if target is None:
            continue
        bookmark = f'_BKM_{kind}_{number.replace(".", "_")}'
        add_bookmark(target, bookmark, next_bookmark_id); next_bookmark_id += 1
        before_page = p.text.rsplit('\t', 1)[0] + '\t'
        for run in list(p.runs): p._p.remove(run._r)
        p.add_run(before_page)
        add_pageref(p, bookmark)

# Remove leftover wording that describes this as an interim report.
for p in list(doc.paragraphs):
    if 'interim' in p.text.lower():
        cleaned = re.sub(r'interim\s+project\s+work', 'project work', p.text, flags=re.I)
        cleaned = re.sub(r'updated\s+interim\s+report', 'earlier analysis', cleaned, flags=re.I)
        cleaned = re.sub(r'interim\s+project\s+report', 'project report', cleaned, flags=re.I)
        cleaned = re.sub(r'interim\s+report', 'project report', cleaned, flags=re.I)
        cleaned = re.sub(r'\binterim\b', '', cleaned, flags=re.I)
        for run in list(p.runs): p._p.remove(run._r)
        p.add_run(cleaned)
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                if 'interim' in p.text.lower():
                    cleaned = re.sub(r'\binterim\b', '', p.text, flags=re.I)
                    for run in list(p.runs): p._p.remove(run._r)
                    p.add_run(cleaned)

# Ask Word to refresh fields when the document is opened.
settings = doc.settings.element
uf = settings.find(qn('w:updateFields'))
if uf is None:
    uf = OxmlElement('w:updateFields')
    settings.append(uf)
uf.set(qn('w:val'), 'true')
doc.add_paragraph('[18] Federal Highway Administration, Surrogate Safety Assessment Model (SSAM): Validation of SSAM, FHWA-HRT-08-051, 2008.')
doc.add_paragraph('[19] Federal Highway Administration, Surrogate Safety Measures from Traffic Simulation Models, FHWA-RD-03-050, 2003.')
doc.save(OUT)
print(OUT)
