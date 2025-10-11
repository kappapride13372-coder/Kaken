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

# <-- use your actual keys here (you provided them earlier) -->
api_key = "NBcae3Tbuc3qupKsDDUX4yiuHCx9qZriNpRy7waABK28hZ9PDULthpWe"
api_secret = "ZOOOjkYN4W9vIBBH7p/ji+qdy9SQuJyvaZ+7911ELMJTETy/ibI+SC9vanb3+1TcVI5aLM0Z1hoURhFmCdNSbg=="
kraken = krakenex.API(key=api_key, secret=api_secret)

trade_log_file = "trades_log.csv"
positions_file = "positions.json"
PAIR_CACHE_FILE = "kraken_pairs.json"

# =======================
# Strategy parameters
# =======================
symbols = [
"CELOUSD","HPOS10IUSD","APUUSD","PROMPTUSD","STBLUSD","MCUSD","KMNOUSD","RIZEUSD","SPXUSD","OPENUSD",
"UNITEUSD","SDNUSD","CXTUSD","TRACUSD","SCRTUSD","VERSEUSD","HUSD","XPLUSD","FARTCOINUSD","MXCUSD",
"STEPUSD","CLANKERUSD","JAILSTOOLUSD","PYTHUSD","RETARDIOUSD","NODLUSD","ASTRUSD","ORDERUSD","CAMPUSD","KEYUSD",
"ACAUSD","USDUCUSD","MNTUSD","EPTUSD","PENGUUSD","DRIFTUSD","QUSD","BDXNUSD","MERLUSD","CHEEMSUSD",
"BMTUSD","BITUSD","KERNELUSD","NOSUSD","DBRUSD","LOFIUSD","LOCKINUSD","TITCOINUSD","SGBUSD","APTUSD",
"TREMPUSD","ALICEUSD","REZUSD","MOVEUSD","SOGNIUSD","GOMININGUSD","COWUSD","HONEYUSD","XTZUSD","FISUSD",
"KINTUSD","ARUSD","B3USD","SUNDOGUSD","INITUSD","STRDUSD","FWOGUSD","WUSD","XNYUSD","CQTUSD",
"PORTALUSD","MICHIUSD","DEGENUSD","FHEUSD","UFDUSD","ATHUSD","KTAUSD","TACUSD","OMGUSD","WINUSD",
"MVUSD","SWARMSUSD","FFUSD","TREEUSD","SLAYUSD","BERTUSD","MINAUSD","PROUSD","WMTXUSD","BLZUSD",
"PUPSUSD","WIFUSD","CFGUSD","CHEXUSD","MIRRORUSD","ZEUSUSD","WELLUSD","AI16ZUSD","BODENUSD","STRKUSD",
"VVVUSD","EULUSD","MOONUSD","TUSDUSD","ICPUSD","ZETAUSD","MASKUSD","TOKEUSD","UNFIUSD","CTCUSD",
"NEARUSD","OGNUSD","AURAUSD","REQUSD","LOBOUSD","XANUSD","NPCUSD","CLOUDUSD","AAVEUSD","SNEKUSD",
"DOGEUSD","SAMOUSD","ALGOUSD","JOEUSD","BCHUSD","OXYUSD","XCNUSD","GUSD","SKYUSD","MORPHOUSD",
"ATOMUSD","DRVUSD","XLMUSD","UNIUSD","SHIBUSD","SSVUSD","USDDUSD","OMUSD","WBTCUSD","BSXUSD",
"BNBUSD","AIOZUSD","AEROUSD","ANKRUSD","LCAPUSD","BTCUSD","CHRUSD","TRUMPUSD","TBTCUSD","SEIUSD",
"BTTUSD","XYOUSD","INJUSD","HOUSEUSD","RARIUSD","ALTUSD","PARTIUSD","TIAUSD","XRPUSD","PEPEUSD",
"SRMUSD","KARUSD","EGLDUSD","HIPPOUSD","GIGAUSD","LSSOLUSD","ETHUSD","FILUSD","POLUSD","QIUSD",
"PDAUSD","SOLUSD","TEERUSD","BADGERUSD","CLVUSD","TRXUSD","ANLOGUSD","ADXUSD","SAPIENUSD","QTUMUSD",
"KSMUSD","GNOUSD","COMPUSD","LSETHUSD","NOTUSD","SUSHIUSD","AGLDUSD","ZEREBROUSD","ENAUSD","BNTUSD",
"BIGTIMEUSD","SUSD","SYRUPUSD","PTBUSD","APENFTUSD","SUNUSD","SOSOUSD","MATUSD","GAIAUSD","AUSD",
"FIDAUSD","ZRXUSD","ARBUSD","LINKUSD","XAUTUSD","CMETHUSD","POPCATUSD","ACXUSD","GBPUSD","CCDUSD",
"DASHUSD","EURQUSD","XL1USD","PYUSDUSD","ETCUSD","MULTIUSD","USDRUSD","EURCUSD","USDQUSD","USDGUSD",
"USDCUSD","STXUSD","RLUSDUSD","USD1USD","USDTUSD","USDEUSD","MSOLUSD","XIONUSD","FETUSD","DAIUSD",
"ESUSD","EURUSD","PAXGUSD","RUNEUSD","CROUSD","SXTUSD","ARKMUSD","UUSD","METHUSD","FLOWUSD",
"SCUSD","NEIROUSD","EUROPUSD","IDEXUSD","ABUSD","SWEATUSD","RENDERUSD","AUDUSD","CPOOLUSD","ICXUSD",
"RAYUSD","KETUSD","OSMOUSD","LTCUSD","MOODENGUSD","DUCKUSD","HBARUSD","MANAUSD","STORJUSD","SUIUSD",
"BALUSD","USDSUSD","ONDOUSD","MOCAUSD","HMSTRUSD","BONDUSD","ADAUSD","AIRUSD","ALCXUSD","BTRUSD",
"GOATUSD","EURRUSD","AXSUSD","PLUMEUSD","GALAUSD","GHIBLIUSD","RAREUSD","MELANIAUSD","NYMUSD","DOGSUSD",
"FORTHUSD","PONDUSD","PNUTUSD","KNCUSD","TONUSD","OXTUSD","SAFEUSD","RADUSD","CVCUSD","ENJUSD",
"ASRRUSD","GRIFFAINUSD","YFIUSD","MIMUSD","JUPUSD","OPUSD","TAOUSD","POLSUSD","POLISUSD","OCEANUSD",
"EWTUSD","DMCUSD","TOSHIUSD","ACHUSD","ODOSUSD","SIGMAUSD","NANOUSD","FLUXUSD","BOBAUSD","ELXUSD",
"TLMUSD","BANANAS31USD","ZKUSD","AVAXUSD","SONICUSD","GRTUSD","VSNUSD","SYNUSD","MEMEUSD","ALPHAUSD",
"PHAUSD","ENSUSD","MLNUSD","TOKENUSD","TANSSIUSD","VELODROMEUSD","MIRUSD","MEWUSD","WCTUSD","FLRUSD",
"JTOUSD","SPELLUSD","MUBARAKUSD","ORCAUSD","WALUSD","BATUSD","BLURUSD","JITOSOLUSD","PLAYUSD","LMWRUSD",
"IMXUSD","GFIUSD","VIRTUALUSD","TURBOUSD","APEUSD","ESXUSD","WLFIUSD","RAIINUSD","LPTUSD","WENUSD",
"LCXUSD","AVAAIUSD","0GUSD","BONKUSD","MOVRUSD","POWRUSD","UMAUSD","SANDUSD","AKTUSD","DOGUSD",
"DYMUSD","DEEPUSD","DOTUSD","ARPAUSD","CHZUSD","XDCUSD","BERAUSD","DENTUSD","ACTUSD","2ZUSD",
"GTCUSD","RENUSD","ATLASUSD","ANONUSD","CELRUSD","GMTUSD","BEAMUSD","AUDIOUSD","IPUSD","HNTUSD",
"JASMYUSD","PERPUSD","CTSIUSD","AUCTIONUSD","BANDUSD","QNTUSD","LITUSD","DYDXUSD","RBCUSD","SBRUSD",
"PRCLUSD","GLMRUSD","FLYUSD","BICOUSD","TUSD","XMRUSD","MEUSD","WLDUSD","CRVUSD","TNSRUSD",
"USUALUSD","SAGAUSD","LSKUSD","RPLUSD","REDUSD","ZROUSD","PUMPUSD","PUFFERUSD","ETHFIUSD","BRICKUSD",
"RLCUSD","PONKEUSD","PENDLEUSD","NILUSD","SWELLUSD","KINUSD","AIXBTUSD","TRUUSD","LQTYUSD","YGGUSD",
"CARVUSD","KAITOUSD","GHSTUSD","1INCHUSD","VANRYUSD","STGUSD","BIOUSD","FARMUSD","SPKUSD","LUNA2USD",
"CVXUSD","KP3RUSD","AEVOUSD","NMRUSD","PROVEUSD","SAHARAUSD","WAXLUSD","SPICEUSD","MIRAUSD","COQUSD",
"EIGENUSD","SAROSUSD","FLOKIUSD","PEAQUSD","REPV2USD","ETHWUSD","JSTUSD","COTIUSD","LRCUSD","KAVAUSD",
"REKTUSD","METISUSD","RSRUSD","GUNUSD","XTERUSD","CYBERUSD","KEEPUSD","REPUSD","API3USD","CATUSD",
"WOOUSD","USTUSD","LDOUSD","BNCUSD","KASUSD","GARIUSD","LAYERUSD","COOKIEUSD","MNGOUSD","BABYUSD",
"L3USD","HFTUSD","PRIMEUSD","SUPERUSD","ZEXUSD","GMXUSD","HDXUSD","MUSD","NODEUSD","ZIGUSD",
"AVNTUSD","FXSUSD","EDGEUSD","TVKUSD","NTRNUSD","VINEUSD","SNXUSD","ALKIMIUSD","ALCHUSD","OMNIUSD",
"RUJIUSD","GRASSUSD","DOLOUSD","MOGUSD","LINEAUSD","SOONUSD","NOBODYUSD","CHILLHOUSEUSD","ZECUSD","C98USD",
"USELESSUSD","AI3USD","ZORAUSD","ROOKUSD","KOBANUSD","ICNTUSD","TERMUSD","CAKEUSD","GALUSD","PSTAKEUSD",
"CSMUSD","GSTUSD","ARTUSD","XRTUSD","BLESSUSD","CORNUSD","INTRUSD","AKEUSD","ARCUSD","JUNOUSD"
]
bollinger_length = 180
bollinger_std = 3
position_size_pct = 0.2  # fraction of total portfolio value to target per position (USD exposure)
stop_loss_pct = 0.40

# Positions structure:
# positions[symbol] = [
#     {entry, volume, entry_time, stop_txid, order_type, take_profit_enabled, strategy_type, tp_points}
# ]
positions = {s: [] for s in symbols}
trades = {s: [] for s in symbols}
last_scanned = {s: None for s in symbols}

# =======================
# Kraken pair utilities (caching)
# =======================
def load_pair_cache():
    if os.path.isfile(PAIR_CACHE_FILE):
        with open(PAIR_CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_pair_cache(cache):
    with open(PAIR_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def build_pair_cache():
    """Fetch all Kraken trading pairs once and store them locally."""
    print(Fore.YELLOW + "🔍 Building Kraken pair cache (AssetPairs)...")
    resp = kraken.query_public("AssetPairs")
    if resp.get("error"):
        print(Fore.RED + f"Error fetching AssetPairs: {resp['error']}")
        return {}
    cache = {}
    for pair_name, data in resp["result"].items():
        # data["base"], data["quote"] are like 'XXBT', 'ZUSD' etc.
        base = data.get("base", "")
        quote = data.get("quote", "")
        # normalized forms
        base_norm = base.replace("X", "").replace("Z", "")
        quote_norm = quote.replace("X", "").replace("Z", "")
        # create keys we might be asked for (e.g. CELOUSD, CELO/USD, pair_name)
        key1 = (base_norm + quote_norm).upper()        # e.g. CELOUSD
        key2 = f"{base_norm}{quote_norm}".upper()      # same
        key3 = pair_name.upper()                       # Kraken internal key
        # map common key to pair_name
        cache[key1] = pair_name
        cache[key2] = pair_name
        cache[key3] = pair_name
        # also map base-only USD keys if quote is USD
        if quote_norm.upper() == "USD":
            cache[base_norm.upper() + "USD"] = pair_name
            cache[base_norm.upper()] = pair_name
    save_pair_cache(cache)
    print(Fore.GREEN + f"✅ Pair cache built: {len(cache)} entries")
    return cache

PAIR_CACHE = load_pair_cache()
if not PAIR_CACHE:
    PAIR_CACHE = build_pair_cache()

def resolve_pair(symbol):
    """
    Return Kraken internal pair name for a given friendly symbol (e.g. 'CELOUSD').
    Tries several fallbacks and optionally rebuilds the cache once.
    """
    if symbol in PAIR_CACHE:
        return PAIR_CACHE[symbol]
    # try normalized variants
    variants = [
        symbol,
        symbol.replace("/", "").upper(),
        symbol.replace("ZUSD", "USD").upper(),
        symbol.replace("USD", "USD").upper(),
        symbol.upper()
    ]
    for v in variants:
        if v in PAIR_CACHE:
            return PAIR_CACHE[v]
    # try rebuild cache once
    PAIR_CACHE.update(build_pair_cache())
    return PAIR_CACHE.get(symbol)

# =======================
# Helper functions
# =======================
def kraken_private_request(method, data=None):
    resp = kraken.query_private(method, data or {})
    return resp

def fetch_ohlc(symbol, interval=240, since=None):
    pair = resolve_pair(symbol)
    if not pair:
        print(Fore.LIGHTRED_EX + f"❌ Unknown pair for OHLC: {symbol}")
        return None
    params = {"pair": pair, "interval": interval}
    if since:
        params["since"] = since
    resp = kraken.query_public("OHLC", params)
    if resp.get("error"):
        print(Fore.RED + f"Error fetching OHLC for {symbol} ({pair}): {resp['error']}")
        return None
    data = list(resp['result'].values())[0]
    df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
    df[['open','high','low','close','volume']] = df[['open','high','low','close','volume']].astype(float)
    df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
    return df

def calculate_bollinger(df):
    df['mean'] = df['close'].rolling(bollinger_length).mean()
    df['std'] = df['close'].rolling(bollinger_length).std()
    df['upper'] = df['mean'] + bollinger_std * df['std']
    df['lower'] = df['mean'] - bollinger_std * df['std']
    return df

def get_current_price(symbol):
    pair = resolve_pair(symbol)
    if not pair:
        print(Fore.LIGHTRED_EX + f"❌ Unknown Kraken pair for price lookup: {symbol}")
        return None
    try:
        resp = kraken.query_public("Ticker", {"pair": pair})
        if resp.get("error"):
            # show a concise message but not the long error spam
            print(Fore.RED + f"Error fetching price for {symbol} ({pair}): {resp['error']}")
            return None
        result_key = list(resp["result"].keys())[0]
        return float(resp["result"][result_key]["c"][0])
    except Exception as e:
        print(Fore.RED + f"Exception getting price for {symbol} ({pair}): {e}")
        return None

def format_pnl(value):
    return Fore.GREEN + f"{value:.2f}" + Style.RESET_ALL if value >= 0 else Fore.RED + f"{value:.2f}" + Style.RESET_ALL

def log_trade_csv(trade):
    file_exists = os.path.isfile(trade_log_file)
    with open(trade_log_file, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'type', 'symbol', 'entry', 'exit', 'profit', 'entry_time', 'exit_time', 'duration', 'order_type', 'strategy_type'
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'type': trade['type'],
            'symbol': trade['symbol'],
            'entry': f"{trade['entry']:.4f}",
            'exit': f"{trade.get('exit', ''):.4f}" if trade.get('exit') else "",
            'profit': f"{trade.get('profit', ''):.4f}" if trade.get('profit') else "",
            'entry_time': trade['entry_time'],
            'exit_time': trade.get('exit_time', ""),
            'duration': f"{trade.get('duration', ''):.2f}" if trade.get('duration') else "",
            'order_type': trade.get('order_type', ""),
            'strategy_type': trade.get('strategy_type', "")
        })

# =======================
# Portfolio & balances
# =======================
def get_total_equity_usd():
    """Sum balances (USD and other assets converted to USD using pair cache)."""
    resp = kraken_private_request("Balance")
    if resp.get("error"):
        print(Fore.RED + f"Error fetching balance: {resp['error']}")
        return 0
    balances = resp['result']
    total_equity = 0.0
    for asset, amount_str in balances.items():
        amount = float(amount_str)
        if amount <= 0:
            continue
        # Kraken uses ZUSD for USD sometimes
        if asset in ["ZUSD", "USDT", "USD"]:
            total_equity += amount
            continue
        # build a symbol like "ASSETUSD"
        normalized_asset = asset.replace("X", "").replace("Z", "")
        symbol = (normalized_asset + "USD").upper()
        price = get_current_price(symbol)
        if price:
            total_equity += amount * price
        else:
            # If price not found, skip but warn once
            # (We don't spam; resolution happens via pair cache)
            pass
    return total_equity

def get_available_margin():
    resp = kraken_private_request("TradeBalance", {"asset": "ZUSD"})
    if resp.get("error"):
        return 0
    balance = float(resp['result']['eb'])
    margin_used = float(resp['result']['mf'])
    return max(balance - margin_used, 0)

def get_spot_balance(asset="ZUSD"):
    resp = kraken_private_request("Balance")
    if resp.get("error"):
        return 0
    return max(float(resp['result'].get(asset, 0)), 0)

# =======================
# Persistent storage for positions
# =======================
def save_positions():
    with open(positions_file, "w") as f:
        serializable_positions = {}
        for sym, pos_list in positions.items():
            serializable_positions[sym] = []
            for pos in pos_list:
                pos_copy = pos.copy()
                # convert datetime to iso
                pos_copy['entry_time'] = pos_copy['entry_time'].isoformat()
                serializable_positions[sym].append(pos_copy)
        json.dump(serializable_positions, f, indent=4)

def load_positions():
    global positions
    if os.path.isfile(positions_file):
        with open(positions_file, "r") as f:
            loaded = json.load(f)
        positions = {s: [] for s in symbols}
        for sym, pos_list in loaded.items():
            for pos in pos_list:
                pos['entry_time'] = datetime.fromisoformat(pos['entry_time'])
                positions[sym].append(pos)
        print(Fore.YELLOW + f"♻️ Loaded {sum(len(p) for p in positions.values())} open positions from {positions_file}")

# =======================
# Order sizing & placement
# =======================
def calculate_order_volume(symbol, price, risk_pct):
    """
    Target exposure (USD) = total_portfolio_value * risk_pct
    Volume = target_exposure_usd / price
    """
    # total portfolio (cash + all holdings) in USD
    total_portfolio = get_total_equity_usd()
    if total_portfolio <= 0:
        print(Fore.RED + "Unable to compute portfolio value; skipping sizing.")
        return 0, None

    target_exposure = total_portfolio * risk_pct  # USD amount we want each position to represent
    volume = target_exposure / price
    # prefer margin if available; actual execution will attempt margin first and fallback
    return volume, "margin"

def place_market_order(symbol, side, volume, desired_order_type="margin"):
    """Place order using resolved Kraken pair name. Attempts desired_order_type, fallback to spot on margin errors."""
    if volume <= 0:
        print(Fore.RED + f"Invalid volume for {symbol}: {volume}")
        return None

    pair = resolve_pair(symbol)
    if not pair:
        print(Fore.RED + f"Cannot resolve pair for {symbol}; order aborted.")
        return None

    data = {"pair": pair, "type": side, "ordertype": "market", "volume": f"{volume:.8f}"}
    # Try margin first if desired
    if desired_order_type == "margin":
        data_with_margin = data.copy()
        data_with_margin["oflags"] = "margin"
        resp = kraken_private_request("AddOrder", data_with_margin)
        if resp.get("error"):
            # If margin-specific error, try spot fallback
            err = resp.get("error")
            print(Fore.YELLOW + f"⚠️ Margin order error for {symbol} ({pair}): {err} — trying spot fallback.")
            # Attempt spot
            resp_spot = kraken_private_request("AddOrder", data)
            if resp_spot.get("error"):
                print(Fore.RED + f"❌ Spot fallback also failed for {symbol}: {resp_spot['error']}")
                return None
            txid = resp_spot['result']['txid'][0]
            print(Fore.GREEN + f"✅ Spot order placed after margin fallback: {symbol} | TXID: {txid}")
            return volume, get_current_price(symbol), "spot"
        else:
            txid = resp['result']['txid'][0]
            print(Fore.GREEN + f"✅ Margin order placed: {symbol} | TXID: {txid}")
            return volume, get_current_price(symbol), "margin"
    else:
        # Spot
        resp = kraken_private_request("AddOrder", data)
        if resp.get("error"):
            print(Fore.RED + f"❌ Spot order error for {symbol}: {resp['error']}")
            return None
        txid = resp['result']['txid'][0]
        print(Fore.GREEN + f"✅ Spot order placed: {symbol} | TXID: {txid}")
        return volume, get_current_price(symbol), "spot"

def place_stop_loss(symbol, entry_price, side, volume, stop_loss_pct=0.4):
    stop_price = entry_price * (1 - stop_loss_pct) if side == "buy" else entry_price * (1 + stop_loss_pct)
    pair = resolve_pair(symbol)
    if not pair:
        print(Fore.LIGHTRED_EX + f"Cannot resolve pair for stop-loss: {symbol}")
        return None
    data = {
        "pair": pair,
        "type": "sell" if side == "buy" else "buy",
        "ordertype": "stop-loss",
        "price": f"{stop_price:.4f}",
        "volume": f"{volume:.8f}"
    }
    resp = kraken_private_request("AddOrder", data)
    if resp.get("error"):
        print(Fore.RED + f"Stop-loss order error for {symbol}: {resp['error']}")
        return None
    txid = resp['result']['txid'][0]
    print(Fore.RED + f"🛑 Stop-loss set at {stop_price:.4f} | TXID: {txid}")
    return txid

def cancel_stop_loss(txid):
    if not txid: return
    resp = kraken_private_request("CancelOrder", {"txid": txid})
    if resp.get("error"):
        print(Fore.RED + f"Failed to cancel stop-loss {txid}: {resp['error']}")
    else:
        print(Fore.YELLOW + f"🗑 Stop-loss {txid} canceled")

# =======================
# Trading logic
# =======================
def scan_for_entry(symbol, last_closed_candle):
    if last_closed_candle['close'] < last_closed_candle['lower'] and len(positions[symbol]) == 0:
        price = last_closed_candle['close']
        volume, _ = calculate_order_volume(symbol, price, position_size_pct)
        if volume <= 0:
            print(Fore.RED + f"No calculated volume for {symbol}")
            return
        result = place_market_order(symbol, "buy", volume, desired_order_type="margin")
        if result:
            vol, entry_price, order_type = result
            stop_txid = place_stop_loss(symbol, entry_price, "buy", vol, stop_loss_pct)
            trade = {
                'symbol': symbol,
                'type': 'market_buy',
                'entry': entry_price,
                'entry_time': datetime.now(timezone.utc),
                'volume': vol,
                'order_type': order_type,
                'stop_txid': stop_txid,
                'take_profit_enabled': True,
                'strategy_type': "strategy1",
                'tp_points': [entry_price * 1.02, entry_price * 1.05]  # example TPs
            }
            positions[symbol].append(trade)
            trades.setdefault(symbol, []).append(trade)
            save_positions()
            log_trade_csv(trade)
            print(Fore.GREEN + f"[{symbol}] 🚀 Market BUY executed at {entry_price:.4f} ({order_type}) with stop-loss set")

def close_position(symbol, position):
    cancel_stop_loss(position.get('stop_txid'))
    volume = position['volume']
    entry_price = position['entry']
    pair = resolve_pair(symbol)
    if not pair:
        print(Fore.RED + f"Cannot resolve pair to close position: {symbol}")
        return
    resp = kraken_private_request("AddOrder", {"pair": pair, "type": "sell", "ordertype": "market", "volume": f"{volume:.8f}"})
    if resp.get("error"):
        print(Fore.RED + f"Error closing {symbol}: {resp['error']}")
        return
    exit_price = get_current_price(symbol)
    profit = (exit_price - entry_price) * volume
    duration_hours = (datetime.now(timezone.utc) - position['entry_time']).total_seconds() / 3600
    trade = {
        'symbol': symbol,
        'type': 'take_profit',
        'entry': entry_price,
        'exit': exit_price,
        'profit': profit,
        'entry_time': position['entry_time'],
        'exit_time': datetime.now(timezone.utc),
        'duration': duration_hours,
        'order_type': position.get('order_type', ""),
        'strategy_type': position.get('strategy_type', "")
    }
    trades.setdefault(symbol, []).append(trade)
    positions[symbol].remove(position)
    save_positions()
    log_trade_csv(trade)
    print(Fore.YELLOW + f"[{symbol}] ✅ Trade closed at {exit_price:.4f} | PnL: {profit:.2f}")

# =======================
# Load existing positions on startup (optionally augment with OpenPositions)
# =======================
def load_open_positions_from_kraken():
    """Load open positions directly from Kraken (gives opentm and margin info)."""
    resp = kraken_private_request("OpenPositions", {"docalcs": True})
    if resp.get("error"):
        print(Fore.RED + f"Error fetching open positions: {resp['error']}")
        return
    for txid, pos in resp['result'].items():
        pair = pos.get('pair')
        # normalize to friendly symbol if possible (use mapping inverse)
        # We'll keep pair as is and try to map it to our symbols list if possible
        # Compute entry price and volume
        try:
            entry_price = float(pos['cost']) / float(pos['vol'])
        except Exception:
            entry_price = float(pos.get('price', 0))
        volume = float(pos['vol'])
        order_type = "margin" if pos.get('margin') == "1" else "spot"
        entry_time = datetime.fromtimestamp(int(float(pos.get('opentm', time.time()))), timezone.utc)
        # Map pair back to symbol key such as "CELOUSD" if possible
        friendly = None
        # search cache for mapping pair->friendly
        for k, v in PAIR_CACHE.items():
            if v == pair:
                friendly = k
                break
        if not friendly:
            # fallback to pair name itself
            friendly = pair
        trade = {
            'symbol': friendly,
            'type': 'market_buy',
            'entry': entry_price,
            'entry_time': entry_time,
            'volume': volume,
            'order_type': order_type,
            'stop_txid': None,
            'take_profit_enabled': True,
            'strategy_type': "unknown",
            'tp_points': []
        }
        positions.setdefault(friendly, []).append(trade)
        trades.setdefault(friendly, []).append(trade)
        print(Fore.LIGHTBLUE_EX + f"♻️ Loaded open position: {friendly} | Entry: {entry_price:.4f} | Vol: {volume:.4f} | Type: {order_type} | Opened: {entry_time}")

# =======================
# Boot: load caches & persisted positions
# =======================
# ensure pair cache exists (already built above if empty)
if not PAIR_CACHE:
    PAIR_CACHE = build_pair_cache()

# Load persisted positions (this will prefer persisted positions.json)
if os.path.isfile(positions_file):
    load_positions()
else:
    # If no positions.json, attempt to import open positions from Kraken
    load_open_positions_from_kraken()
    save_positions()

# =======================
# Main loop
# =======================
last_portfolio_update = 0
portfolio_update_interval = 300
initial_scan_done = False

try:
    while True:
        now = time.time()
        for symbol in symbols:
            try:
                df = fetch_ohlc(symbol)
                if df is None or len(df) < bollinger_length:
                    continue
                df = calculate_bollinger(df)
                last_closed = df.iloc[-2]
                if last_scanned[symbol] == last_closed['time']:
                    continue
                last_scanned[symbol] = last_closed['time']

                print(Fore.CYAN + f"[{symbol}] Scanning {last_closed['time']} | Close={last_closed['close']:.4f}, Lower={last_closed['lower']:.4f}")

                # Entry & exit
                scan_for_entry(symbol, last_closed)
                for pos in positions.get(symbol, [])[:]:
                    if last_closed['close'] > last_closed['mean'] and pos.get('take_profit_enabled'):
                        close_position(symbol, pos)

            except Exception as e:
                print(Fore.RED + f"[{symbol}] Skipping symbol due to error: {e}")

        # --- Portfolio update ---
        if now - last_portfolio_update >= portfolio_update_interval or not initial_scan_done:
            last_portfolio_update = now
            initial_scan_done = True

            total_equity = get_total_equity_usd()
            print(Style.BRIGHT + Fore.MAGENTA + f"\n📊 Portfolio Update @ {datetime.now(timezone.utc)} | Cash/Total Equity: ${total_equity:.2f}")

            for sym, pos_list in positions.items():
                for pos in pos_list:
                    current_price = get_current_price(sym)
                    if current_price is None:
                        continue
                    pos_value = current_price * pos['volume']
                    unrealized = (current_price - pos['entry']) * pos['volume']
                    duration_hours = (datetime.now(timezone.utc) - pos['entry_time']).total_seconds() / 3600
                    print(Fore.LIGHTWHITE_EX + f"[{sym}] Entry: {pos['entry']:.4f} | Qty: {pos['volume']:.4f} | Current: {current_price:.4f} | $ Value: {pos_value:.2f} | PnL: {format_pnl(unrealized)} | Duration: {duration_hours:.2f}h | Type: {pos['order_type']} | Strategy: {pos.get('strategy_type','')}")
            # Time until next 4h candle
            now_utc = datetime.now(timezone.utc)
            hours = now_utc.hour % 4
            minutes = now_utc.minute
            seconds = now_utc.second
            seconds_until_next_candle = ((3 - hours) * 3600) + ((59 - minutes) * 60) + (60 - seconds)
            print(Fore.LIGHTBLUE_EX + f"⏱ Time until next entry scan: {seconds_until_next_candle//3600}h {(seconds_until_next_candle%3600)//60}m {seconds_until_next_candle%60}s")
            print(Fore.MAGENTA + "-"*60)

        time.sleep(10)

except KeyboardInterrupt:
    print(Fore.RED + "🛑 Bot stopped manually.")
