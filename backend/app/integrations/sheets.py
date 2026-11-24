import csv
import io
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.models import Product
from app.database.repository import BusinessRepository

class SheetsIntegration:
    REQUIRED_PRODUCT_COLUMNS = ["product_id", "product_name", "category", "cost_price", "selling_price", "current_stock", "supplier_name"]

    @classmethod
    def preview_csv_import(cls, csv_content: str, db: Session, store_id: str = "STORE_001") -> Dict[str, Any]:
        """
        Parses CSV, validates schema, identifies duplicates vs new products,
        and returns a structured preview without modifying database records.
        """
        reader = csv.DictReader(io.StringIO(csv_content.strip()))
        headers = reader.fieldnames or []

        # Check required columns
        missing = [col for col in cls.REQUIRED_PRODUCT_COLUMNS if col not in headers]
        if missing:
            return {
                "success": False,
                "error": f"Missing required columns in CSV: {', '.join(missing)}"
            }

        repo = BusinessRepository(db)
        existing_products = {p.product_id: p for p in repo.get_products(store_id=store_id)}

        valid_rows = []
        updates = []
        new_items = []
        errors = []

        for idx, row in enumerate(reader, start=1):
            pid = row.get("product_id", "").strip()
            name = row.get("product_name", "").strip()
            if not pid or not name:
                errors.append(f"Row {idx}: Missing product ID or name.")
                continue

            try:
                cost = float(row.get("cost_price", 0))
                sell = float(row.get("selling_price", 0))
                stock = int(row.get("current_stock", 0))
            except ValueError:
                errors.append(f"Row {idx} ({pid}): Invalid numeric values for cost, sell, or stock.")
                continue

            if sell < cost:
                errors.append(f"Row {idx} ({pid}): Selling price (₹{sell}) is below cost price (₹{cost}).")
                continue

            item_data = {
                "product_id": pid,
                "product_name": name,
                "category": row.get("category", "General"),
                "cost_price": cost,
                "selling_price": sell,
                "current_stock": stock,
                "minimum_stock": int(row.get("minimum_stock", 10)),
                "monthly_units_sold": int(row.get("monthly_units_sold", 0)),
                "expiry_date": row.get("expiry_date", "2026-12-31"),
                "supplier_name": row.get("supplier_name", "Local Supplier"),
                "status": "HEALTHY",
                "store_id": store_id
            }

            if pid in existing_products:
                updates.append(item_data)
            else:
                new_items.append(item_data)

            valid_rows.append(item_data)

        return {
            "success": True,
            "total_rows_parsed": len(valid_rows) + len(errors),
            "valid_count": len(valid_rows),
            "new_products_count": len(new_items),
            "updated_products_count": len(updates),
            "errors": errors,
            "preview_items": valid_rows[:10]
        }

    @classmethod
    def confirm_csv_import(cls, items: List[Dict[str, Any]], db: Session, store_id: str = "STORE_001") -> Dict[str, Any]:
        """
        Safely commits validated products to the store database.
        """
        imported = 0
        updated = 0
        for item in items:
            prod = db.query(Product).filter_by(product_id=item["product_id"], store_id=store_id).first()
            if not prod:
                new_prod = Product(**item)
                db.add(new_prod)
                imported += 1
            else:
                for k, v in item.items():
                    setattr(prod, k, v)
                updated += 1
        db.commit()

        repo = BusinessRepository(db)
        repo.log_audit(
            event_type="SHEETS_IMPORT",
            agent_name="System",
            details=f"Imported {imported} new products, updated {updated} existing products from Google Sheets/CSV.",
            store_id=store_id
        )

        return {
            "success": True,
            "imported_count": imported,
            "updated_count": updated,
            "message": f"Successfully processed {imported + updated} catalog items."
        }
