from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import requests
import json
import os
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import schedule
import time
import threading
from web3 import Web3
from eth_account import Account
import hashlib
from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, init_db, Resolution, SessionLocal

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Force immediate flush for Railway logs
import sys
sys.stdout.reconfigure(line_buffering=True)

app = FastAPI(title="Market Resolver Agent", version="1.0.0")

# ASI-1 Mini API Configuration
ASI_API_URL = "https://api.asi1.ai/v1/chat/completions"
ASI_API_KEY = os.getenv("ASI_API_KEY", "sk_a1d55fd6b1ba47ddadc98bd1e8048e56ff00c4736c844a9db4aab791d33f0989")
MODEL_NAME = "asi1-mini"

# Generator API configuration
GENERATOR_API_URL = os.getenv("GENERATOR_API_URL", "https://prove-me-wrong-production.up.railway.app")
RESOLUTIONS_API_URL = os.getenv("RESOLUTIONS_API_URL", "https://prove-me-wrong-production.up.railway.app")

# Blockchain Configuration
RPC_URL = os.getenv("RPC_URL", None)
PMW_ADDRESS = os.getenv("PMW_ADDRESS", None)
FDC_HUB_ADDRESS = os.getenv("FDC_HUB_ADDRESS", None)
FDC_FEE_CONFIG_ADDRESS = os.getenv("FDC_FEE_CONFIG_ADDRESS", None)
ADMIN_PRIVATE_KEY = os.getenv("ADMIN_PRIVATE_KEY", None)
CHAIN_ID = int(os.getenv("CHAIN_ID", 0))

# Database storage for resolutions (replaces file storage)

class MarketData(BaseModel):
    id: str
    title: str
    description: str
    prompt: str
    close_time_iso: str
    outcomes: List[str]
    initial_prob: float
    validation: Dict[str, Any]
    created_at: str
    status: str

class ResolutionRequest(BaseModel):
    market_id: str
    force_resolve: bool = False

class ResolutionResult(BaseModel):
    market_id: str
    outcome: str  # YES, NO, or EXPIRED
    confidence: float
    reasoning: str
    evidence_sources: List[str]
    resolved_at: str
    auto_expired: bool = False

class ResolutionResponse(BaseModel):
    success: bool
    resolution: Optional[ResolutionResult] = None
    error: Optional[str] = None

def get_asi_headers():
    """Get headers for ASI-1 API requests"""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'bearer {ASI_API_KEY}'
    }

def get_web3_instance():
    """Get Web3 instance for blockchain interactions"""
    if not RPC_URL:
        logger.warning("RPC_URL not configured, blockchain operations will be skipped")
        return None
    
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if not w3.is_connected():
            logger.error("Failed to connect to blockchain")
            return None
        return w3
    except Exception as e:
        logger.error(f"Error connecting to blockchain: {e}")
        return None

def get_resolve_market_abi():
    """Get the ProveMeWrong contract ABI for resolveMarket function"""
    return [
        {
        "inputs": [
            {
            "internalType": "bytes32",
            "name": "marketId",
            "type": "bytes32"
            },
            {
            "components": [
                {
                "internalType": "bytes32[]",
                "name": "merkleProof",
                "type": "bytes32[]"
                },
                {
                "components": [
                    {
                    "internalType": "bytes32",
                    "name": "attestationType",
                    "type": "bytes32"
                    },
                    {
                    "internalType": "bytes32",
                    "name": "sourceId",
                    "type": "bytes32"
                    },
                    {
                    "internalType": "uint64",
                    "name": "votingRound",
                    "type": "uint64"
                    },
                    {
                    "internalType": "uint64",
                    "name": "lowestUsedTimestamp",
                    "type": "uint64"
                    },
                    {
                    "components": [
                        {
                        "internalType": "string",
                        "name": "url",
                        "type": "string"
                        },
                        {
                        "internalType": "string",
                        "name": "httpMethod",
                        "type": "string"
                        },
                        {
                        "internalType": "string",
                        "name": "headers",
                        "type": "string"
                        },
                        {
                        "internalType": "string",
                        "name": "queryParams",
                        "type": "string"
                        },
                        {
                        "internalType": "string",
                        "name": "body",
                        "type": "string"
                        },
                        {
                        "internalType": "string",
                        "name": "postProcessJq",
                        "type": "string"
                        },
                        {
                        "internalType": "string",
                        "name": "abiSignature",
                        "type": "string"
                        }
                    ],
                    "internalType": "struct IWeb2Json.RequestBody",
                    "name": "requestBody",
                    "type": "tuple"
                    },
                    {
                    "components": [
                        {
                        "internalType": "bytes",
                        "name": "abiEncodedData",
                        "type": "bytes"
                        }
                    ],
                    "internalType": "struct IWeb2Json.ResponseBody",
                    "name": "responseBody",
                    "type": "tuple"
                    }
                ],
                "internalType": "struct IWeb2Json.Response",
                "name": "data",
                "type": "tuple"
                }
            ],
            "internalType": "struct IWeb2Json.Proof",
            "name": "data",
            "type": "tuple"
            }
        ],
        "name": "resolveMarket",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
        }
    ]

def get_request_fee_abi():
    return [
        {
        "inputs": [
        {
            "internalType": "bytes",
            "name": "_data",
            "type": "bytes"
        }
        ],
        "name": "getRequestFee",
        "outputs": [
        {
            "internalType": "uint256",
            "name": "_fee",
            "type": "uint256"
        }
        ],
        "stateMutability": "view",
        "type": "function"
    },
]

def get_request_attestation_abi():
    return [
       {
        "inputs": [
        {
            "internalType": "bytes",
            "name": "_data",
            "type": "bytes"
        }
        ],
        "name": "requestAttestation",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }   
    ]

def prepare_fdc_request(
    url: str
) -> Optional[str]:
    """Prepare a request for the Flare FDC"""
    
    try:
        body = {
            "attestationType": "0x494a736f6e417069000000000000000000000000000000000000000000000000",
            "sourceId": "0x5745423200000000000000000000000000000000000000000000000000000000",
            "requestBody": {
                "url": url,
                "postprocessJq": ".",
                "abi_signature": "{\"components\": [{\"internalType\": \"uint256\",\"name\": \"outcome\",\"type\": \"uint256\"}],\"name\": \"task\",\"type\": \"tuple\"}"
            }
        }

        response = requests.post(
            "https://jq-verifier-test.flare.rocks/JsonApi/prepareRequest",
            headers={
                "X-API-KEY": "flare-oxford-2025",
                "Content-Type": "application/json"
            },
            json=body
        )
        
        if not response.ok:
            logger.error(f"FDC request failed with status: {response.status_code}")
            return None
        
        data = response.json()
        if data.get("status") != "VALID":
            logger.error(f"FDC request returned invalid status: {data.get('status')}")
            return None
        
        return data.get("abiEncodedRequest")
        
    except Exception as e:
        logger.error(f"Error preparing FDC request: {e}")
        return None

def resolve_market_onchain(market_id: str, url: str) -> bool:
    """Resolve a market on the blockchain using admin wallet"""
    
    w3 = get_web3_instance()
    if not w3:
        logger.warning("Web3 not available, skipping blockchain resolution")
        return False
    
    if ADMIN_PRIVATE_KEY is None:
        logger.warning("ADMIN_PRIVATE_KEY not configured, skipping blockchain resolution")
        return False
    
    if PMW_ADDRESS is None:
        logger.warning("PMW_ADDRESS not configured, skipping blockchain resolution")
        return False

    if FDC_FEE_CONFIG_ADDRESS is None:
        logger.warning("FDC_FEE_CONFIG_ADDRESS not configured, skipping blockchain resolution")
        return False

    if FDC_HUB_ADDRESS is None:
        logger.warning("FDC_HUB_ADDRESS not configured, skipping blockchain resolution")
        return False
    
    try:
        # Create account from private key
        account = Account.from_key(ADMIN_PRIVATE_KEY)

        # Get encoded request from FDC
        encoded_request = prepare_fdc_request(
            url
        )
        if not encoded_request:
            logger.error("Failed to prepare FDC request")
            return False

        request_fee = w3.eth.contract(
            address=Web3.to_checksum_address(FDC_FEE_CONFIG_ADDRESS), 
            abi=get_request_fee_abi()
        ).functions.getRequestFee(encoded_request).call()
        logger.info(f"Request fee: {request_fee}")

        attestation_tx = w3.eth.contract(
            address=Web3.to_checksum_address(FDC_HUB_ADDRESS),
            abi=get_request_attestation_abi()
        ).functions.requestAttestation(encoded_request).build_transaction({
            'from': account.address,
            'gas': 500000,  # Adjust gas limit as needed
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'chainId': CHAIN_ID,
            'value': request_fee
        })

        signed_attestation_txn = w3.eth.account.sign_transaction(attestation_tx, ADMIN_PRIVATE_KEY)
        attestation_tx_hash = w3.eth.send_raw_transaction(signed_attestation_txn.rawTransaction)
        attestation_receipt = w3.eth.wait_for_transaction_receipt(attestation_tx_hash)
        block_number = attestation_receipt.get('blockNumber')
        # Get block details to extract timestamp
        block = w3.eth.get_block(block_number)
        block_timestamp = block.get('timestamp')
        logger.info(f"Attestation transaction receipt: {attestation_receipt}")
        logger.info(f"Attestation block number: {block_number}, timestamp: {block_timestamp}, tx: {attestation_tx_hash.hex()}")
        
        if block_timestamp is None:
            logger.error("Block timestamp is None")
            return False

        if attestation_receipt["status"] != 1:
            logger.error(f"Attestation transaction failed: {attestation_tx_hash.hex()}")
            return False

        voting_round_id = (block_timestamp - 1658430000) / 90
        logger.info(f"Voting round ID: {voting_round_id}")

        return True
    except Exception as e:
        logger.error(f"Error resolving market on blockchain: {e}")
        return False

def ensure_resolutions_directory():
    """Ensure the resolutions directory structure exists"""
    if not os.path.exists(RESOLUTIONS_DIR):
        os.makedirs(RESOLUTIONS_DIR)
    if not os.path.exists(os.path.join(RESOLUTIONS_DIR, "active")):
        os.makedirs(os.path.join(RESOLUTIONS_DIR, "active"))
    if not os.path.exists(os.path.join(RESOLUTIONS_DIR, "archived")):
        os.makedirs(os.path.join(RESOLUTIONS_DIR, "archived"))

def load_resolutions() -> Dict[str, ResolutionResult]:
    """Load resolutions from local storage"""
    ensure_resolutions_directory()
    
    # Load active resolutions
    active_file = os.path.join(RESOLUTIONS_DIR, ACTIVE_RESOLUTIONS_FILE)
    archived_file = os.path.join(RESOLUTIONS_DIR, ARCHIVED_RESOLUTIONS_FILE)

def load_resolutions_from_db(db: Session) -> Dict[str, ResolutionResult]:
    """Load resolutions from database"""
    resolutions = {}
    try:
        db_resolutions = db.query(Resolution).all()
        for db_resolution in db_resolutions:
            resolution_data = {
                "market_id": db_resolution.market_id,
                "outcome": db_resolution.outcome,
                "confidence": db_resolution.confidence,
                "reasoning": db_resolution.reasoning,
                "evidence_sources": db_resolution.evidence_sources,
                "resolved_at": db_resolution.resolved_at,
                "auto_expired": db_resolution.auto_expired
            }
            resolutions[db_resolution.market_id] = ResolutionResult(**resolution_data)
    except Exception as e:
        logger.error(f"Error loading resolutions from database: {e}")
    
    return resolutions

def save_resolution_to_db(db: Session, resolution: ResolutionResult):
    """Save resolution to database"""
    try:
        db_resolution = Resolution(
            id=resolution.market_id,  # Use market_id as the primary key
            market_id=resolution.market_id,
            outcome=resolution.outcome,
            confidence=resolution.confidence,
            reasoning=resolution.reasoning,
            evidence_sources=resolution.evidence_sources,
            resolved_at=resolution.resolved_at,
            auto_expired=resolution.auto_expired
        )
        
        # Check if resolution exists
        existing_resolution = db.query(Resolution).filter(Resolution.market_id == resolution.market_id).first()
        if existing_resolution:
            # Update existing resolution
            existing_resolution.outcome = resolution.outcome
            existing_resolution.confidence = resolution.confidence
            existing_resolution.reasoning = resolution.reasoning
            existing_resolution.evidence_sources = resolution.evidence_sources
            existing_resolution.resolved_at = resolution.resolved_at
            existing_resolution.auto_expired = resolution.auto_expired
        else:
            # Add new resolution
            db.add(db_resolution)
        
        db.commit()
        logger.info(f"Saved resolution to database: {resolution.market_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving resolution to database: {e}")
        raise

def archive_old_resolutions_db(db: Session, days_old: int = 30):
    """Move old resolutions to archived status in database"""
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(days=days_old)
    updated = False
    
    try:
        active_resolutions = db.query(Resolution).filter(Resolution.auto_expired == False).all()
        for db_resolution in active_resolutions:
            try:
                resolved_time = datetime.fromisoformat(db_resolution.resolved_at.replace('Z', '+00:00'))
                if resolved_time <= cutoff_time:
                    db_resolution.auto_expired = True
                    updated = True
                    logger.info(f"Archived old resolution for market: {db_resolution.market_id}")
            except Exception as e:
                logger.error(f"Error checking resolution age: {e}")
        
        if updated:
            db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error archiving old resolutions: {e}")
    
    return updated

def get_markets_from_generator() -> Dict[str, MarketData]:
    """Get markets from the generator API"""
    try:
        response = requests.get(f"{GENERATOR_API_URL}/markets")
        if response.status_code == 200:
            data = response.json()
            markets = {}
            for market_data in data.get("markets", []):
                markets[market_data["id"]] = MarketData(**market_data)
            return markets
        else:
            logger.error(f"Failed to get markets from generator: {response.status_code}")
            return {}
    except Exception as e:
        logger.error(f"Error getting markets from generator: {e}")
        return {}

async def search_for_evidence(market: MarketData) -> List[Dict[str, Any]]:
    """Search for evidence about the market outcome"""
    
    # Get current date for context
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    search_prompt = f"""
    CURRENT DATE: {current_date} (July 2025)
    
    Search for the LATEST, MOST RECENT news, reports, or official announcements about: {market.prompt}
    
    CRITICAL: Focus on finding the MOST CURRENT information available RIGHT NOW. Do not rely on historical data or outdated information.
    
    Look for sources like: {', '.join(market.validation.get('reliable_sources', []))}
    
    Search strategy:
    1. Look for the most recent announcements, news, or official statements
    2. Check for any updates that happened today or very recently
    3. Focus on definitive evidence that would resolve this prediction market
    4. Prioritize sources that provide current, up-to-date information
    
    Return a JSON array of relevant sources with this structure:
    [
        {{
            "title": "Article title",
            "url": "source URL", 
            "snippet": "Brief description of the content",
            "relevance_score": 0.0-1.0,
            "date": "YYYY-MM-DD (if available)"
        }}
    ]
    
    Only include sources that provide definitive evidence about the outcome.
    Prioritize sources with the most recent information.
    """
    
    try:
        response = requests.post(
            ASI_API_URL,
            headers=get_asi_headers(),
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": search_prompt}],
                "temperature": 0.3,
                "stream": False,
                "max_tokens": 1000
            }
        )
        
        if response.status_code != 200:
            logger.error(f"ASI API error in search: {response.status_code}")
            return []
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            logger.warning("Could not parse search results as JSON")
            return []
            
    except Exception as e:
        logger.error(f"Error in evidence search: {e}")
        return []

async def scrape_content(url: str) -> str:
    """Scrape content from a URL"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text content
                    text = soup.get_text()
                    
                    # Clean up whitespace
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    return text[:2000]  # Limit content length
                else:
                    logger.warning(f"Failed to scrape {url}: {response.status}")
                    return ""
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return ""

async def analyze_outcome(market: MarketData, evidence_sources: List[Dict[str, Any]]) -> ResolutionResult:
    """Use ASI-1 Mini to analyze the outcome based on evidence"""
    
    # Get current date for context
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Scrape content from evidence sources
    scraped_content = []
    for source in evidence_sources[:3]:  # Limit to top 3 sources
        if source.get("url"):
            content = await scrape_content(source["url"])
            if content:
                scraped_content.append(f"Source: {source['title']}\nContent: {content[:500]}...")
    
    analysis_prompt = f"""
    CURRENT DATE: {current_date} (July 2025)
    
    You are a professional prediction market resolver. Analyze the following market and evidence to determine the outcome.

    MARKET: {market.title}
    PROMPT: {market.prompt}
    CLOSE DATE: {market.close_time_iso}

    EVIDENCE (MOST RECENT AVAILABLE):
    {chr(10).join(scraped_content) if scraped_content else "No evidence found"}

    RELIABLE SOURCES TO CHECK: {', '.join(market.validation.get('reliable_sources', []))}

    CRITICAL: Base your analysis on the MOST CURRENT information available. Do not rely on historical data or outdated information. If the evidence is from before the current date, it may not be relevant for resolving this market.

    Return a JSON object with the following structure:
    {{
        "outcome": "YES/NO/INSUFFICIENT_EVIDENCE",
        "confidence": 0.0-1.0,
        "reasoning": "Detailed explanation of your analysis",
        "evidence_sources": ["List of sources that provided evidence"],
        "auto_expired": false
    }}

    RESOLUTION RULES:
    1. Only resolve as YES or NO if there is definitive evidence from reliable sources
    2. If the close date has passed and no definitive evidence exists, mark as auto_expired
    3. If evidence is insufficient or conflicting, return INSUFFICIENT_EVIDENCE
    4. Be conservative - only resolve when you have high confidence
    5. For "before X date" markets, if the date has passed without the event occurring, resolve as NO
    6. **CRITICAL: Only use current, up-to-date evidence. Historical data may not be relevant.**
    7. **CRITICAL: If the evidence is outdated or doesn't reflect the current situation, return INSUFFICIENT_EVIDENCE**
    """
    
    try:
        response = requests.post(
            ASI_API_URL,
            headers=get_asi_headers(),
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": analysis_prompt}],
                "temperature": 0.2,
                "stream": False,
                "max_tokens": 1500
            }
        )
        
        if response.status_code != 200:
            logger.error(f"ASI API error in analysis: {response.status_code}")
            return ResolutionResult(
                market_id=market.id,
                outcome="INSUFFICIENT_EVIDENCE",
                confidence=0.0,
                reasoning="Failed to analyze due to API error",
                evidence_sources=[],
                resolved_at=datetime.now().isoformat(),
                auto_expired=False
            )
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
            return ResolutionResult(
                market_id=market.id,
                outcome=analysis.get("outcome", "INSUFFICIENT_EVIDENCE"),
                confidence=analysis.get("confidence", 0.0),
                reasoning=analysis.get("reasoning", "No reasoning provided"),
                evidence_sources=analysis.get("evidence_sources", []),
                resolved_at=datetime.now().isoformat(),
                auto_expired=analysis.get("auto_expired", False)
            )
        else:
            logger.warning("Could not parse analysis as JSON")
            return ResolutionResult(
                market_id=market.id,
                outcome="INSUFFICIENT_EVIDENCE",
                confidence=0.0,
                reasoning="Failed to parse analysis response",
                evidence_sources=[],
                resolved_at=datetime.now().isoformat(),
                auto_expired=False
            )
            
    except Exception as e:
        logger.error(f"Error in outcome analysis: {e}")
        return ResolutionResult(
            market_id=market.id,
            outcome="INSUFFICIENT_EVIDENCE",
            confidence=0.0,
            reasoning=f"Error during analysis: {str(e)}",
            evidence_sources=[],
            resolved_at=datetime.now().isoformat(),
            auto_expired=False
        )

def check_auto_expiration(market: MarketData) -> bool:
    """Check if a market should be auto-expired"""
    try:
        close_time = datetime.fromisoformat(market.close_time_iso.replace('Z', '+00:00'))
        now = datetime.now()
        
        # Check if close date has passed
        if close_time <= now:
            # Check if it's a "before X date" type market
            if market.validation.get("auto_expire", False):
                return True
            
            # Check if it's been more than 7 days past close date
            if (now - close_time).days > 7:
                return True
                
        return False
    except Exception as e:
        logger.error(f"Error checking auto-expiration: {e}")
        return False

@app.post("/resolve", response_model=ResolutionResponse)
async def resolve_market(request: ResolutionRequest, db: Session = Depends(get_db)):
    """Resolve a specific market"""
    
    if not ASI_API_KEY:
        raise HTTPException(status_code=500, detail="ASI API key not configured")
    
    try:
        logger.info(f"Resolving market: {request.market_id}")
        
        # Get markets from generator
        markets = get_markets_from_generator()
        
        if request.market_id not in markets:
            return ResolutionResponse(
                success=False,
                error="Market not found"
            )
        
        market = markets[request.market_id]
        
        """
        # Check if already resolved
        resolutions = load_resolutions_from_db(db)
        if request.market_id in resolutions and not request.force_resolve:
            return ResolutionResponse(
                success=True,
                resolution=resolutions[request.market_id]
            )
        
        # Check for auto-expiration
        if check_auto_expiration(market):
            resolution = ResolutionResult(
                market_id=market.id,
                outcome="NO",  # Default to NO for expired markets
                confidence=1.0,
                reasoning="Market expired without definitive outcome",
                evidence_sources=[],
                resolved_at=datetime.now().isoformat(),
                auto_expired=True
            )
        else:
            # Search for evidence
            evidence_sources = await search_for_evidence(market)
            logger.info(f"Found {len(evidence_sources)} evidence sources")
            
            # Analyze outcome
            resolution = await analyze_outcome(market, evidence_sources)
        
        # Store resolution in database
        save_resolution_to_db(db, resolution)
        """

        url = f"{RESOLUTIONS_API_URL}/resolver/resolutions/{market.id}/outcome"

        # Resolve the market onchain
        resolve_market_onchain(market.id, url)  
        
        #logger.info(f"Market resolved: {resolution.outcome} (confidence: {resolution.confidence})")
        
        return ResolutionResponse(
            success=True,
            resolution=None
        )
        
    except Exception as e:
        logger.error(f"Error resolving market: {e}")
        return ResolutionResponse(
            success=False,
            error=f"Internal error: {str(e)}"
        )

@app.post("/resolve-all")
async def resolve_all_markets(db: Session = Depends(get_db)):
    """Resolve all active markets (for cron job)"""
    
    if not ASI_API_KEY:
        raise HTTPException(status_code=500, detail="ASI API key not configured")
    
    try:
        logger.info("Starting batch resolution of all markets")
        
        # Get markets from generator
        markets = get_markets_from_generator()
        resolutions = load_resolutions_from_db(db)
        
        results = []
        
        for market_id, market in markets.items():
            # Skip if already resolved
            if market_id in resolutions:
                continue
            
            url = f"{RESOLUTIONS_API_URL}/resolver/resolutions/{market_id}/outcome"

            # Resolve the market onchain
            resolve_market_onchain(market_id, url)   

            """
            # Check for auto-expiration first
            if check_auto_expiration(market):
                resolution = ResolutionResult(
                    market_id=market.id,
                    outcome="NO",
                    confidence=1.0,
                    reasoning="Market expired without definitive outcome",
                    evidence_sources=[],
                    resolved_at=datetime.now().isoformat(),
                    auto_expired=True
                )
                save_resolution_to_db(db, resolution)
                results.append({"market_id": market_id, "outcome": "EXPIRED", "auto_expired": True})
                continue
            
            # Only resolve markets that are close to their resolution date or have high probability of resolution
            close_time = datetime.fromisoformat(market.close_time_iso.replace('Z', '+00:00'))
            days_until_close = (close_time - datetime.now()).days
            
            # Resolve if close date is within 3 days or if it's a high-profile market
            if days_until_close <= 3 or market.validation.get("confidence", 0) > 0.8:
                try:
                    evidence_sources = await search_for_evidence(market)
                    resolution = await analyze_outcome(market, evidence_sources)

                    url = f"{RESOLUTIONS_API_URL}/resolver/resolutions/{market_id}/outcome"
                    
                    if resolution.outcome in ["YES", "NO"]:
                        save_resolution_to_db(db, resolution)

                        resolutions[market_id] = resolution
                        
                        results.append({
                            "market_id": market_id, 
                            "outcome": resolution.outcome, 
                            "confidence": resolution.confidence
                        })

                        # Resolve the market onchain
                        resolve_market_onchain(market_id, url)                        
                    else:
                        results.append({
                            "market_id": market_id, 
                            "outcome": "INSUFFICIENT_EVIDENCE"
                        })
                except Exception as e:
                    logger.error(f"Error resolving market {market_id}: {e}")
                    results.append({
                        "market_id": market_id, 
                        "outcome": "ERROR", 
                        "error": str(e)
                    })
            """
        
        logger.info(f"Batch resolution complete. Processed {len(results)} markets")
        
        return {
            "success": True,
            "processed": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in batch resolution: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/archive-old")
async def archive_old_resolutions_endpoint(days_old: int = 30, db: Session = Depends(get_db)):
    """Manually trigger archiving of old resolutions"""
    try:
        updated = archive_old_resolutions_db(db, days_old)
        return {
            "success": True,
            "message": f"Archived {updated} old resolutions" if updated else "No old resolutions to archive",
            "archived_count": updated,
            "days_old": days_old
        }
    except Exception as e:
        logger.error(f"Error archiving old resolutions: {e}")
        raise HTTPException(status_code=500, detail=f"Error archiving resolutions: {str(e)}")

@app.get("/resolutions")
def list_resolutions(db: Session = Depends(get_db)):
    """List all resolved markets"""
    resolutions = load_resolutions_from_db(db)
    return {
        "total": len(resolutions),
        "resolutions": [resolution.dict() for resolution in resolutions.values()]
    }

@app.get("/resolutions/active")
async def get_active_resolutions(db: Session = Depends(get_db)):
    """Get only active resolutions (not auto-expired)"""
    try:
        db_resolutions = db.query(Resolution).filter(Resolution.auto_expired == False).all()
        resolutions = []
        for db_resolution in db_resolutions:
            resolution_data = ResolutionResult(
                market_id=db_resolution.market_id,
                outcome=db_resolution.outcome,
                confidence=db_resolution.confidence,
                reasoning=db_resolution.reasoning,
                evidence_sources=db_resolution.evidence_sources,
                resolved_at=db_resolution.resolved_at,
                auto_expired=db_resolution.auto_expired
            )
            resolutions.append(resolution_data)
        
        return {
            "total": len(resolutions),
            "resolutions": resolutions
        }
    except Exception as e:
        logger.error(f"Error getting active resolutions: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading resolutions: {str(e)}")

@app.get("/resolutions/archived")
async def get_archived_resolutions(db: Session = Depends(get_db)):
    """Get only archived resolutions (auto-expired)"""
    try:
        db_resolutions = db.query(Resolution).filter(Resolution.auto_expired == True).all()
        resolutions = []
        for db_resolution in db_resolutions:
            resolution_data = ResolutionResult(
                market_id=db_resolution.market_id,
                outcome=db_resolution.outcome,
                confidence=db_resolution.confidence,
                reasoning=db_resolution.reasoning,
                evidence_sources=db_resolution.evidence_sources,
                resolved_at=db_resolution.resolved_at,
                auto_expired=db_resolution.auto_expired
            )
            resolutions.append(resolution_data)
        
        return {
            "total": len(resolutions),
            "resolutions": resolutions
        }
    except Exception as e:
        logger.error(f"Error getting archived resolutions: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading resolutions: {str(e)}")

@app.get("/resolutions/{market_id}")
def get_resolution(market_id: str, db: Session = Depends(get_db)):
    """Get a specific resolution by market ID"""
    db_resolution = db.query(Resolution).filter(Resolution.market_id == market_id).first()
    if db_resolution:
        resolution_data = ResolutionResult(
            market_id=db_resolution.market_id,
            outcome=db_resolution.outcome,
            confidence=db_resolution.confidence,
            reasoning=db_resolution.reasoning,
            evidence_sources=db_resolution.evidence_sources,
            resolved_at=db_resolution.resolved_at,
            auto_expired=db_resolution.auto_expired
        )
        return resolution_data
    raise HTTPException(status_code=404, detail="Resolution not found")

@app.get("/resolutions/{market_id}/outcome")
def get_market_outcome(market_id: str, db: Session = Depends(get_db)):
    """Get the outcome of a market (true, false, or undefined)"""
    db_resolution = db.query(Resolution).filter(Resolution.market_id == market_id).first()
    if not db_resolution:
        raise HTTPException(status_code=404, detail="Resolution not found")
    
    # Check if market is resolved
    if db_resolution.outcome == "YES":
        return {"outcome": 1}
    elif db_resolution.outcome == "NO":
        return {"outcome": 0}
    else:
        return {"outcome": 2}  # INSUFFICIENT_EVIDENCE, EXPIRED, etc.

@app.get("/health")
def health():
    """Health check endpoint"""
    try:
        # Try to get a database session
        db = SessionLocal()
        try:
            resolution_count = db.query(Resolution).count()
            markets = get_markets_from_generator()
            return {
                "status": "healthy",
                "asi_api_configured": bool(ASI_API_KEY),
                "model": MODEL_NAME,
                "stored_resolutions": resolution_count,
                "total_markets": len(markets),
                "generator_api_url": GENERATOR_API_URL,
                "blockchain_configured": bool(RPC_URL and PMW_ADDRESS and ADMIN_PRIVATE_KEY),
                "blockchain_connected": bool(w3),
                "pmw_contract_address": PMW_ADDRESS
            }
        except Exception as e:
            logger.error(f"Health check DB error: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "asi_api_configured": bool(ASI_API_KEY),
                "model": MODEL_NAME,
                "generator_api_url": GENERATOR_API_URL
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "asi_api_configured": bool(ASI_API_KEY),
            "model": MODEL_NAME,
            "generator_api_url": GENERATOR_API_URL
        }

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "service": "Market Resolver Agent",
        "version": "1.0.0",
        "model": MODEL_NAME,
        "blockchain_integration": "enabled",
        "endpoints": {
            "POST /resolve": "Resolve a specific market",
            "POST /resolve-all": "Resolve all active markets",
            "GET /resolutions": "List all resolutions",
            "GET /resolutions/{id}": "Get specific resolution",
            "GET /health": "Health check"
        }
    }

# Background task for periodic resolution
def run_periodic_resolution():
    """Run resolution every hour"""
    while True:
        try:
            logger.info("Running periodic market resolution")
            # Create a new database session for the background task
            db = SessionLocal()
            try:
                asyncio.run(resolve_all_markets(db))
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in periodic resolution: {e}")
        
        # Wait for 1 hour
        time.sleep(3600)

# Start background task
@app.on_event("startup")
async def start_background_tasks():
    """Start background tasks on startup"""
    thread = threading.Thread(target=run_periodic_resolution, daemon=True)
    thread.start()
    logger.info("Background resolution task started")

@app.on_event("startup")
async def startup_event():
    """Initialize database and clean up old resolutions on startup"""
    try:
        init_db()
        logger.info("Database initialized successfully")
        
        logger.info("Market Resolver Agent starting up...")
        logger.info(f"Generator API URL: {GENERATOR_API_URL}")
        logger.info(f"ASI API configured: {bool(ASI_API_KEY)}")
        
        # Archive old resolutions
        db = SessionLocal()
        try:
            updated = archive_old_resolutions_db(db, 30)  # Archive resolutions older than 30 days
            if updated:
                logger.info(f"Archived {updated} old resolutions on startup")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error during startup: {e}")