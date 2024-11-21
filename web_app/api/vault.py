from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from decimal import Decimal
import logging
from sqlalchemy.orm import Session

from web_app.db.models import VaultDeposit
from web_app.db.database import get_database
from web_app.schemas.vault import VaultDepositRequest, VaultDepositResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vault", tags=["vault"])

@router.post("/deposit", response_model=VaultDepositResponse)
def deposit_to_vault(
    request: VaultDepositRequest, 
    db: Session = Depends(get_database)
) -> VaultDepositResponse:

    try:
        logger.info(f"Processing deposit request for wallet {request.wallet_id}")
        
        # Create vault deposit record
        deposit = VaultDeposit(
            wallet_id=request.wallet_id,
            amount=request.amount,
            symbol=request.symbol,
            status="pending"
        )
        
        db.add(deposit)
        db.commit()
        db.refresh(deposit)
        
        logger.info(f"Created deposit record with ID {deposit.id}")

        return VaultDepositResponse(
            deposit_id=deposit.id,
            wallet_id=deposit.wallet_id,
            amount=deposit.amount,
            symbol=deposit.symbol,
            status=deposit.status
        )

    except Exception as e:
        logger.error(f"Error processing deposit: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process deposit: {str(e)}"
        )