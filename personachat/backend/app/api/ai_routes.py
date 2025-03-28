from fastapi import APIRouter, HTTPException
from typing import List
from app.services.ai_service import AIServiceManager

router = APIRouter(prefix="/providers", tags=["ai_providers"])

def get_ai_service_manager() -> AIServiceManager:
    """Dependency to get the AI service manager instance"""
    from app.main import ai_service_manager
    return ai_service_manager

@router.get("/", response_model=List[str])
async def list_providers(ai_service: AIServiceManager = Depends(get_ai_service_manager)):
    """List all available AI providers"""
    return ai_service.get_available_providers()

@router.get("/{provider_name}/models", response_model=List[str])
async def list_provider_models(
    provider_name: str, 
    ai_service: AIServiceManager = Depends(get_ai_service_manager)
):
    """List available models for a specific provider"""
    try:
        models = await ai_service.get_models_for_provider(provider_name)
        if not models:
            raise HTTPException(
                status_code=404,
                detail=f"No models found for provider '{provider_name}'"
            )
        return models
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Error getting models for provider '{provider_name}': {str(e)}"
        )