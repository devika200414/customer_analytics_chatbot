import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

doc = SimpleDocTemplate("Customer_Analytics_Report.pdf")
story = []

# ----------------------------
# Title
# ----------------------------
story.append(Paragraph("Customer Analytics Report", styles["Title"]))
story.append(Paragraph("<br/><br/>", styles["Normal"]))

# ----------------------------
# Load Data
# ----------------------------
rfm = pd.read_csv("data/rfm_segmented.csv")
churn = pd.read_csv("data/customer_churn_analysis.csv")
monthly = pd.read_csv("data/monthly_revenue_Analysis.csv")
country = pd.read_csv("data/country_revenue_Analysis.csv")

# ----------------------------
# Project Overview
# ----------------------------
story.append(Paragraph("Project Overview", styles["Heading1"]))
story.append(Paragraph(
    "This report analyzes customer behavior using RFM segmentation, churn analysis and revenue trends. "
    "The objective is to identify valuable customers, customers likely to churn and business growth opportunities.",
    styles["BodyText"]
))

# ----------------------------
# Dataset Summary
# ----------------------------
story.append(Paragraph("Dataset Summary", styles["Heading1"]))

story.append(Paragraph(f"Total Customers : {len(rfm)}", styles["BodyText"]))

if "CustomerID" in rfm.columns:
    story.append(
        Paragraph(f"Unique Customers : {rfm['CustomerID'].nunique()}",
                  styles["BodyText"])
    )

story.append(Paragraph("<br/>", styles["BodyText"]))

# ----------------------------
# Customer Segmentation
# ----------------------------
story.append(Paragraph("Customer Segmentation", styles["Heading1"]))

segment_counts = rfm["Segment"].value_counts()

for segment, count in segment_counts.items():
    story.append(
        Paragraph(f"{segment}: {count} customers",
                  styles["BodyText"])
    )

story.append(Paragraph("<br/>", styles["BodyText"]))

# ----------------------------
# Churn Analysis
# ----------------------------
story.append(Paragraph("Customer Churn Analysis", styles["Heading1"]))

if "Churn" in churn.columns:

    churned = (churn["Churn"] == "Yes").sum()
    active = (churn["Churn"] == "No").sum()

    story.append(
        Paragraph(f"Churned Customers : {churned}",
                  styles["BodyText"])
    )

    story.append(
        Paragraph(f"Active Customers : {active}",
                  styles["BodyText"])
    )

story.append(Paragraph("<br/>", styles["BodyText"]))

# ----------------------------
# Monthly Revenue
# ----------------------------
story.append(Paragraph("Monthly Revenue Analysis", styles["Heading1"]))

story.append(
    Paragraph(
        monthly.head(12).to_string(index=False),
        styles["Code"]
    )
)

story.append(Paragraph("<br/>", styles["BodyText"]))

# ----------------------------
# Country Revenue
# ----------------------------
story.append(Paragraph("Country Revenue Analysis", styles["Heading1"]))

story.append(
    Paragraph(
        country.head(10).to_string(index=False),
        styles["Code"]
    )
)

story.append(Paragraph("<br/>", styles["BodyText"]))

# ----------------------------
# Business Recommendations
# ----------------------------
story.append(Paragraph("Business Recommendations", styles["Heading1"]))

recommendations = [
    "Retain At Risk customers through targeted offers.",
    "Reward Champion customers with loyalty programs.",
    "Increase repeat purchases using personalized campaigns.",
    "Monitor churn probability regularly.",
    "Focus marketing efforts on high-revenue countries."
]

for rec in recommendations:
    story.append(Paragraph("• " + rec, styles["BodyText"]))

# ----------------------------
# Finish
# ----------------------------
doc.build(story)

print("Customer_Analytics_Report.pdf created successfully!")