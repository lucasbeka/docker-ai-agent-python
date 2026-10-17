import os

from pydantic import BaseModel, Field

class EmailMessageSchema(BaseModel):
    subject: str = Field(description="Short email subject line, max 8 words")
    contents: str = Field(description="Full plain text email body")
    invalid_request: bool = Field(default=False, description="True only if the request is impossible to fulfill")
