from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import httpx
import os
import logging
import sys

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
sys.stdout.reconfigure(line_buffering=True)

app = FastAPI(title="Prove Me Wrong API", version="1.0.0")

# Use Railway's PORT environment variable or default to 8000
PORT = int(os.getenv("PORT", 8000))

GENERATOR_URL = "http://localhost:8000"  # Generator service port
RESOLVER_URL = "http://localhost:8001"   # Resolver service port
COORDINATOR_URL = "http://localhost:8002"  # Coordinator agent port

# Updated proxy with coordinator agent support
@app.get("/")
async def root():
    return {
        "message": "Prove Me Wrong API",
        "services": {
            "generator": "/generator/*",
            "resolver": "/resolver/*",
            "coordinator": "/coordinator/*"
        },
        "endpoints": {
            "create_market": "POST /coordinator/create-market",
            "resolve_market": "POST /coordinator/resolve-market",
            "list_markets": "GET /coordinator/markets",
            "get_outcome": "GET /coordinator/resolutions/{market_id}/outcome",
            "resolve_all": "POST /coordinator/resolve-all",
            "health": "GET /coordinator/health"
        }
    }

@app.api_route("/generator/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def generator_proxy(request: Request, path: str):
    """Proxy requests to generator service"""
    url = f"{GENERATOR_URL}/{path}"
    
    # Log the request for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔀 Proxying to generator: {request.method} {url}")
    
    # Get request body if it exists
    body = None
    if request.method in ["POST", "PUT"]:
        body = await request.body()
    
    # Forward headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            logger.info(f"✅ Generator response: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Generator proxy error: {e}")
        raise
    
    # Return response content and status code properly
    from fastapi.responses import Response
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

@app.api_route("/resolver/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def resolver_proxy(request: Request, path: str):
    """Proxy requests to resolver service"""
    url = f"{RESOLVER_URL}/{path}"
    
    # Log the request for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔀 Proxying to resolver: {request.method} {url}")
    
    # Get request body if it exists
    body = None
    if request.method in ["POST", "PUT"]:
        body = await request.body()
    
    # Forward headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            logger.info(f"✅ Resolver response: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Resolver proxy error: {e}")
        raise
    
    # Return response content and status code properly
    from fastapi.responses import Response
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

@app.api_route("/coordinator/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def coordinator_proxy(request: Request, path: str):
    """Proxy requests to coordinator agent"""
    url = f"{COORDINATOR_URL}/{path}"
    
    # Log the request for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔀 Proxying to coordinator: {request.method} {url}")
    
    # Get request body if it exists
    body = None
    if request.method in ["POST", "PUT"]:
        body = await request.body()
    
    # Forward headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            logger.info(f"✅ Coordinator response: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Coordinator proxy error: {e}")
        raise
    
    # Return response content and status code properly
    from fastapi.responses import Response
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

@app.get("/health")
async def health():
    """Health check for all services"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            generator_health = await client.get(f"{GENERATOR_URL}/health")
            resolver_health = await client.get(f"{RESOLVER_URL}/health")
            coordinator_health = await client.get(f"{COORDINATOR_URL}/health")
            
            return {
                "status": "healthy",
                "generator": generator_health.status_code == 200,
                "resolver": resolver_health.status_code == 200,
                "coordinator": coordinator_health.status_code == 200
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        } 