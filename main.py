from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import os

app = FastAPI()

NVIDIA_API_KEY = os.getenv("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")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

# DeepSeek model name on NVIDIA NIM
# You'll need to verify the exact model name from build.nvidia.com
DEEPSEEK_MODEL = "deepseek-ai/deepseek-v3.2"  # Update this with the correct model name

@app.get("/")
async def root():
    return {
        "status": "OpenAI-compatible NVIDIA NIM Proxy (DeepSeek V3)",
        "model": DEEPSEEK_MODEL,
        "nvidia_configured": bool(NVIDIA_API_KEY)
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
        
        # Override model with DeepSeek on NVIDIA NIM
        # Use the exact model identifier from NVIDIA catalog
        if body.get("model"):
            body["model"] = DEEPSEEK_MODEL
        else:
            body["model"] = DEEPSEEK_MODEL
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{NVIDIA_BASE_URL}/chat/completions",
                json=body,
                headers={
                    "Authorization": f"Bearer {NVIDIA_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=120.0
            )
            
            if body.get("stream"):
                async def generate():
                    async for chunk in response.aiter_bytes():
                        yield chunk
                return StreamingResponse(generate(), media_type="text/event-stream")
            
            return JSONResponse(content=response.json(), status_code=response.status_code)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": DEEPSEEK_MODEL,
                "object": "model",
                "owned_by": "nvidia"
            },
            {
                "id": "deepseek-v3",
                "object": "model",
                "owned_by": "nvidia"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)