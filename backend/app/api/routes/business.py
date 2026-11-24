from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.services.business_service import BusinessService
from app.services.evaluation_service import EvaluationService
from app.api.schemas.api_models import ProductPriceUpdateRequest

router = APIRouter(prefix="/api", tags=["Business"])

@router.get("/business/overview")
def get_business_overview(db: Session = Depends(get_db)):
    svc = BusinessService(db)
    return svc.get_overview()

@router.get("/business/analytics")
def get_business_analytics(db: Session = Depends(get_db)):
    svc = BusinessService(db)
    return svc.get_analytics()

@router.get("/customers")
def get_customers(segment: Optional[str] = Query(None), db: Session = Depends(get_db)):
    svc = BusinessService(db)
    return svc.get_customers(segment=segment)

@router.get("/products")
def get_products(category: Optional[str] = Query(None), status: Optional[str] = Query(None), db: Session = Depends(get_db)):
    svc = BusinessService(db)
    return svc.get_products(category=category, status=status)

@router.put("/products/{product_id}")
def update_product_price(product_id: str, req: ProductPriceUpdateRequest, db: Session = Depends(get_db)):
    svc = BusinessService(db)
    prod = svc.repo.update_product_price(product_id, req.cost_price, req.selling_price)
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
def get_evaluation(execution_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    svc = EvaluationService(db)
    return svc.evaluate_system(execution_id=execution_id)
