
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
import base64
import io
from PIL import Image
from ..Services.image_recognition import predict_image

router = APIRouter()

# 1. Crie um schema Pydantic para receber a string Base64
class ImageRequest(BaseModel):
    image_base64: str

# 2. Modifique o endpoint para receber o schema
@router.post("/process-photo/")
async def process_photo_endpoint(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado não é uma imagem."
        )

    try:
        image_bytes = await file.read()
        prediction = predict_image(image_bytes)
        
        if "error" in prediction:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=prediction["error"]
            )
            
        return {"status": "success", "data": prediction}

    except HTTPException as e:
        # Reaproveita a exceção se já for um HTTPException
        raise e
    except Exception as e:
        # Lida com qualquer outro erro interno
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {e}"
        )
