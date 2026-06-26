#!/usr/bin/env python3
"""
Garena Guest Generator API with Auto Activation
For Render Deployment - Fixed Version
"""

import hmac
import hashlib
import aiohttp
import asyncio
import string
import random
import json
import time
import base64
import sys
import os
import requests
import urllib3
import warnings
from datetime import datetime
from aiohttp import web
import threading
from concurrent.futures import ThreadPoolExecutor
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")

# =============================================================================
# RENDER REQUIREMENTS - Auto install if missing
# =============================================================================
def install_requirements():
    """Auto install required packages for Render deployment"""
    required_packages = [
        'aiohttp',
        'requests',
        'pycryptodome',
        'protobuf',
        'urllib3'
    ]
    
    for package in required_packages:
        try:
            if package == 'pycryptodome':
                import Crypto
            elif package == 'protobuf':
                import google.protobuf
            elif package == 'aiohttp':
                import aiohttp
            elif package == 'requests':
                import requests
            elif package == 'urllib3':
                import urllib3
            logger.info(f"✅ {package} already installed")
        except ImportError:
            logger.info(f"📦 Installing {package}...")
            try:
                import subprocess
                subprocess.run([sys.executable, '-m', 'pip', 'install', package, '--quiet'], check=True)
                logger.info(f"✅ {package} installed successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to install {package}: {e}")

# Install requirements on startup
install_requirements()

# =============================================================================
# PROTOBUF IMPORTS WITH FALLBACK - CREATING MANUAL PROTOBUF
# =============================================================================
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    AES_AVAILABLE = True
except ImportError:
    AES_AVAILABLE = False
    def pad(data, block_size): return data
    logger.warning("⚠️ Crypto not available - using fallback")

# Create manual protobuf classes if not available
try:
    import MajoRLoGinrEq_pb2
    import MajoRLoGinrEs_pb2
    NEW_PROTO_AVAILABLE = True
    logger.info("✅ Protobuf modules loaded successfully")
except ImportError:
    NEW_PROTO_AVAILABLE = False
    logger.warning("⚠️ Protobuf modules not found - creating manual fallback")
    
    # Manual protobuf classes for fallback
    class MajorLoginEq:
        def __init__(self):
            self.event_time = ""
            self.game_name = ""
            self.platform_id = 0
            self.client_version = ""
            self.system_software = ""
            self.system_hardware = ""
            self.telecom_operator = ""
            self.network_type = ""
            self.screen_width = 0
            self.screen_height = 0
            self.screen_dpi = ""
            self.processor_details = ""
            self.memory = 0
            self.gpu_renderer = ""
            self.gpu_version = ""
            self.unique_device_id = ""
            self.client_ip = ""
            self.language = ""
            self.open_id = ""
            self.open_id_type = ""
            self.device_type = ""
            self.memory_available = type('obj', (object,), {'version': 0, 'hidden_value': 0})
            self.access_token = ""
            self.platform_sdk_id = 0
            self.network_operator_a = ""
            self.network_type_a = ""
            self.client_using_version = ""
            self.external_storage_total = 0
            self.external_storage_available = 0
            self.internal_storage_total = 0
            self.internal_storage_available = 0
            self.game_disk_storage_available = 0
            self.game_disk_storage_total = 0
            self.external_sdcard_avail_storage = 0
            self.external_sdcard_total_storage = 0
            self.login_by = 0
            self.library_path = ""
            self.reg_avatar = 0
            self.library_token = ""
            self.channel_type = 0
            self.cpu_type = 0
            self.cpu_architecture = ""
            self.client_version_code = ""
            self.graphics_api = ""
            self.supported_astc_bitset = 0
            self.login_open_id_type = 0
            self.analytics_detail = b""
            self.loading_time = 0
            self.release_channel = ""
            self.extra_info = ""
            self.android_engine_init_flag = 0
            self.if_push = 0
            self.is_vpn = 0
            self.origin_platform_type = ""
            self.primary_platform_type = ""
        
        def SerializeToString(self):
            # Build a basic binary string
            result = b""
            if self.event_time:
                result += b"\x1a" + len(self.event_time).to_bytes(1, 'little') + self.event_time.encode()
            if self.game_name:
                result += b"\x22" + len(self.game_name).to_bytes(1, 'little') + self.game_name.encode()
            if self.client_version:
                result += b"\x3a" + len(self.client_version).to_bytes(1, 'little') + self.client_version.encode()
            if self.open_id:
                result += b"\xb2\x01" + len(self.open_id).to_bytes(1, 'little') + self.open_id.encode()
            if self.access_token:
                result += b"\xea\x01" + len(self.access_token).to_bytes(1, 'little') + self.access_token.encode()
            return result
    
    class MajorLoginRes:
        def __init__(self):
            self.token = ""
            self.account_uid = ""
            self.key = b""
            self.iv = b""
            self.region = ""
            self.url = ""
        
        def ParseFromString(self, data):
            # Try to extract JWT token from response
            try:
                text = data.decode('utf-8', errors='ignore')
                import re
                jwt_match = re.search(r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', text)
                if jwt_match:
                    self.token = jwt_match.group()
                    # Try to decode account ID from JWT
                    try:
                        parts = self.token.split('.')
                        if len(parts) >= 2:
                            payload = parts[1]
                            padding = 4 - len(payload) % 4
                            if padding != 4:
                                payload += '=' * padding
                            decoded = base64.urlsafe_b64decode(payload)
                            data = json.loads(decoded)
                            self.account_uid = str(data.get('account_id') or data.get('external_id') or '')
                    except:
                        pass
            except:
                pass
    
    MajoRLoGinrEq_pb2 = type('MajoRLoGinrEq_pb2', (), {'MajorLogin': MajorLoginEq})
    MajoRLoGinrEs_pb2 = type('MajoRLoGinrEs_pb2', (), {'MajorLoginRes': MajorLoginRes})

# =============================================================================
# REGIONAL IP BLOCKS (For client header rotation)
# =============================================================================
REGION_IP_RANGES = {
    "IND": ["103.21.140.", "103.51.92.", "43.224.128.", "115.240.0.", "122.160.0."],
    "TW":  ["1.160.0.", "36.224.0.", "61.216.0.", "114.24.0.", "101.12.0."],
    "BD":  ["103.25.248.", "103.102.116.", "115.127.24.", "203.188.0."],
    "PK":  ["39.32.0.", "111.88.0.", "119.160.0.", "175.107.0."],
    "ID":  ["36.64.0.", "101.255.0.", "114.120.0.", "180.251.0."],
    "TH":  ["1.4.0.", "49.228.0.", "58.8.0.", "110.168.0."],
    "VN":  ["1.52.0.", "14.160.0.", "113.160.0.", "123.24.0."],
    "ME":  ["2.50.0.", "5.30.0.", "82.199.0.", "94.200.0."],
    "BR":  ["2.80.0.", "177.0.0.", "186.200.0.", "201.0.0."],
    "EU":  ["46.4.0.", "95.140.0.", "109.252.0.", "212.0.0."],
    "CIS": ["46.0.0.", "95.52.0.", "178.120.0.", "193.0.0."],
    "NA":  ["3.0.0.", "63.160.0.", "128.0.0.", "172.0.0."],
    "SAC": ["181.1.0.", "190.1.0.", "200.1.0.", "201.1.0."]
}

# =============================================================================
# REGION ACTIVATION CONFIGURATIONS
# =============================================================================
ACTIVATION_CONFIGS = {
    'IND': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.common.ggbluefox.com/MajorLogin',
        'get_login_data_url': 'https://client.ind.freefiremobile.com/GetLoginData',
        'client_host': 'client.ind.freefiremobile.com',
        'region_code': 'IND'
    },
    'BD': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
        'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
        'client_host': 'clientbp.ggblueshark.com',
        'region_code': 'BD'
    },
    'PK': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
        'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
        'client_host': 'clientbp.ggblueshark.com',
        'region_code': 'PK'
    },
    'ID': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
        'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
        'client_host': 'clientbp.ggblueshark.com',
        'region_code': 'ID'
    },
    'TH': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.common.ggbluefox.com/MajorLogin',
        'get_login_data_url': 'https://clientbp.common.ggbluefox.com/GetLoginData',
        'client_host': 'clientbp.common.ggbluefox.com',
        'region_code': 'TH'
    },
    'VN': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
        'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
        'client_host': 'clientbp.ggblueshark.com',
        'region_code': 'VN'
    },
    'ME': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.common.ggbluefox.com/MajorLogin',
        'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
        'client_host': 'clientbp.ggblueshark.com',
        'region_code': 'ME'
    },
    'BR': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
        'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
        'client_host': 'clientbp.ggblueshark.com',
        'region_code': 'BR'
    },
    'TW': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
        'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
        'client_host': 'clientbp.ggblueshark.com',
        'region_code': 'TW'
    },
    'EU': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
        'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
        'client_host': 'clientbp.ggblueshark.com',
        'region_code': 'EU'
    },
    'CIS': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.common.ggbluefox.com/MajorLogin',
        'get_login_data_url': 'https://client.ind.freefiremobile.com/GetLoginData',
        'client_host': 'client.ind.freefiremobile.com',
        'region_code': 'CIS'
    },
    'NA': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.ggblueshark.com/MajorLogin',
        'get_login_data_url': 'https://clientbp.ggblueshark.com/GetLoginData',
        'client_host': 'clientbp.ggblueshark.com',
        'region_code': 'NA'
    },
    'SAC': {
        'guest_url': 'https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant',
        'major_login_url': 'https://loginbp.common.ggbluefox.com/MajorLogin',
        'get_login_data_url': 'https://client.ind.freefiremobile.com/GetLoginData',
        'client_host': 'client.ind.freefiremobile.com',
        'region_code': 'SAC'
    }
}

# =============================================================================
# PROXY UTILITY
# =============================================================================
def get_rotated_proxy(region):
    """Reads proxies.json and returns a single rotated proxy URL for the region"""
    try:
        if os.path.exists("proxies.json"):
            with open("proxies.json", "r") as f:
                data = json.load(f)
                proxies_list = data.get(region.upper(), [])
                if proxies_list:
                    return random.choice(proxies_list)
    except Exception:
        pass
    return None

def generate_rotated_ip(region):
    """Generates a random, valid IP address based on the region's subnet blocks"""
    blocks = REGION_IP_RANGES.get(region.upper(), ["223.191.51."])
    base = random.choice(blocks)
    return f"{base}{random.randint(1, 254)}"

# =============================================================================
# ENCRYPTION & PROTO UTILS
# =============================================================================
def generate_exponent_number():
    exponent_digits = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
    }
    number = random.randint(1, 99999)
    return ''.join(exponent_digits[d] for d in f"{number:05d}")

def decode_jwt_token(jwt_token):
    try:
        parts = jwt_token.split('.')
        if len(parts) >= 2:
            payload_part = parts[1]
            padding = 4 - len(payload_part) % 4
            if padding != 4:
                payload_part += '=' * padding
            decoded = base64.urlsafe_b64decode(payload_part)
            data = json.loads(decoded)
            return str(data.get('account_id') or data.get('external_id') or "N/A")
    except:
        pass
    return "N/A"

async def EnC_Vr(N):
    if N < 0: return b''
    H = []
    while True:
        BesTo = N & 0x7F
        N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)

async def CrEaTe_VarianT(field_number, value):
    return await EnC_Vr((field_number << 3) | 0) + await EnC_Vr(value)

async def CrEaTe_LenGTh(field_number, value):
    h = await EnC_Vr((field_number << 3) | 2)
    e = value.encode() if isinstance(value, str) else value
    return h + await EnC_Vr(len(e)) + e

async def CrEaTe_ProTo(fields):
    p = bytearray()
    for f, v in fields.items():
        if isinstance(v, dict):
            p.extend(await CrEaTe_LenGTh(f, await CrEaTe_ProTo(v)))
        elif isinstance(v, int):
            p.extend(await CrEaTe_VarianT(f, v))
        elif isinstance(v, (str, bytes)):
            p.extend(await CrEaTe_LenGTh(f, v))
    return p

def E_AEs(Pc):
    if not AES_AVAILABLE:
        return bytes.fromhex(Pc)
    Z = bytes.fromhex(Pc)
    key = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
    iv  = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])
    K = AES.new(key, AES.MODE_CBC, iv)
    return K.encrypt(pad(Z, AES.block_size))

# =============================================================================
# SIMPLIFIED ACTIVATION - Using Direct Requests
# =============================================================================
def activate_account(uid, password, region, proxy_url=None):
    """Activate account using region-specific configuration - Simplified"""
    try:
        cfg = ACTIVATION_CONFIGS.get(region.upper())
        if not cfg:
            return False
            
        client_ip = generate_rotated_ip(region)
        
        # Step 1: Guest token
        guest_headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G960F Build/PIE)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "close",
            "X-Forwarded-For": client_ip,
            "X-Real-IP": client_ip,
        }
        
        guest_data = {
            "uid": uid,
            "password": password,
            "response_type": "token",
            "client_type": "2",
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_id": "100067"
        }
        
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        
        # Get guest token
        resp = requests.post(
            cfg['guest_url'], 
            headers=guest_headers, 
            data=guest_data, 
            verify=False, 
            timeout=10, 
            proxies=proxies
        )
        
        if resp.status_code != 200:
            return False
            
        gjson = resp.json()
        access_token = gjson.get('access_token')
        open_id = gjson.get('open_id')
        
        if not access_token or not open_id:
            return False
        
        # Step 2: Major Login (simplified - using direct request)
        major_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD)',
            'Connection': 'Keep-Alive',
            'X-Forwarded-For': client_ip,
            'X-Real-IP': client_ip,
        }
        
        # Build simple major login request
        major_data = {
            'open_id': open_id,
            'access_token': access_token,
            'client_version': '1.126.2',
            'platform_id': '1',
            'game_name': 'free fire'
        }
        
        try:
            resp = requests.post(
                cfg['major_login_url'],
                headers=major_headers,
                data=major_data,
                verify=False,
                timeout=10,
                proxies=proxies
            )
            
            if resp.status_code == 200:
                return True
        except:
            pass
        
        return False
    except Exception as e:
        logger.error(f"Activation error: {e}")
        return False

# =============================================================================
# ASYNC GUEST GENERATION ENGINE - SIMPLIFIED
# =============================================================================
async def create_acc_for_api(session, region, name_prefix, is_ghost, semaphore, auto_activate=True):
    """Simplified account generation"""
    client_ip = generate_rotated_ip(region)
    proxy_url = get_rotated_proxy(region)
    
    async with semaphore:
        for attempt in range(3):
            try:
                password = "Sulavje93" + ''.join(random.choice(string.ascii_uppercase) for _ in range(4))
                
                # STEP 1: Register
                payload_reg = json.dumps({
                    "app_id": 100067, 
                    "client_type": 2, 
                    "password": password, 
                    "source": 2
                }, separators=(',', ':'))
                
                signature_reg = hmac.new(
                    bytes.fromhex("2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"), 
                    payload_reg.encode(), 
                    hashlib.sha256
                ).hexdigest()
                
                timestamp = str(int(time.time() * 1000))
                
                headers_reg = {
                    "User-Agent": "GarenaMSDK/4.0.39(SM-A325M ;Android 13;en;HK;)",
                    "Authorization": f"Signature {signature_reg}",
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json",
                    "Connection": "Keep-Alive",
                    "Host": "100067.connect.garena.com",
                    "X-Garena-Timestamp": timestamp,
                    "X-Forwarded-For": client_ip,
                    "X-Real-IP": client_ip,
                }
                
                async with session.post(
                    "https://100067.connect.garena.com/api/v2/oauth/guest:register", 
                    data=payload_reg, 
                    headers=headers_reg, 
                    ssl=False,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        continue
                    reg_json = await resp.json()
                    if reg_json.get("code") != 0:
                        continue
                    uid = reg_json['data']['uid']
                
                # STEP 2: Token
                payload_tok = json.dumps({
                    "client_id": 100067,
                    "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
                    "client_type": 2,
                    "password": password,
                    "response_type": "token",
                    "uid": uid,
                }, separators=(',', ':'))
                
                signature_tok = hmac.new(
                    bytes.fromhex("2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"), 
                    payload_tok.encode(), 
                    hashlib.sha256
                ).hexdigest()
                
                headers_tok = {
                    "User-Agent": "GarenaMSDK/4.0.39(SM-A325M ;Android 13;en;HK;)",
                    "Authorization": f"Signature {signature_tok}",
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json",
                    "Connection": "Keep-Alive",
                    "Host": "100067.connect.garena.com",
                    "X-Garena-Timestamp": timestamp,
                    "X-Forwarded-For": client_ip,
                    "X-Real-IP": client_ip,
                }
                
                async with session.post(
                    "https://100067.connect.garena.com/api/v2/oauth/guest/token:grant", 
                    data=payload_tok, 
                    headers=headers_tok, 
                    ssl=False,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        continue
                    tok_json = await resp.json()
                    if tok_json.get("code") != 0:
                        continue
                    access_token = tok_json['data']['access_token']
                    open_id = tok_json['data']['open_id']
                
                # STEP 3: Get Account ID from JWT
                account_data = {
                    "uid": uid,
                    "password": password,
                    "name": f"{name_prefix}{generate_exponent_number()}",
                    "region": "GHOST" if is_ghost else region,
                    "account_id": "N/A",
                    "jwt_token": "",
                    "client_ip": client_ip,
                    "proxy_used": proxy_url if proxy_url else "Direct"
                }
                
                # Try to get JWT token for activation
                try:
                    jwt_headers = {
                        "Accept-Encoding": "gzip",
                        "Authorization": "Bearer",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "ReleaseVersion": "OB54",
                        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
                        "X-Forwarded-For": client_ip,
                        "X-Real-IP": client_ip,
                    }
                    
                    async with session.post(
                        "https://loginbp.ggblueshark.com/MajorLogin",
                        data=f"open_id={open_id}&access_token={access_token}",
                        headers=jwt_headers,
                        ssl=False,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as resp:
                        if resp.status == 200:
                            content = await resp.read()
                            text = content.decode('utf-8', errors='ignore')
                            jwt_start = text.find("eyJ")
                            if jwt_start != -1:
                                jwt_token = text[jwt_start:]
                                second_dot = jwt_token.find(".", jwt_token.find(".") + 1)
                                if second_dot != -1:
                                    jwt_token = jwt_token[:second_dot + 44]
                                    account_data['jwt_token'] = jwt_token
                                    account_data['account_id'] = decode_jwt_token(jwt_token)
                except:
                    pass
                
                # Auto Activate if enabled
                if auto_activate and not is_ghost and account_data['account_id'] != "N/A":
                    activated = await asyncio.get_event_loop().run_in_executor(
                        None, activate_account, uid, password, region, proxy_url
                    )
                    account_data['activated'] = activated
                else:
                    account_data['activated'] = False
                
                return account_data
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                continue
        
        return None

# =============================================================================
# API HANDLER ENDPOINT
# =============================================================================
async def handle_generate(request):
    """
    API Endpoint: /g?name={}&region={}&count={}&activate={true/false}
    """
    name_prefix = request.query.get('name', 'Sulav')
    region = request.query.get('region', 'IND').upper()
    auto_activate = request.query.get('activate', 'true').lower() == 'true'
    
    try:
        count = int(request.query.get('count', '1'))
    except ValueError:
        count = 1
        
    count = max(1, min(count, 50))
    is_ghost = (region == "GHOST")
    actual_region = "BR" if is_ghost else region
    
    if actual_region not in ACTIVATION_CONFIGS:
        return web.json_response({
            "status": "error",
            "message": f"Region '{actual_region}' not supported. Supported: {list(ACTIVATION_CONFIGS.keys())}"
        }, status=400)
    
    results = []
    semaphore = asyncio.Semaphore(10)
    
    connector = aiohttp.TCPConnector(limit=0, force_close=False, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for _ in range(count):
            tasks.append(create_acc_for_api(
                session, actual_region, name_prefix, is_ghost, semaphore, auto_activate
            ))
        
        completed = await asyncio.gather(*tasks)
        
        for account_data in completed:
            if account_data:
                results.append(account_data)
    
    response_data = {
        "status": "success" if results else "failed",
        "requested_count": count,
        "generated_count": len(results),
        "auto_activation": auto_activate,
        "region": actual_region,
        "accounts": results
    }
    
    return web.json_response(response_data)

async def handle_index(request):
    return web.json_response({
        "status": "online",
        "service": "Garena Guest Generator API",
        "version": "3.0",
        "supported_regions": list(ACTIVATION_CONFIGS.keys()),
        "endpoints": {
            "/": "Info page",
            "/g": "Generate: /g?name={name}&region={region}&count={count}&activate={true/false}"
        },
        "example": "/g?name=Vaibhav&region=IND&count=3&activate=true"
    })

# =============================================================================
# RENDER.COM SPECIFIC CONFIGURATION
# =============================================================================
def get_port():
    return int(os.environ.get('PORT', 8080))

# =============================================================================
# RUNNER
# =============================================================================
def main():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/g', handle_generate)
    
    port = get_port()
    
    print("=" * 60)
    print("🚀 GARENA GUEST GENERATOR API")
    print("=" * 60)
    print(f"📡 Server: http://0.0.0.0:{port}")
    print(f"📝 Endpoint: /g?region=IND&count=3")
    print(f"📝 Supported: {list(ACTIVATION_CONFIGS.keys())}")
    print("=" * 60)
    
    web.run_app(app, host='0.0.0.0', port=port)

if __name__ == "__main__":
    main()