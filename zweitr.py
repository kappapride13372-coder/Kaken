
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

    print(Style.BRIGHT + Fore.CYAN + "📊 Portfolio Status")
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
# =======================
# Main runtime loop
# =======================
if __name__ == "__main__":
    print(Fore.CYAN + "🚀 Kraken Bot started")
    print(Fore.YELLOW + "✅ Pair cache loaded and ready")
    print(Fore.WHITE + "Press CTRL+C to stop.\n")

    last_portfolio_update = 0
    portfolio_update_interval = 300  # 5 minutes
    initial_scan_done = False

    try:
        while True:
            now = time.time()

            # --- Scan for new signals only on new 4h candle ---
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

                    # Print scan info
                    print(Fore.CYAN + f"[{symbol}] Scanning {last_closed['time']} | Close={last_closed['close']:.4f}, Lower={last_closed['lower']:.4f}")

                    # Entry & exit checks
                    scan_for_entry(symbol, last_closed)
                    for pos in positions[symbol][:]:
                        if last_closed['close'] > last_closed['mean']:
                            close_position(symbol, pos)

                except Exception as e:
                    print(Fore.RED + f"[{symbol}] Skipping symbol due to error: {e}")

            # --- Portfolio update every 5 minutes ---
            if now - last_portfolio_update >= portfolio_update_interval or not initial_scan_done:
                last_portfolio_update = now
                initial_scan_done = True

                total_equity = get_total_equity_usd()
                print(Style.BRIGHT + Fore.MAGENTA + f"\n📊 Portfolio Update @ {datetime.now(timezone.utc)} | Total Equity: ${total_equity:.2f}")

                for sym in symbols:
                    for pos in positions[sym]:
                        current_price = get_current_price(sym)
                        if current_price is None:
                            continue
                        pos_value = current_price * pos['volume']
                        unrealized = (current_price - pos['entry_price']) * pos['volume'] if pos['side'] == "buy" else (pos['entry_price'] - current_price) * pos['volume']
                        print(Fore.LIGHTWHITE_EX + f"[{sym}] Entry: {pos['entry_price']:.4f} | Qty: {pos['volume']:.4f} | Current: {current_price:.4f} | $ Value: {pos_value:.2f} | PnL: {format_pnl(unrealized)}")

                # Time until next 4h candle close
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

