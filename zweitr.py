
import time
import pandas as pd
from datetime import datetime, timezone
from colorama import Fore, Style, init
import krakenex
import csv
import os
import json

# =======================
# Initialize
# =======================
init(autoreset=True)

api_key = "NBcae3Tbuc3qupKsDDUX4yiuHCx9qZriNpRy7waABK28hZ9PDULthpWe"
api_secret = "ZOOOjkYN4W9vIBBH7p/ji+qdy9SQuJyvaZ+7911ELMJTETy/ibI+SC9vanb3+1TcVI5aLM0Z1hoURhFmCdNSbg=="
kraken = krakenex.API(key=api_key, secret=api_secret)

trade_log_file = "trades_log.csv"
positions_file = "positions.json"
PAIR_CACHE_FILE = "kraken_pairs.json"

# =======================
# Strategy parameters
# =======================
symbols = ["0G/USD","1INCH/USD","2Z/USD","AB/USD","ACA/USD","ACH/USD","ACT/USD","ACX/USD","ADX/USD","AEVO/USD","AGLD/USD","AI16Z/USD","AI3/USD","AIOZ/USD","AIR/USD","AIXBT/USD","AKE/USD","AKT/USD","ALCH/USD","ALCX/USD","ALICE/USD","ALKIMI/USD","ALPHA/USD","ALTHEA/USD","ALT/USD","ANKR/USD","ANLOG/USD","ANON/USD","APENFT/USD","API3/USD","APU/USD","ARC/USD","ARKM/USD","ARPA/USD","ART/USD","AR/USD","ASRR/USD","ASTR/USD","ATH/USD","ATLAS/USD","AUCTION/USD","AUDIO/USD","AUD/USD","AURA/USD","A/USD","AVAAI/USD","B2/USD","B3/USD","BABY/USD","BADGER/USD","BAL/USD","BANANAS31/USD","BAND/USD","BDXN/USD","BEAM/USD","BERA/USD","BERT/USD","BICO/USD","BIGTIME/USD","BILLY/USD","BIO/USD","BIT/USD","BLESS/USD","BLZ/USD","BMT/USD","BNC/USD","BNT/USD","BOBA/USD","BODEN/USD","BOND/USD","BRICK/USD","BSX/USD","BTR/USD","BTT/USD","C98/USD","CAKE/USD","CAMP/USD","CARV/USD","CAT/USD","CCD/USD","CELO/USD","CELR/USD","CFG/USD","CHEEMS/USD","CHEX/USD","CHILLHOUSE/USD","CHR/USD","CLANKER/USD","CLOUD/USD","CLV/USD","CMETH/USD","COOKIE/USD","COQ/USD","CORN/USD","COTI/USD","COW/USD","CPOOL/USD","CQT/USD","CRO/USD","CSM/USD","CTC/USD","CTSI/USD","CVC/USD","CVX/USD","CXT/USD","CYBER/USD","DBR/USD","DEEP/USD","DEGEN/USD","DENT/USD","DMC/USD","DOGS/USD","DOLO/USD","DRIFT/USD","DRV/USD","DUCK/USD","DYM/USD","EDGE/USD","EGLD/USD","ELX/USD","ENJ/USD","EPT/USD","ES/USD","ESX/USD","ETHFI/USD","ETHW/USD","EUL/USD","EURC/USD","EUROP/USD","EURQ/USD","EURR/USD","EWT/USD","FARM/USD","FF/USD","FHE/USD","FIDA/USD","FIS/USD","FLUX/USD","FLY/USD","FORTH/USD","FWOG/USD","FXS/USD","GAIA/USD","GAL/USD","GARI/USD","GFI/USD","GHIBLI/USD","GHST/USD","GIGA/USD","GLMR/USD","GMT/USD","GMX/USD","GNO/USD","GOMINING/USD","GRASS/USD","GRIFFAIN/USD","GST/USD","GTC/USD","GUN/USD","G/USD","HBAR/USD","HDX/USD","HFT/USD","HIPPO/USD","HMSTR/USD","HNT/USD","HONEY/USD","HOUSE/USD","HPOS10I/USD","H/USD","ICNT/USD","ICX/USD","IDEX/USD","INIT/USD","INTR/USD","IP/USD","JAILSTOOL/USD","JITOSOL/USD","JOE/USD","JST/USD","JTO/USD","JUNO/USD","KAR/USD","KERNEL/USD","KET/USD","KEY/USD","KGEN/USD","KINT/USD","KIN/USD","KMNO/USD","KOBAN/USD","KP3R/USD","KTA/USD","L3/USD","LAYER/USD","LCAP/USD","LCX/USD","LINEA/USD","LIT/USD","LMWR/USD","LOBO/USD","LOCKIN/USD","LOFI/USD","LPT/USD","LQTY/USD","LSETH/USD","LSK/USD","LSSOL/USD","LUNA2/USD","LUNA/USD","MASK/USD","MAT/USD","MC/USD","MEME/USD","MERL/USD","METH/USD","METIS/USD","ME/USD","MF/USD","MICHI/USD","MIM/USD","MIRA/USD","MIRROR/USD","MIR/USD","MNGO/USD","MNT/USD","MOCA/USD","MOON/USD","MOVE/USD","MOVR/USD","MSOL/USD","MUBARAK/USD","MULTI/USD","M/USD","MV/USD","MXC/USD","MXNB/USD","MYX/USD","NEIRO/USD","NIL/USD","NMR/USD","NOBODY/USD","NODE/USD","NODL/USD","NOS/USD","NOT/USD","NPC/USD","NTRN/USD","NYM/USD","OCEAN/USD","ODOS/USD","OGN/USD","OMNI/USD","OPEN/USD","ORCA/USD","ORDER/USD","OSMO/USD","OXT/USD","OXY/USD","PARTI/USD","PDA/USD","PEAQ/USD","PENDLE/USD","PERP/USD","PHA/USD","PIPE/USD","PLAY/USD","PLUME/USD","PNUT/USD","POLIS/USD","POLS/USD","POND/USD","PONKE/USD","PORTAL/USD","POWR/USD","PRCL/USD","PRIME/USD","PROMPT/USD","PRO/USD","PROVE/USD","PSTAKE/USD","PTB/USD","PUFFER/USD","PUPS/USD","PYUSD/USD","QI/USD","QNT/USD","Q/USD","RAD/USD","RAIIN/USD","RARE/USD","RARI/USD","RBC/USD","RED/USD","REKT/USD","REN/USD","REPV2/USD","REQ/USD","RETARDIO/USD","REZ/USD","RIZE/USD","RLC/USD","RLUSD/USD","ROOK/USD","RPL/USD","RSR/USD","RUJI/USD","SAFE/USD","SAHARA/USD","SAMO/USD","SAPIEN/USD","SAROS/USD","SBR/USD","SCRT/USD","SDN/USD","SGB/USD","SIDEKICK/USD","SIGMA/USD","SKY/USD","SLAY/USD","SNEK/USD","SOGNI/USD","SONIC/USD","SOON/USD","SOSO/USD","SPELL/USD","SPICE/USD","SPK/USD","SRM/USD","SSV/USD","STEP/USD","STG/USD","STORJ/USD","STRD/USD","SUKU/USD","SUNDOG/USD","SUN/USD","SUPER/USD","S/USD","SWARMS/USD","SWEAT/USD","SWELL/USD","SXT/USD","SYN/USD","TAC/USD","TANSSI/USD","TBTC/USD","TEER/USD","TERM/USD","TITCOIN/USD","TLM/USD","TNSR/USD","TOKEN/USD","TOKE/USD","TOSHI/USD","TRAC/USD","TREE/USD","TREMP/USD","TRU/USD","T/USD","TUSD/USD","TVK/USD","UFD/USD","UMA/USD","UNFI/USD","UNITE/USD","USD1/USD","USDD/USD","USDE/USD","USDG/USD","USDQ/USD","USDR/USD","USDS/USD","USDUC/USD","USELESS/USD","UST/USD","USUAL/USD","U/USD","VANRY/USD","VELODROME/USD","VERSE/USD","VINE/USD","VSN/USD","VVV/USD","WAL/USD","WAXL/USD","WBTC/USD","WCT/USD","WELL/USD","WEN/USD","WIN/USD","WMTX/USD","WOO/USD","XAN/USD","XAUT/USD","XDC/USD","XION/USD","XL1/USD","MLN/USD","XMN/USD","XNY/USD","REP/USD","XRT/USD","XTER/USD","XYO/USD","YGG/USD","ZEREBRO/USD","ZETA/USD","EUR/USD","ZEUS/USD","ZEX/USD","GBP/USD","ZIG/USD","ZORA/USD","AAVE/USD","ADA/USD","AERO/USD","ALGO/USD","APE/USD","APT/USD","ARB/USD","ATOM/USD","AVAX/USD","AVNT/USD","AXS/USD","BAT/USD","BCH/USD","BLUR/USD","BNB/USD","BONK/USD","CHZ/USD","COMP/USD","CRV/USD","DAI/USD","DASH/USD","DOG/USD","DOT/USD","DYDX/USD","EIGEN/USD","ENA/USD","ENS/USD","FARTCOIN/USD","FET/USD","FIL/USD","FLOKI/USD","FLOW/USD","FLR/USD","GALA/USD","GOAT/USD","GRT/USD","ICP/USD","IMX/USD","INJ/USD","JASMY/USD","JUP/USD","KAITO/USD","KAS/USD","KAVA/USD","KEEP/USD","KNC/USD","KSM/USD","LDO/USD","LINK/USD","LRC/USD","MANA/USD","MELANIA/USD","MEW/USD","MINA/USD","MOG/USD","MOODENG/USD","MORPHO/USD","NANO/USD","NEAR/USD","OMG/USD","OM/USD","ONDO/USD","OP/USD","PAXG/USD","PENGU/USD","PEPE/USD","POL/USD","POPCAT/USD","PUMP/USD","PYTH/USD","QTUM/USD","RAY/USD","RENDER/USD","RUNE/USD","SAGA/USD","SAND/USD","SC/USD","SEI/USD","SHIB/USD","SNX/USD","SOL/USD","SPX/USD","STBL/USD","STRK/USD","STX/USD","SUI/USD","SUSHI/USD","SYRUP/USD","TAO/USD","TIA/USD","TON/USD","TRUMP/USD","TRX/USD","TURBO/USD","UNI/USD","USDC/USD","USDT/USD","VIRTUAL/USD","WIF/USD","WLD/USD","WLFI/USD","W/USD","XCN/USD","XDG/USD","ETC/USD","ETH/USD","LTC/USD","XPL/USD","XTZ/USD","XBT/USD","XLM/USD","XMR/USD","XRP/USD","ZEC/USD","YFI/USD","ZK/USD","ZRO/USD","ZRX/USD"]  # shortened list for testing
bollinger_length = 180
bollinger_std = 3
position_size_pct = 0.2
stop_loss_pct = 0.40

positions = {s: [] for s in symbols}
trades = {s: [] for s in symbols}
last_scanned = {s: None for s in symbols}

# =======================
# Pair cache handling
# =======================
def load_pair_cache():
    if os.path.isfile(PAIR_CACHE_FILE):
        try:
            with open(PAIR_CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(Fore.RED + f"⚠️ Pair cache corrupted, rebuilding. ({e})")
    return {}

def save_pair_cache(cache):
    with open(PAIR_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def build_pair_cache():
    print(Fore.YELLOW + "🔍 Building Kraken pair cache (AssetPairs)...")
    resp = kraken.query_public("AssetPairs")
    if resp.get("error"):
        print(Fore.RED + f"Error fetching AssetPairs: {resp['error']}")
        return {}
    cache = {}
    for pair_name, data in resp["result"].items():
        base = data.get("base", "")
        quote = data.get("quote", "")
        base_norm = base.replace("X", "").replace("Z", "")
        quote_norm = quote.replace("X", "").replace("Z", "")
        key1 = (base_norm + quote_norm).upper()
        cache[key1] = pair_name
        if quote_norm.upper() == "USD":
            cache[base_norm.upper()] = pair_name
    save_pair_cache(cache)
    print(Fore.GREEN + f"✅ Pair cache built: {len(cache)} entries")
    return cache

PAIR_CACHE = load_pair_cache()
if not PAIR_CACHE:
    PAIR_CACHE = build_pair_cache()

def resolve_pair(symbol):
    if symbol in PAIR_CACHE:
        return PAIR_CACHE[symbol]
    variants = [symbol, symbol.replace("/", "").upper()]
    for v in variants:
        if v in PAIR_CACHE:
            return PAIR_CACHE[v]
    PAIR_CACHE.update(build_pair_cache())
    return PAIR_CACHE.get(symbol)

# =======================
# Kraken helpers
# =======================
def kraken_private_request(method, data=None):
    return kraken.query_private(method, data or {})

def get_current_price(symbol):
    pair = resolve_pair(symbol)
    if not pair:
        print(Fore.RED + f"❌ Unknown Kraken pair for {symbol}")
        return None
    resp = kraken.query_public("Ticker", {"pair": pair})
    if resp.get("error"):
        print(Fore.RED + f"Price error {symbol}: {resp['error']}")
        return None
    result_key = list(resp["result"].keys())[0]
    return float(resp["result"][result_key]["c"][0])

# =======================
# Order functions with leverage patch
# =======================
def place_market_order(symbol, side, volume, desired_order_type="margin"):
    if volume <= 0:
        print(Fore.RED + f"Invalid volume for {symbol}")
        return None
    pair = resolve_pair(symbol)
    if not pair:
        print(Fore.RED + f"Cannot resolve pair for {symbol}")
        return None

    data = {
        "pair": pair,
        "type": side,
        "ordertype": "market",
        "volume": f"{volume:.8f}"
    }

    if desired_order_type == "margin":
        data_margin = data.copy()
        data_margin["leverage"] = "2:1"
        resp = kraken_private_request("AddOrder", data_margin)
        if resp.get("error"):
            print(Fore.YELLOW + f"⚠️ Margin order error for {symbol}: {resp['error']} — trying spot fallback.")
            resp_spot = kraken_private_request("AddOrder", data)
            if resp_spot.get("error"):
                print(Fore.RED + f"❌ Spot fallback also failed: {resp_spot['error']}")
                return None
            txid = resp_spot['result']['txid'][0]
            price = get_current_price(symbol)
            print(Fore.GREEN + f"✅ Spot order placed after margin fallback {symbol} | TXID {txid}")
            return volume, price, "spot"
        txid = resp['result']['txid'][0]
        price = get_current_price(symbol)
        print(Fore.GREEN + f"✅ Margin order placed {symbol} | TXID {txid}")
        return volume, price, "margin"

    resp_spot = kraken_private_request("AddOrder", data)
    if resp_spot.get("error"):
        print(Fore.RED + f"❌ Spot order error {symbol}: {resp_spot['error']}")
        return None
    txid = resp_spot['result']['txid'][0]
    price = get_current_price(symbol)
    print(Fore.GREEN + f"✅ Spot order placed {symbol} | TXID {txid}")
    return volume, price, "spot"

def place_stop_loss(symbol, entry_price, side, volume, stop_loss_pct=0.4):
    stop_price = entry_price * (1 - stop_loss_pct) if side == "buy" else entry_price * (1 + stop_loss_pct)
    pair = resolve_pair(symbol)
    if not pair:
        print(Fore.RED + f"Stop-loss failed, unknown pair {symbol}")
        return None
    data = {
        "pair": pair,
        "type": "sell" if side == "buy" else "buy",
        "ordertype": "stop-loss",
        "price": f"{stop_price:.4f}",
        "volume": f"{volume:.8f}",
        "leverage": "2:1"
    }
    resp = kraken_private_request("AddOrder", data)
    if resp.get("error"):
        print(Fore.YELLOW + f"⚠️ Stop-loss leverage error for {symbol}: {resp['error']} — fallback spot")
        data.pop("leverage", None)
        resp = kraken_private_request("AddOrder", data)
        if resp.get("error"):
            print(Fore.RED + f"Stop-loss failed {symbol}: {resp['error']}")
            return None
    txid = resp['result']['txid'][0]
    print(Fore.RED + f"🛑 Stop-loss set at {stop_price:.4f} | TXID {txid}")
    return txid


# =======================
# Portfolio printout
# =======================
def get_account_balance():
    resp = kraken_private_request("Balance")
    if resp.get("error"):
        print(Fore.RED + f"❌ Balance error: {resp['error']}")
        return {}
    return resp["result"]

def print_portfolio_status():
    balances = get_account_balance()
    if not balances:
        return
    total_usd = float(balances.get("ZUSD", 0))
    exposure = 0
    margin_used = 0
    leverage_ratio = 0

    # Calculate exposure from open positions (simplified)
    for sym, pos_list in positions.items():
        for p in pos_list:
            exposure += p.get("exposure", 0)
            if p.get("type") == "margin":
                margin_used += p.get("margin", 0)

    if margin_used > 0:
        leverage_ratio = round(exposure / margin_used, 2)

    print(Style.BRIGHT + Fore.CYAN + "
📊 Portfolio Status")
    print(Fore.WHITE + f"💰 USD Balance: {total_usd:,.2f}")
    print(Fore.YELLOW + f"📈 Exposure: {exposure:,.2f} USD")
    print(Fore.MAGENTA + f"🪙 Margin Used: {margin_used:,.2f} USD")
    print(Fore.GREEN + f"⚔️ Leverage Ratio: {leverage_ratio if leverage_ratio else 1}x")

    # Per-symbol breakdown
    for sym, pos_list in positions.items():
        for p in pos_list:
            print(Fore.WHITE + f"  {sym} | {p.get('side')} | Exposure: {p.get('exposure',0):.2f} | Margin: {p.get('margin',0):.2f} | Lvg: {p.get('leverage',1)}x")

# Example of storing position data when creating orders
def open_position(symbol, side, volume, leverage_type):
    price = get_current_price(symbol)
    if not price:
        return
    exposure = volume * price
    margin = exposure / 2 if leverage_type == "margin" else exposure
    pos = {
        "side": side,
        "volume": volume,
        "entry_price": price,
        "exposure": exposure,
        "margin": margin,
        "leverage": 2 if leverage_type == "margin" else 1,
        "type": leverage_type,
        "timestamp": time.time()
    }
    positions[symbol].append(pos)
    print(Fore.CYAN + f"📌 Position opened: {symbol} {side} {volume} @ {price:.2f} | Exposure: {exposure:.2f} | Margin: {margin:.2f} | Lvg: {pos['leverage']}x")

