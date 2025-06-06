# backend/app/schemas/pdf_schemas.py
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class PDFGenerationRequest(BaseModel):
    product_name: str
    base_part_code: str
    final_part_code: Optional[str] = None
    variants: List[Dict[str, Any]]
    selected_variant_id: Optional[int] = None
    selected_variant_index: Optional[int] = 0
    selected_options: Dict[str, Dict[str, Any]]
    accessories: Optional[List[Dict[str, Any]]] = []

class PDFGenerationResponse(BaseModel):
    message: str
    filename: str