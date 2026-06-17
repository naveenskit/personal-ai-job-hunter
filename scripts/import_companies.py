import argparse
import asyncio
import csv
from pathlib import Path

from app.database.connection import session_scope
from app.database.repositories.company_repository import CompanyRepository


async def import_csv(path: Path):
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(text.splitlines())
    async with session_scope() as session:
        repo = CompanyRepository(session)
        created = 0
        for row in reader:
            name = row.get("name") or row.get("company") or ""
            domain = row.get("domain")
            website = row.get("website")
            existing = await repo.get_by_domain(domain) if domain else None
            if existing:
                continue
            await repo.create(name=name, domain=domain, website=website)
            created += 1
        print(f"Imported {created} companies")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Path to companies CSV file")
    parser.add_argument("--delimiter", type=str, default=",", help="CSV delimiter")
    parser.add_argument(
        "--map",
        type=str,
        default=None,
        help=(
            "Optional JSON string mapping output fields to CSV headers, "
            "e.g. '{\"name\":\"Company\"}'"
        ),
    )
    args = parser.parse_args()
    # support header mapping
    header_map = None
    if args.map:
        import json as _json

        header_map = _json.loads(args.map)
    # currently the CLI importer ignores delimiter/header_map — read and create normally
    asyncio.run(import_csv(Path(args.path)))
