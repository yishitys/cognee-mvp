import csv
import datetime as dt
import json
import pathlib
import random


BASE_DIR = pathlib.Path("demo_materials/m_agents_rehearsal")
RAW_CRM = BASE_DIR / "crm_sales_opportunities_alt/raw"
RAW_SUPPORT = BASE_DIR / "customer_support_tickets/raw/customer_support_tickets.csv"
RAW_CHURN = BASE_DIR / "saas_customer_churn/raw/train.csv"
OUT_DIR = BASE_DIR / "assembled_crisis_pack"

RANDOM_SEED = 42
LOGIN_FREQUENCY = {
    "Daily": 7,
    "Several times a week": 4,
    "Weekly": 1,
    "Monthly": 0,
}


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: pathlib.Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def alias_for(account_name: str, idx: int) -> str:
    if idx % 5 == 0:
        return account_name.replace(" ", "")
    if idx % 5 == 1:
        return f"{account_name} Inc"
    if idx % 5 == 2:
        return f"{account_name} Ltd"
    if idx % 5 == 3:
        return account_name.lower()
    return account_name


def main() -> None:
    random.seed(RANDOM_SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    crm_accounts = read_csv(RAW_CRM / "accounts.csv")
    pipeline = read_csv(RAW_CRM / "sales_pipeline.csv")
    sales_teams = read_csv(RAW_CRM / "sales_teams.csv")
    support = read_csv(RAW_SUPPORT)
    churn = read_csv(RAW_CHURN)

    selected_accounts = crm_accounts[:40]
    account_ids = {row["account"]: f"ACC-{idx + 1:04d}" for idx, row in enumerate(selected_accounts)}
    team_by_agent = {row["sales_agent"]: row for row in sales_teams}
    products = ["API Platform", "Workflow Studio", "Admin Console", "Data Sync", "Billing"]
    regions = ["NA", "EMEA", "APAC", "LATAM"]
    incident_start = dt.date(2026, 5, 18)

    accounts = []
    contacts = []
    for idx, row in enumerate(selected_accounts):
        account_id = account_ids[row["account"]]
        revenue = int(float(row["revenue"] or 1))
        arr = max(25_000, int(revenue * random.uniform(0.04, 0.12)))
        segment = "Strategic" if arr >= 500_000 else "Enterprise" if arr >= 180_000 else "Commercial"
        renewal_date = dt.date(2026, 6, 20) + dt.timedelta(days=random.randint(0, 120))
        accounts.append(
            {
                "account_id": account_id,
                "account_name": row["account"],
                "account_alias": alias_for(row["account"], idx),
                "sector": row["sector"],
                "arr": arr,
                "segment": segment,
                "renewal_date": renewal_date.isoformat(),
                "owner": random.choice(sales_teams)["sales_agent"],
                "region": random.choice(regions),
            }
        )
        contacts.append(
            {
                "contact_id": f"CON-{idx + 1:04d}",
                "account_id": account_id,
                "contact_name": f"{row['account'].split()[0]} Champion",
                "title": random.choice(["VP Operations", "Head of IT", "Director of RevOps", "Customer Success Lead"]),
                "email": f"champion{idx + 1}@{row['account'].lower().replace(' ', '').replace(',', '')}.example.com",
            }
        )

    account_by_name = {row["account_name"]: row for row in accounts}
    account_names = list(account_by_name)

    opportunities = []
    for idx, row in enumerate(pipeline):
        if row["account"] not in account_ids:
            continue
        if len(opportunities) >= 650:
            break
        team = team_by_agent.get(row["sales_agent"], {})
        opportunities.append(
            {
                "opportunity_id": row["opportunity_id"],
                "account_id": account_ids[row["account"]],
                "account_name": row["account"],
                "sales_agent": row["sales_agent"],
                "manager": team.get("manager", ""),
                "regional_office": team.get("regional_office", ""),
                "product": row["product"],
                "stage": row["deal_stage"],
                "amount": row["close_value"] or 0,
                "close_date": row["close_date"],
            }
        )

    usage_rows = []
    date_start = dt.date(2026, 5, 1)
    churn_sample = churn[: len(accounts)]
    for idx, account in enumerate(accounts):
        signal = churn_sample[idx]
        login_frequency = LOGIN_FREQUENCY.get(signal["Login_Frequency"], 2)
        base_active = max(20, login_frequency * random.randint(8, 16))
        base_usage = max(30, int(float(signal["Daily_Usage_Mins"])))
        affected = account["segment"] in {"Strategic", "Enterprise"} and idx % 3 != 0
        for day in range(35):
            current_date = date_start + dt.timedelta(days=day)
            incident_day = current_date >= incident_start
            usage_drop = 0.45 if affected and incident_day else 1.0
            api_errors = random.randint(0, 8)
            if affected and incident_day:
                api_errors += random.randint(20, 70)
            usage_rows.append(
                {
                    "account_id": account["account_id"],
                    "date": current_date.isoformat(),
                    "active_users": int(base_active * usage_drop + random.randint(-8, 8)),
                    "api_errors": api_errors,
                    "core_workflows_completed": int(base_usage * usage_drop + random.randint(-10, 10)),
                    "login_frequency": signal["Login_Frequency"],
                    "daily_usage_mins": signal["Daily_Usage_Mins"],
                }
            )

    tickets = []
    severity_map = {"Low": "low", "Medium": "medium", "High": "high", "Critical": "critical"}
    for idx, row in enumerate(support[:900]):
        account = accounts[idx % len(accounts)]
        noisy_name = account["account_alias"] if idx % 4 == 0 else account["account_name"]
        missing_id = idx % 11 == 0
        product_area = random.choice(products)
        severity = severity_map.get(row["Ticket Priority"], row["Ticket Priority"].lower())
        if product_area in {"API Platform", "Data Sync"} and idx % 7 == 0:
            severity = random.choice(["high", "critical"])
        ticket_date = incident_start + dt.timedelta(days=random.randint(-8, 13))
        tickets.append(
            {
                "ticket_id": row["Ticket ID"],
                "account_id": "" if missing_id else account["account_id"],
                "account_name": noisy_name,
                "contact_email": contacts[idx % len(contacts)]["email"],
                "product_area": product_area,
                "reported_severity": row["Ticket Priority"],
                "normalized_severity": severity,
                "status": row["Ticket Status"],
                "created_at": ticket_date.isoformat(),
                "subject": row["Ticket Subject"],
                "description": row["Ticket Description"],
                "customer_satisfaction": row["Customer Satisfaction Rating"],
            }
        )

    incident_log = [
        {
            "incident_id": "INC-2026-05-API-001",
            "start_time": "2026-05-18T03:10:00",
            "end_time": "2026-05-21T14:30:00",
            "product_area": "API Platform",
            "customer_impact": "Elevated API errors and degraded workflow completion for enterprise tenants.",
            "root_cause": "Retry storm after a queue worker deployment caused backlog growth.",
        },
        {
            "incident_id": "INC-2026-05-SYNC-002",
            "start_time": "2026-05-23T10:45:00",
            "end_time": "2026-05-23T19:20:00",
            "product_area": "Data Sync",
            "customer_impact": "Delayed sync jobs and duplicate status notifications.",
            "root_cause": "Schema migration produced conflicting sync-state records.",
        },
    ]

    write_csv(OUT_DIR / "accounts.csv", accounts, list(accounts[0].keys()))
    write_csv(OUT_DIR / "contacts.csv", contacts, list(contacts[0].keys()))
    write_csv(OUT_DIR / "opportunities.csv", opportunities, list(opportunities[0].keys()))
    write_csv(OUT_DIR / "usage_events.csv", usage_rows, list(usage_rows[0].keys()))
    write_csv(OUT_DIR / "support_tickets.csv", tickets, list(tickets[0].keys()))
    write_csv(OUT_DIR / "incident_log.csv", incident_log, list(incident_log[0].keys()))

    summary = {
        "source_datasets": {
            "crm_sales_opportunities_alt": "Kaggle innocentmfa/crm-sales-opportunities",
            "customer_support_tickets": "Kaggle suraj520/customer-support-ticket-dataset",
            "saas_customer_churn": "Kaggle suhanigupta04/saas-customer-churn-prediction-dataset",
        },
        "assembled_tables": {
            "accounts.csv": len(accounts),
            "contacts.csv": len(contacts),
            "opportunities.csv": len(opportunities),
            "usage_events.csv": len(usage_rows),
            "support_tickets.csv": len(tickets),
            "incident_log.csv": len(incident_log),
        },
        "intentional_data_quality_issues": [
            "Account aliases differ across accounts and support tickets.",
            "Some support tickets omit account_id and require entity resolution.",
            "Reported severity and normalized severity are not always aligned.",
            "Strategic and enterprise accounts show post-incident usage drops.",
            "Incidents affect product areas that appear in support tickets and usage signals.",
        ],
    }
    (OUT_DIR / "README.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
