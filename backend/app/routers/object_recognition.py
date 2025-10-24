from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from ..services.computer_vision import predict_image

router = APIRouter()



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
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {e}"
        )