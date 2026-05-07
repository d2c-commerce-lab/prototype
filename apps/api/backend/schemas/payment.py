from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PaymentSimulationRequest(BaseModel):
    order_id: UUID
    payment_method: str = Field(min_length=1, max_length=50)
    simulate_result: str = Field(pattern="^(success|failed)$")


class PaymentSimulationResponse(BaseModel):
    payment_id: UUID
    order_id: UUID
    payment_method: str
    payment_status: str
    requested_amount: Decimal
    approved_amount: Decimal
    failed_reason: str | None = None
    paid_at: datetime | None = None
    created_at: datetime
    message: str