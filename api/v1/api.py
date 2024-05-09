from fastapi import APIRouter
from api.v1.endpoints import returns, users,product,orders,address,pincode,package,currency,login,image,weight_freeze\
    ,weight_discrepancy,payment,account_transaction,indent
from api.v1.endpoints import (
    returns,
    shopify,
    users,
    product,
    orders,
    address,
    pincode,
    package,
    currency,
    login,
    image,
    weight_freeze,
    weight_discrepancy,
    payment,
    indent,
    kyc,
    company,
    dashboard,
    channel
)

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(product.router, prefix="/product", tags=["Product"])
api_router.include_router(returns.router, prefix="/return", tags=["Returns"])
api_router.include_router(orders.router, prefix="/order", tags=["Orders"])
api_router.include_router(address.router, prefix="/address", tags=["Address"])
api_router.include_router(pincode.router, prefix="/pincode", tags=["Pincode"])
api_router.include_router(package.router, prefix="/package", tags=["package"])
api_router.include_router(currency.router, prefix="/currency", tags=["Currency"])
api_router.include_router(login.router, prefix="/login", tags=["Login"])
api_router.include_router(image.router, prefix="/image", tags=["Image"])
api_router.include_router(
    weight_freeze.router, prefix="/weight_freeze", tags=["Weight Freeze"]
)
api_router.include_router(
    weight_discrepancy.router, prefix="/weight_discrepancy", tags=["Weight Discrepancy"]
)
api_router.include_router(payment.router, prefix="/payment", tags=["Payment"])
api_router.include_router(account_transaction.router, prefix="/account_transaction", tags=["Account Transaction"])
api_router.include_router(shopify.router, prefix="/shopify")
api_router.include_router(indent.router, prefix="/indent")
api_router.include_router(kyc.router, prefix="/kyc", tags=["Kyc"])
api_router.include_router(company.router, prefix="/company", tags=["Company"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(channel.router, prefix="/channel", tags=["channel"])