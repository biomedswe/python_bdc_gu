
import pandas as pd
from pathlib import Path
import smtplib
import os
from email.message import EmailMessage

INPUT_FILE = Path(__file__).resolve().parent / "samples.txt"

# Read the data
df = pd.read_csv(INPUT_FILE)

# Extract origin and identify failed samples
df["origin"] = df["sample"].str[1]
df["failed"] = (df["pct_covered_bases"] < 95) | (~df["qc_pass"])

# Calculate failure statistics
results = df.groupby("origin")["failed"].agg(["sum", "count"])
results["percentage"] = results["sum"] / results["count"] * 100

# Create the report
report = ["Weekly sequencing quality report", ""]

for origin, row in results.iterrows():
    percentage = row["percentage"]

    report.append(
        f"Origin {origin}: {int(row['sum'])}/{int(row['count'])} "
        f"failed ({percentage:.2f}%)"
    )

    if percentage > 10:
        report.append(
            f"WARNING: Origin {origin} exceeds the 10% threshold!"
        )

# Combine report lines into a single string
message_text = "\n".join(report)

# Display the report
print(message_text)

# Save the report
output_file = INPUT_FILE.parent / "quality_report.txt"
output_file.write_text(message_text + "\n")

# Email configuration (I would implement e.g. something like this for sending the notification by email)

# sender = os.environ["QC_EMAIL_SENDER"]
# receiver = os.environ["QC_EMAIL_RECEIVER"]
# password = os.environ["QC_EMAIL_PASSWORD"]
# smtp_server = os.environ["QC_SMTP_SERVER"]
# smtp_port = int(os.environ.get("QC_SMTP_PORT", "587"))

# # Create the email
# msg = EmailMessage()
# msg["From"] = sender
# msg["To"] = receiver
# msg["Subject"] = "Weekly sequencing quality report"
# msg.set_content(message_text)

# # Send the email securely
# with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
#     server.starttls()
#     server.login(sender, password)
#     server.send_message(msg)

# print("Email notification sent.")


# For automatization of running this script, I would use 
# crontab -e
# Then configure it to run every Monday at 08:00:
# 0 8 * * 1 /path/to/python /path/to/QC_warning.py.py
