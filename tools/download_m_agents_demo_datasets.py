import csv
import json
import pathlib
import urllib.request
import zipfile


DATASETS = {
    "crm_sales_opportunities": "https://www.kaggle.com/api/v1/datasets/download/iamlynn/crm-sales-opportunities",
    "crm_sales_opportunities_alt": "https://www.kaggle.com/api/v1/datasets/download/innocentmfa/crm-sales-opportunities",
    "customer_support_tickets": "https://www.kaggle.com/api/v1/datasets/download/suraj520/customer-support-ticket-dataset",
    "saas_customer_churn": "https://www.kaggle.com/api/v1/datasets/download/suhanigupta04/saas-customer-churn-prediction-dataset",
}

BASE_DIR = pathlib.Path("demo_materials/m_agents_rehearsal")


def csv_summary(csv_path: pathlib.Path) -> dict[str, object]:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with csv_path.open(newline="", encoding=encoding) as handle:
                reader = csv.reader(handle)
                header = next(reader)
                row_count = sum(1 for _ in reader)
            return {
                "file": str(csv_path),
                "rows": row_count,
                "columns": header,
                "encoding": encoding,
            }
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", b"", 0, 1, f"Could not decode {csv_path}")


def download_dataset(name: str, url: str) -> list[dict[str, object]]:
    dataset_dir = BASE_DIR / name
    raw_dir = dataset_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    zip_path = dataset_dir / f"{name}.zip"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    zip_path.write_bytes(urllib.request.urlopen(request, timeout=120).read())

    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(raw_dir)

    summaries = []
    for csv_path in sorted(raw_dir.rglob("*.csv")):
        summaries.append(csv_summary(csv_path))

    (dataset_dir / "dataset_summary.json").write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summaries


def main() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    all_summaries = {}
    for name, url in DATASETS.items():
        all_summaries[name] = download_dataset(name, url)

    (BASE_DIR / "dataset_summaries.json").write_text(
        json.dumps(all_summaries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(all_summaries, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
