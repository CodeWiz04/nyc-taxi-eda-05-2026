
import json
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak,
)
from reportlab.lib.utils import ImageReader

IMAGES_DIR = "images"
CLEANING_SUMMARY_PATH = "data/processed/cleaning_summary.json"
BUSINESS_SUMMARY_PATH = "business_analysis_summary.json"
OUTPUT_PATH = "reports/final_report.pdf"

PAGE_WIDTH, _ = letter
CONTENT_WIDTH = PAGE_WIDTH - 1.4 * inch  # matches SimpleDocTemplate margins


def load_json(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find {path}. Run the pipeline step that produces it "
            f"before generating the report."
        )
    with open(path) as f:
        return json.load(f)


def fitted_image(path, max_width=CONTENT_WIDTH, max_height=3.6 * inch):
    """Load an image scaled to fit within max_width x max_height, preserving
    aspect ratio, so charts never get stretched or overflow the page."""
    if not os.path.exists(path):
        return None
    reader = ImageReader(path)
    iw, ih = reader.getSize()
    scale = min(max_width / iw, max_height / ih)
    return Image(path, width=iw * scale, height=ih * scale)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"], fontSize=24, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle", parent=styles["Normal"], fontSize=12,
        textColor=colors.grey, spaceAfter=24
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading", parent=styles["Heading1"], fontSize=16,
        spaceBefore=18, spaceAfter=10, textColor=colors.HexColor("#1a3c5e")
    ))
    styles.add(ParagraphStyle(
        name="SubHeading", parent=styles["Heading2"], fontSize=12.5,
        spaceBefore=10, spaceAfter=6, textColor=colors.HexColor("#2f5c85")
    ))
    styles.add(ParagraphStyle(
        name="KeyNumber", parent=styles["Normal"], fontSize=13,
        textColor=colors.HexColor("#1a3c5e"), spaceAfter=4, leading=17
    ))
    return styles


def make_table(data, col_widths=None):
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3c5e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def build_title_page(story, styles, cleaning):
    story.append(Spacer(1, 1.6 * inch))
    story.append(Paragraph("NYC Yellow Taxi Trip Data", styles["ReportTitle"]))
    story.append(Paragraph("Exploratory Data Analysis -- Final Report", styles["ReportSubtitle"]))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph(
        f"Dataset: {cleaning.get('initial_rows', 'N/A'):,} raw trip records "
        f"({cleaning.get('initial_cols', 'N/A')} columns)", styles["Normal"]
    ))
    story.append(Paragraph(
        f"After cleaning: {cleaning.get('final_rows', 'N/A'):,} records "
        f"({cleaning.get('pct_rows_removed', 'N/A')}% removed, with reasons "
        f"documented below)", styles["Normal"]
    ))
    story.append(PageBreak())


def build_objective_section(story, styles):
    story.append(Paragraph("1. Objective", styles["SectionHeading"]))
    story.append(Paragraph(
        "This report summarizes a full exploratory analysis of one month of "
        "NYC Yellow Taxi trip records: how the raw data was cleaned and why, "
        "what the data shows about rider and fare patterns, and direct "
        "answers to five specific business questions. Every number in this "
        "report is generated directly by the analysis pipeline -- nothing "
        "here is estimated or written by hand.", styles["Normal"]
    ))


def build_cleaning_section(story, styles, cleaning):
    story.append(Paragraph("2. Data Cleaning", styles["SectionHeading"]))
    story.append(Paragraph(
        f"Starting from {cleaning['initial_rows']:,} raw records, the "
        f"pipeline applied the filters below in sequence. "
        f"{cleaning['total_rows_removed']:,} rows "
        f"({cleaning['pct_rows_removed']}%) were removed in total, leaving "
        f"{cleaning['final_rows']:,} clean records. No row was dropped "
        f"without being counted and explained here.", styles["Normal"]
    ))
    story.append(Spacer(1, 8))

    table_data = [["Step", "Rows Removed", "Rows Remaining", "Why"]]
    for step in cleaning["steps"]:
        table_data.append([
            Paragraph(step["step"], styles["Normal"]),
            f"{step.get('rows_removed', step.get('n_missing', '-')):,}"
            if isinstance(step.get('rows_removed', step.get('n_missing')), int) else "-",
            f"{step.get('rows_remaining', '-'):,}" if isinstance(step.get('rows_remaining'), int) else "-",
            Paragraph(step.get("justification", step.get("decision", "")), styles["Normal"]),
        ])
    story.append(make_table(table_data, col_widths=[1.5 * inch, 0.9 * inch, 0.9 * inch, 2.5 * inch]))

    if "missingness_correlation_check" in cleaning:
        check = cleaning["missingness_correlation_check"]
        story.append(Paragraph("Missing Data: Was It Random?", styles["SubHeading"]))
        story.append(Paragraph(
            f"Checked missingness against: {check['checked_against']}. "
            f"{check['finding']}", styles["Normal"]
        ))


def build_outlier_section(story, styles, cleaning):
    story.append(Paragraph("3. Outlier Detection", styles["SectionHeading"]))
    story.append(Paragraph(
        "Fare, distance, and tip values are all right-skewed (a small share "
        "of trips are legitimately long or expensive), which makes z-score "
        "unreliable and a plain statistical (IQR) rule prone to over-"
        "flagging normal trips. Instead, each feature was checked against a "
        "domain-informed ceiling (grounded in real NYC taxi operating "
        "limits) backed by a 99.5th-percentile safety net computed from "
        "this month's data. No row was silently deleted for being an "
        "outlier -- values were either capped (winsorized) or, where no "
        "safe replacement existed, left in place and flagged.",
        styles["Normal"]
    ))
    story.append(Spacer(1, 8))

    outliers = cleaning.get("outlier_detection", {})
    table_data = [["Feature", "Method", "Rows Flagged", "Action"]]
    for feature, info in outliers.items():
        table_data.append([
            feature,
            Paragraph(info["method"], styles["Normal"]),
            f"{info['rows_flagged']:,}",
            Paragraph(info["action"], styles["Normal"]),
        ])
    story.append(make_table(table_data, col_widths=[1.1 * inch, 2.1 * inch, 0.9 * inch, 1.7 * inch]))


def build_eda_section(story, styles):
    story.append(PageBreak())
    story.append(Paragraph("4. Exploratory Visuals", styles["SectionHeading"]))
    story.append(Paragraph(
        "A full set of univariate and bivariate charts was generated for "
        "every numerical and categorical feature (saved in images/). The "
        "three below illustrate the headline patterns.", styles["Normal"]
    ))

    highlights = [
        ("trip_duration_histogram.png", "Trip duration is right-skewed: most rides are short, with a long tail of longer trips."),
        ("fare_distribution.png", "Fare amount follows the same right-skewed shape as duration, as expected since fare scales with distance/time."),
        ("heatmap_hourly.png", "Trip volume varies strongly by hour and day of week -- the basis for the peak-vs-trough answer below."),
    ]
    for filename, caption in highlights:
        img = fitted_image(os.path.join(IMAGES_DIR, filename))
        if img:
            story.append(img)
            story.append(Paragraph(caption, styles["Normal"]))
            story.append(Spacer(1, 10))
        else:
            story.append(Paragraph(f"[missing chart: {filename}]", styles["Normal"]))


def build_business_section(story, styles, biz):
    story.append(PageBreak())
    story.append(Paragraph("5. Business Questions -- Answered", styles["SectionHeading"]))

    # 1. Peak vs trough
    p = biz["peak_vs_trough_hour"]
    story.append(Paragraph("Peak vs. Slowest Demand Hour", styles["SubHeading"]))
    story.append(Paragraph(
        f"Peak is {p['ratio']}x the trough "
        f"(hour {p['peak_hour']}:00 with {p['peak_count']:,} trips vs. "
        f"hour {p['trough_hour']}:00 with {p['trough_count']:,} trips).",
        styles["KeyNumber"]
    ))
    img = fitted_image(os.path.join(IMAGES_DIR, "business_peak_vs_trough_hour.png"))
    if img:
        story.append(img)

    # 2. Weekend vs weekday fare
    w = biz["weekend_vs_weekday_fare"]
    story.append(Paragraph("Weekend vs. Weekday Average Fare", styles["SubHeading"]))
    sig_text = "statistically significant" if w["statistically_significant"] else "not statistically significant"
    story.append(Paragraph(
        f"Weekend fares average ${w['weekend_mean_fare']} vs. ${w['weekday_mean_fare']} "
        f"on weekdays -- a difference of ${w['difference']} ({w['pct_difference']}%), "
        f"which is {sig_text} (Mann-Whitney U, p={w['p_value']:.4g}). "
        f"Note: with a dataset this large, statistical significance alone "
        f"doesn't mean the difference is large enough to act on -- the "
        f"percentage difference above is the more useful business signal.",
        styles["KeyNumber"]
    ))
    img = fitted_image(os.path.join(IMAGES_DIR, "business_weekend_vs_weekday_fare.png"))
    if img:
        story.append(img)

    story.append(PageBreak())

    # 3. Tip rate by payment type
    t = biz["tip_rate_by_payment_type"]
    story.append(Paragraph("Payment Type with Highest Average Tip Rate", styles["SubHeading"]))
    story.append(Paragraph(
        f"{t['top_payment_type']} has the highest average tip rate at "
        f"{t['top_avg_tip_rate_pct']}% of the fare, and accounts for "
        f"{t['top_share_of_trips_pct']}% of all trips. "
        f"(Cash tips are not captured by the taxi meter, so cash trips "
        f"structurally show near-zero recorded tips -- this reflects "
        f"reported tips, not true generosity by payment method.)",
        styles["KeyNumber"]
    ))
    img = fitted_image(os.path.join(IMAGES_DIR, "business_tip_rate_by_payment_type.png"))
    if img:
        story.append(img)

    # 4. Duration by day of week
    d = biz["avg_duration_by_dayofweek"]
    story.append(Paragraph("Average Trip Duration by Day of Week", styles["SubHeading"]))
    duration_line = ", ".join(f"{day}: {mins} min" for day, mins in d.items())
    story.append(Paragraph(duration_line, styles["KeyNumber"]))
    img = fitted_image(os.path.join(IMAGES_DIR, "business_avg_duration_by_day.png"))
    if img:
        story.append(img)

    story.append(PageBreak())

    # 5. Short trip fare per mile
    s = biz["short_trip_fare_per_mile"]
    story.append(Paragraph("Short Trips (Under 2 Miles) vs. Longer Trips", styles["SubHeading"]))
    story.append(Paragraph(
        f"{s['share_under_2mi_pct']}% of trips are under 2 miles. Those "
        f"short trips cost ${s['avg_fare_per_mile_under_2mi']} per mile on "
        f"average, vs. ${s['avg_fare_per_mile_2mi_plus']} per mile for "
        f"longer trips -- short trips cost {s['ratio']}x more per mile, "
        f"which is expected since the flat pickup/minimum-fare cost is "
        f"spread over fewer miles.",
        styles["KeyNumber"]
    ))
    img = fitted_image(os.path.join(IMAGES_DIR, "business_short_trip_fare_per_mile.png"))
    if img:
        story.append(img)


def build_limitations_section(story, styles):
    story.append(PageBreak())
    story.append(Paragraph("6. Limitations", styles["SectionHeading"]))
    story.append(Paragraph(
        "This analysis covers a single month, so seasonal patterns (e.g. "
        "holidays, weather) are not captured. Cash tips are not recorded "
        "by the metering system, so all tip-related figures reflect card "
        "payments only. Outlier capping changes the extreme values of a "
        "small share of rows (see Section 3); analyses re-run on the "
        "original uncapped data may shift slightly at the tail.",
        styles["Normal"]
    ))


def main():
    styles = build_styles()
    cleaning = load_json(CLEANING_SUMMARY_PATH)
    biz = load_json(BUSINESS_SUMMARY_PATH)

    os.makedirs("reports", exist_ok=True)
    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=letter,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
    )

    story = []
    build_title_page(story, styles, cleaning)
    build_objective_section(story, styles)
    build_cleaning_section(story, styles, cleaning)
    build_outlier_section(story, styles, cleaning)
    build_eda_section(story, styles)
    build_business_section(story, styles, biz)
    build_limitations_section(story, styles)

    doc.build(story)
    print(f"Report saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()