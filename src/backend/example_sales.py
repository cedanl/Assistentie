import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st

SALES_FILE = Path("data/sales.json")


def generate_sample_sales() -> list[dict]:
    """Generate sample sales data if file doesn't exist."""
    categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
    start_date = datetime.now() - timedelta(days=180)
    return [
        {
            "id": i + 1,
            "date": (start_date + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d"),
            "amount": round(random.uniform(50, 1000), 2),
            "category": random.choice(categories),
            "customer": f"Customer_{random.randint(1, 50)}",
        }
        for i in range(100)
    ]


@st.cache_data
def get_sales_data() -> list[dict]:
    """Load or generate sales data — cached across Streamlit reruns."""
    if not SALES_FILE.exists():
        SALES_FILE.parent.mkdir(parents=True, exist_ok=True)
        sales = generate_sample_sales()
        SALES_FILE.write_text(json.dumps(sales, indent=2), encoding="utf-8")
        return sales
    return json.loads(SALES_FILE.read_text(encoding="utf-8"))


def get_monthly_sales(sales_data: list[dict]) -> dict[str, float]:
    """Sommeer omzet per maand (YYYY-MM-sleutel) — gebruikt voor chart en metrics."""
    monthly: dict[str, float] = {}
    for sale in sales_data:
        month = sale["date"][:7]
        monthly[month] = monthly.get(month, 0.0) + sale["amount"]
    return monthly


def calculate_sales_metrics(sales_data: list[dict]) -> dict[str, float | str]:
    """Calculate key sales metrics."""
    if not sales_data:
        return {"total": 0, "average": 0, "best_month": "N/A", "growth": 0}

    total = sum(sale["amount"] for sale in sales_data)
    average = total / len(sales_data)
    monthly_totals = get_monthly_sales(sales_data)
    best_month = max(monthly_totals, key=lambda m: monthly_totals[m]) if monthly_totals else "N/A"

    months = sorted(monthly_totals.keys())
    growth = (
        ((monthly_totals[months[-1]] - monthly_totals[months[0]]) / monthly_totals[months[0]]) * 100
        if len(months) >= 2
        else 0
    )
    return {"total": total, "average": average, "best_month": best_month, "growth": growth}


def get_sales_by_category(sales_data: list[dict]) -> dict[str, float]:
    """Sommeer omzet per categorie — voor de bar chart in de Sales pagina."""
    totals: dict[str, float] = {}
    for sale in sales_data:
        totals[sale["category"]] = totals.get(sale["category"], 0.0) + sale["amount"]
    return totals
