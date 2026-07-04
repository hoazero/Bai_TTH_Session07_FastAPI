from datetime import datetime
from fastapi import FastAPI, status, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

promo_codes_db = {
    "SUMMER25": {"code": "SUMMER25", "discount_rate": 0.15, "max_budget": 50000000, "is_active": True},
    "WELCOME50": {"code": "WELCOME50", "discount_rate": 0.50, "max_budget": 10000000, "is_active": False}
}


class PromoInternal(BaseModel):
    code: str
    discount_rate: float
    max_budget: int  
    is_active: bool


class PromoPublic(BaseModel):
    code: str
    discount_rate: float


@app.exception_handler(HTTPException)
def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "data": None,
            "error": getattr(exc, "error_type", "Bad Request" if exc.status_code == 400 else "Not Found"),
            "message": exc.detail,
            "timestamp": datetime.time().isoformat(),
            "path": request.url.path
        }
    )


@app.get(
    "/promos/{code}", 
    response_model=PromoPublic, 
    status_code=status.HTTP_200_OK
)
def get_promo(code: str):
    promo_key = code.upper()

    if promo_key not in promo_codes_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Mã giảm giá không tồn tại"
        )
        
    promo_data = promo_codes_db[promo_key]

    if not promo_data["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Mã giảm giá đã hết hạn sử dụng"
        )
        
    return promo_data