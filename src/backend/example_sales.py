import json
import random
from datetime import datetime, timedelta
from pathlib import Path

SALES_FILE = Path("data/sales.json")


def generate_sample_sales():
    """Generate sample sales data if file doesn't exist."""
    categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
    sales = []

    start_date = datetime.now() - timedelta(days=180)

    for i in range(100):
        date = start_date + timedelta(days=random.randint(0, 180))
        sale = {
            "id": i + 1,
            "date": date.strftime("%Y-%m-%d"),
            "amount": round(random.uniform(50, 1000), 2),
            "category": random.choice(categories),
            "customer": f"Customer_{random.randint(1, 50)}",
        }
        sales.append(sale)

    return sales


def get_sales_data():
    """Load or generate sales data."""
    if not SALES_FILE.exists():
        SALES_FILE.parent.mkdir(parents=True, exist_ok=True)
        sales = generate_sample_sales()
        SALES_FILE.write_text(json.dumps(sales, indent=2), encoding="utf-8")
        return sales

    return json.loads(SALES_FILE.read_text(encoding="utf-8"))


def calculate_sales_metrics(sales_data):
    """Calculate key sales metrics."""
    if not sales_data:
        return {"total": 0, "average": 0, "best_month": "N/A", "growth": 0}

    total = sum(sale["amount"] for sale in sales_data)
    average = total / len(sales_data)

    monthly_totals: dict[str, float] = {}
    for sale in sales_data:
        month = sale["date"][:7]
        monthly_totals[month] = monthly_totals.get(month, 0) + sale["amount"]

    best_month = max(monthly_totals, key=monthly_totals.get) if monthly_totals else "N/A"

    months = sorted(monthly_totals.keys())
    if len(months) >= 2:
        growth = ((monthly_totals[months[-1]] - monthly_totals[months[0]]) / monthly_totals[months[0]]) * 100
    else:
        growth = 0

    return {"total": total, "average": average, "best_month": best_month, "growth": growth}


def get_monthly_sales(sales_data):
    """Get monthly sales data for charting."""
    monthly_data: dict[str, float] = {}
    for sale in sales_data:
        month = sale["date"][:7]
        monthly_data[month] = monthly_data.get(month, 0) + sale["amount"]

    return monthly_data
