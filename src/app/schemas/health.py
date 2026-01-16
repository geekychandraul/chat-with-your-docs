from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: str
    environment: str
    version: str
    timestamp: str
