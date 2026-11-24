from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.services.business_service import BusinessService
from app.services.evaluation_service import EvaluationService
from app.api.schemas.api_models import ProductPriceUpdateRequest

router = APIRouter(prefix="/api", tags=["Business"])

@router.get("/business/overview")
def get_business_overview(
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = BusinessService(db)
    return svc.get_overview(store_id=x_store_id)

@router.get("/business/analytics")
def get_business_analytics(
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = BusinessService(db)
    return svc.get_analytics(store_id=x_store_id)

@router.get("/customers")
def get_customers(
    segment: Optional[str] = Query(None),
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = BusinessService(db)
    return svc.get_customers(segment=segment, store_id=x_store_id)

@router.get("/products")
def get_products(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = BusinessService(db)
    return svc.get_products(category=category, status=status, store_id=x_store_id)

@router.put("/products/{product_id}")
def update_product_price(
    product_id: str,
    req: ProductPriceUpdateRequest,
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = BusinessService(db)
    prod = svc.repo.update_product_price(product_id, req.cost_price, req.selling_price, store_id=x_store_id)
    if not prod:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
    return {
        "status": "SUCCESS",
        "product_id": prod.product_id,
        "product_name": prod.product_name,
        "cost_price": prod.cost_price,
        "selling_price": prod.selling_price
    }

@router.get("/evaluation")
def get_evaluation(
    execution_id: Optional[str] = Query(None),
    x_store_id: str = Header("STORE_001", alias="X-Store-Id"),
    db: Session = Depends(get_db)
):
    svc = EvaluationService(db)
    return svc.evaluate_system(execution_id=execution_id, store_id=x_store_id)
