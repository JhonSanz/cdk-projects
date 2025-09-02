import boto3
import os
import requests
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_to_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def lambda_handler(event, context):
    client = boto3.client("ce", region_name="us-east-1")  # Cost Explorer solo en us-east-1

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    month_start = today.replace(day=1)

    # --- Costo de ayer ---
    cost_yesterday = client.get_cost_and_usage(
        TimePeriod={"Start": str(yesterday), "End": str(today)},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
    )["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]

    # --- Costo de hoy ---
    cost_today = client.get_cost_and_usage(
        TimePeriod={"Start": str(today), "End": str(today + timedelta(days=1))},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
    )["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]

    # --- Top 10 servicios del mes ---
    top_services = client.get_cost_and_usage(
        TimePeriod={"Start": str(month_start), "End": str(today + timedelta(days=1))},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    groups = top_services["ResultsByTime"][0]["Groups"]
    service_costs = [
        (g["Keys"][0], float(g["Metrics"]["UnblendedCost"]["Amount"]))
        for g in groups
    ]
    service_costs.sort(key=lambda x: x[1], reverse=True)
    top10 = service_costs[:10]

    # --- Formar mensaje ---
    report = "📊 AWS Billing Report\n\n"
    report += f"💰 Costo de ayer ({yesterday}): ${float(cost_yesterday):.2f}\n"
    report += f"💵 Costo de hoy ({today}): ${float(cost_today):.2f}\n\n"
    report += "🔥 Top 10 servicios del mes:\n"
    for service, amount in top10:
        report += f" - {service}: ${amount:.2f}\n"

    send_to_telegram(report[:4000])
    return {"status": "done"}
