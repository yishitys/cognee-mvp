import csv
import json
import pathlib
import urllib.request
import zipfile


DATASETS = {
    "customer_churn": "https://www.kaggle.com/api/v1/datasets/download/hassanamin/customer-churn",
    "retail_sales_forecasting": "https://www.kaggle.com/api/v1/datasets/download/svizor/retail-sales-forecasting-data",
}


def download_dataset(name: str, url: str) -> list[dict[str, object]]:
    base_dir = pathlib.Path("demo_materials") / name
    base_dir.mkdir(parents=True, exist_ok=True)

    zip_path = base_dir / f"{name}.zip"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    zip_path.write_bytes(urllib.request.urlopen(request, timeout=60).read())

    raw_dir = base_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(raw_dir)

    summary = []
    for csv_path in sorted(raw_dir.glob("*.csv")):
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            row_count = sum(1 for _ in reader)
        summary.append(
            {
                "file": str(csv_path),
                "rows": row_count,
                "columns": header,
            }
        )

    (base_dir / "dataset_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    all_summaries = {}
    for name, url in DATASETS.items():
        all_summaries[name] = download_dataset(name, url)

    pathlib.Path("demo_materials/dataset_summaries.json").write_text(
        json.dumps(all_summaries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(all_summaries, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
