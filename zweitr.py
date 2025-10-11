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
position_size_pct = 0.01
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
    # Don't rebuild every time; just warn
    return None

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
# OHLC and Bollinger
# =======================
def fetch_ohlc(symbol, interval=240):
    pair = resolve_pair(symbol)
    if not pair:
        return None
    resp = kraken.query_public("OHLC", {"pair": pair, "interval": interval})
    if resp.get("error"):
        print(Fore.RED + f"OHLC fetch error {symbol}: {resp['error']}")
        return None
    result_key = list(resp["result"].keys())[0]
    data = resp["result"][result_key]
    df = pd.DataFrame(data, columns=["time","open","high","low","close","vwap","volume","count"])
    df = df.astype({"time": int, "open": float, "high": float, "low": float, "close": float,
                    "vwap": float, "volume": float, "count": int})
    return df

def calculate_bollinger(df):
    df['mean'] = df['close'].rolling(bollinger_length).mean()
    df['std'] = df['close'].rolling(bollinger_length).std()
    df['upper'] = df['mean'] + bollinger_std * df['std']
    df['lower'] = df['mean'] - bollinger_std * df['std']
    return df

# =======================
# Trading logic
# =======================
def scan_for_entry(symbol, last_closed):
    close = last_closed['close']
    lower = last_closed['lower']

    if close < lower:
        # Calculate trade size based on total portfolio equity with leverage = 2x
        volume = calculate_trade_volume(symbol, leverage=2)
        if volume <= 0:
            print(Fore.YELLOW + f"Skipping {symbol} due to zero volume")
            return

        # Place margin order
        result = place_market_order(symbol, "buy", volume, "margin")
        if result:
            vol, price, lvg_type = result
            open_position(symbol, "buy", vol, lvg_type)
            place_stop_loss(symbol, price, "buy", vol, stop_loss_pct)

def close_position(symbol, pos):
    volume = pos['volume']
    place_market_order(symbol, "sell", volume, pos['type'])
    positions[symbol].remove(pos)
    print(Fore.YELLOW + f"❌ Position closed {symbol}")

# =======================
# Orders & positions
# =======================
def place_market_order(symbol, side, volume, desired_order_type="margin"):
    if volume <= 0:
        print(Fore.RED + f"Invalid volume for {symbol}")
        return None

    pair = resolve_pair(symbol)
    if not pair:
        return None

    data = {"pair": pair, "type": side, "ordertype": "market", "volume": f"{volume:.8f}"}

    if desired_order_type == "margin":
        data["leverage"] = "2:1"

    resp = kraken_private_request("AddOrder", data)

    # Fallback to spot if margin fails
    if resp.get("error"):
        if desired_order_type == "margin":
            print(Fore.YELLOW + f"Margin order failed for {symbol}: {resp['error']}. Trying spot order...")
            data.pop("leverage")
            resp = kraken_private_request("AddOrder", data)
        if resp.get("error"):
            print(Fore.RED + f"Order failed for {symbol}: {resp['error']}")
            return None

    txid = resp['result']['txid'][0]
    price = get_current_price(symbol)
    print(Fore.GREEN + f"✅ {side.capitalize()} order placed {symbol} @ {price:.4f} | TXID {txid}")
    return volume, price, desired_order_type

def place_stop_loss(symbol, entry_price, side, volume, stop_loss_pct=0.4):
    stop_price = entry_price * (1 - stop_loss_pct) if side == "buy" else entry_price * (1 + stop_loss_pct)
    pair = resolve_pair(symbol)
    data = {"pair": pair, "type": "sell" if side == "buy" else "buy",
            "ordertype": "stop-loss", "price": f"{stop_price:.4f}", "volume": f"{volume:.8f}", "leverage": "2:1"}
    resp = kraken_private_request("AddOrder", data)
    if resp.get("error"):
        print(Fore.YELLOW + f"Stop-loss error for {symbol}: {resp['error']}")
        data.pop("leverage")
        resp = kraken_private_request("AddOrder", data)
        if resp.get("error"):
            print(Fore.RED + f"Stop-loss failed {symbol}: {resp['error']}")
            return None
    txid = resp['result']['txid'][0]
    print(Fore.RED + f"🛑 Stop-loss set at {stop_price:.4f} | TXID {txid}")
    return txid
    
def open_position(symbol, side, volume, leverage_type):
    price = get_current_price(symbol)
    if not price:
        return

    # Exposure is total value of position
    exposure = volume * price

    # Adjust margin according to leverage
    leverage = 2 if leverage_type == "margin" else 1
    margin = exposure / leverage

    pos = {
        "side": side,
        "volume": volume,
        "entry_price": price,
        "exposure": exposure,
        "margin": margin,
        "leverage": leverage,
        "type": leverage_type,
        "timestamp": time.time()
    }
    positions[symbol].append(pos)

    print(Fore.CYAN + f"📌 Position opened: {symbol} {side} {volume:.6f} @ {price:.2f} | "
                       f"Exposure: ${exposure:.2f} | Margin: ${margin:.2f} | Lvg: {leverage}x")

# =======================
# Portfolio & exposure
# =======================
def get_account_balance():
    resp = kraken_private_request("Balance")
    if resp.get("error"):
        print(Fore.RED + f"❌ Balance error: {resp['error']}")
        return {}
    return resp["result"]
    
# =======================
# Portfolio & exposure
# =======================
# =======================
# Portfolio & exposure
# =======================
def get_total_equity_usd():
    """
    Calculate total portfolio equity in USD:
    cash + value of all coins (including open positions)
    """
    balances = get_account_balance()
    if not balances:
        return 0

    total_equity = 0
    for asset, amount in balances.items():
        amount = float(amount)
        if amount <= 0:
            continue

        if asset == "ZUSD":  # Cash
            total_equity += amount
        else:
            symbol = asset.replace("X", "").replace("Z", "") + "USD"
            price = get_current_price(symbol)
            if price is not None:
                total_equity += amount * price

    return total_equity

def calculate_trade_volume(symbol, leverage=2):
    """
    Calculate number of units to buy for target exposure with given leverage.
    Position sizing is based on TOTAL portfolio equity (cash + coins).
    """
    equity = get_total_equity_usd()
    if equity <= 0:
        print(Fore.RED + "❌ Cannot calculate trade size: equity is zero")
        return 0

    price = get_current_price(symbol)
    if not price:
        return 0

    # Target exposure in USD for this trade
    target_exposure = equity * position_size_pct

    # Asset units to buy to reach target exposure
    volume_asset = target_exposure / price

    # Margin required for leveraged trades
    margin_required = target_exposure / leverage

    print(Fore.LIGHTBLUE_EX + f"[{symbol}] Total equity: ${equity:.2f} | "
                               f"Target exposure: ${target_exposure:.2f} (~{volume_asset:.6f} {symbol}), "
                               f"Margin required: ${margin_required:.2f} @ {leverage}x leverage")
    return volume_asset

def format_pnl(value):
    """Format PnL with + / - sign and 2 decimals"""
    return f"{value:+,.2f}"
# =======================
# Check Kraken for existing positions
# =======================
def get_all_open_positions():
    resp = kraken_private_request("OpenPositions")
    if resp.get("error"):
        print(Fore.RED + f"❌ Error fetching open positions: {resp['error']}")
        return {}
    return resp.get("result", {})

def is_already_long_on_kraken(symbol, open_positions):
    pair = resolve_pair(symbol)
    if not pair:
        return False
    for txid, pos in open_positions.items():
        if pos.get("pair") == pair and pos.get("type") == "buy":
            return True
    return False

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

            # --- Fetch all open positions from Kraken ---
            open_positions = get_all_open_positions()

            # --- Sync local positions with Kraken positions ---
            for symbol in symbols:
                positions[symbol] = []  # reset local positions

            for txid, pos in open_positions.items():
                kraken_pair = pos.get("pair") or ""
                side = pos.get("type") or "buy"
                volume = float(pos.get("vol", 0))
                cost = float(pos.get("cost", 0))
                price = cost / volume if volume > 0 else 0
                leverage_type = "margin" if float(pos.get("margin", 0)) > 0 else "spot"

                for s in symbols:
                    if resolve_pair(s) == kraken_pair:
                        positions[s].append({
                            "side": side,
                            "volume": volume,
                            "entry_price": price,
                            "leverage": 2 if leverage_type=="margin" else 1,
                            "type": leverage_type
                        })

            # --- Scan symbols for entries/exits ---
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

                    print(Fore.CYAN + f"[{symbol}] Scanning {last_closed['time']} | "
                                       f"Close={last_closed['close']:.4f}, Lower={last_closed['lower']:.4f}")

                    # --- Skip if already long on Kraken ---
                    if is_already_long_on_kraken(symbol, open_positions):
                        print(Fore.YELLOW + f"⚠️ Already long {symbol} on Kraken — skipping entry")
                        continue

                    # --- Scan for new entry ---
                    scan_for_entry(symbol, last_closed)

                    # Close positions if price above mean
                    for pos in positions[symbol][:]:
                        if last_closed['close'] > last_closed['mean']:
                            close_position(symbol, pos)

                except Exception as e:
                    print(Fore.RED + f"[{symbol}] Skipping symbol due to error: {e}")

            # --- Portfolio update ---
            if now - last_portfolio_update >= portfolio_update_interval or not initial_scan_done:
                last_portfolio_update = now
                initial_scan_done = True

                total_equity = get_total_equity_usd()
                print(Style.BRIGHT + Fore.MAGENTA +
                      f"\n📊 Portfolio Update @ {datetime.now(timezone.utc)} | Total Equity: ${total_equity:.2f}")

                # Print each position
                for sym in symbols:
                    for pos in positions[sym]:
                        current_price = get_current_price(sym)
                        if current_price is None:
                            continue

                        pos_value = pos['volume'] * current_price
                        margin = pos['exposure'] / pos['leverage'] if 'exposure' in pos else pos_value / pos['leverage']

                        unrealized = (current_price - pos['entry_price']) * pos['volume'] \
                            if pos['side'] == "buy" else (pos['entry_price'] - current_price) * pos['volume']

                        print(Fore.LIGHTWHITE_EX + f"[{sym}] Side: {pos['side'].upper()} | "
                                                    f"Entry: {pos['entry_price']:.4f} | Qty: {pos['volume']:.6f} | "
                                                    f"Current: {current_price:.4f} | Exposure: ${pos_value:.2f} | "
                                                    f"Margin: ${margin:.2f} | Lvg: {pos['leverage']}x | "
                                                    f"PnL: {format_pnl(unrealized)}")

                # Total portfolio summary
                cash_usd = float(get_account_balance().get("ZUSD", 0))
                total_margin = sum(p['exposure'] / p['leverage'] if 'exposure' in p else p['volume']*get_current_price(sym)/p['leverage'] 
                                   for sym in positions for p in positions[sym])
                total_exposure = sum(p['exposure'] if 'exposure' in p else p['volume']*get_current_price(sym)
                                     for sym in positions for p in positions[sym])

                print(Fore.LIGHTBLUE_EX + f"\n💰 Cash: ${cash_usd:.2f} | "
                                           f"Total Margin: ${total_margin:.2f} | "
                                           f"Total Exposure: ${total_exposure:.2f} | "
                                           f"Total Equity: ${total_equity:.2f}\n")

                # Time until next 4h candle
                now_utc = datetime.now(timezone.utc)
                hours = now_utc.hour % 4
                minutes = now_utc.minute
                seconds = now_utc.second
                seconds_until_next_candle = ((3 - hours) * 3600) + ((59 - minutes) * 60) + (60 - seconds)
                print(Fore.LIGHTBLUE_EX + f"⏱ Time until next entry scan: {seconds_until_next_candle//3600}h "
                                           f"{(seconds_until_next_candle%3600)//60}m {seconds_until_next_candle%60}s")
                print(Fore.MAGENTA + "-"*60)

            time.sleep(10)

    except KeyboardInterrupt:
        print(Fore.RED + "🛑 Bot stopped manually.")

    except KeyboardInterrupt:
        print(Fore.RED + "🛑 Bot stopped manually.")
