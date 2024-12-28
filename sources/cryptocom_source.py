import asyncio
import json
import hmac
import hashlib
import time
import websockets
from decimal import Decimal
from typing import List, Dict, Optional
from models.position import Position
from interfaces.data_source import DataSource
from config.settings import Settings

class CryptoComSource(DataSource):
    def __init__(self, settings: Settings):
        self.api_key = settings.cryptocom_api_key
        self.api_secret = settings.cryptocom_api_secret
        self.user_ws_url = "wss://stream.crypto.com/exchange/v1/user"
        self.authenticated = False
        self.max_retries = 3
        self.retry_delay = 2

    def fetch_positions(self) -> List[Position]:
        return asyncio.run(self._async_fetch_positions())

    async def _async_fetch_positions(self) -> List[Position]:
        client = WebSocketClient(self.api_key, self.api_secret, self.user_ws_url)
        try:
            account_data = await client.fetch_account_summary()
            return self._process_account_data(account_data)
        finally:
            await client.close()

    def _process_account_data(self, account_data: Dict) -> List[Position]:
        positions = []
        
        try:
            if 'result' in account_data and 'accounts' in account_data['result']:
                for account in account_data['result']['accounts']:
                    balance = Decimal(str(account.get('balance', 0)))
                    available = Decimal(str(account.get('available', 0)))
                    order = Decimal(str(account.get('order', 0)))
                    stake = Decimal(str(account.get('stake', 0)))
                    
                    total = balance + available + order + stake
                    
                    if total > Decimal('0'):
                        positions.append(Position(
                            name=account.get('currency', ''),
                            worth=total,
                            platform="Crypto.com"
                        ))
        except Exception as e:
            print(f"Error processing Crypto.com account data: {e}")
        
        return positions

class WebSocketClient:
    def __init__(self, api_key: str, api_secret: str, ws_url: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws_url = ws_url
        self.ws = None
        self.authenticated = False

    def _generate_signature(self, request_data: Dict) -> str:
        method = request_data["method"]
        id = request_data["id"]
        nonce = request_data["nonce"]
        
        param_str = ""
        if "params" in request_data:
            params = request_data["params"]
            for key in sorted(params.keys()):
                param_str += key + str(params[key])
        
        sig_str = f"{method}{id}{self.api_key}{param_str}{nonce}"
        
        return hmac.new(
            bytes(self.api_secret, 'utf-8'),
            msg=bytes(sig_str, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

    async def authenticate(self) -> bool:
        for attempt in range(3):
            try:
                if not self.ws:
                    self.ws = await websockets.connect(
                        self.ws_url,
                        ping_interval=20,
                        ping_timeout=10
                    )
                
                auth_request = {
                    "id": int(time.time() * 1000),
                    "method": "public/auth",
                    "api_key": self.api_key,
                    "nonce": int(time.time() * 1000)
                }
                
                auth_request["sig"] = self._generate_signature(auth_request)
                await self.ws.send(json.dumps(auth_request))
                
                try:
                    response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    
                    if response_data.get("code") == 0:
                        self.authenticated = True
                        return True
                except asyncio.TimeoutError:
                    continue
                
                if attempt < 2:
                    await asyncio.sleep(2)
            
            except Exception as e:
                print(f"Authentication error: {e}")
                if attempt < 2:
                    await asyncio.sleep(2)
        
        return False

    async def fetch_account_summary(self) -> Dict:
        if not self.authenticated:
            if not await self.authenticate():
                raise Exception("Failed to authenticate with Crypto.com WebSocket API")
        
        request = {
            "id": int(time.time() * 1000),
            "method": "user.getBalance",
            "params": {},
            "nonce": int(time.time() * 1000)
        }
        
        await self.ws.send(json.dumps(request))
        
        try:
            response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
            return json.loads(response)
        except asyncio.TimeoutError:
            raise Exception("Timeout waiting for account summary response")

    async def close(self):
        if self.ws:
            await self.ws.close()
            self.ws = None
            self.authenticated = False