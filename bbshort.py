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

# Use a unique reference for this bot
BOT_USERREF = 999002  # pick any unique number, keep it the same across runs


trade_log_file = "trades_log.csv"
positions_file = "positions.json"
PAIR_CACHE_FILE = "kraken_pairs.json"

# =======================
# Strategy parameters
# =======================
symbols = ["AAVEUSD","ADAUSD","AEROUSD","ALGOUSD","APEUSD","APTUSD","ARBUSD","ATOMUSD","AVAXUSD","AVNTUSD","AXSUSD","BATUSD","BCHUSD","BLURUSD","BNBUSD","BONKUSD","CHZUSD","COMPUSD","CRVUSD","DAIUSD","DASHUSD","DOGUSD","DOTUSD","DYDXUSD","EIGENUSD","ENAUSD","ENSUSD","FARTCOINUSD","FETUSD","FILUSD","FLOKIUSD","FLOWUSD","FLRUSD","GALAUSD","GOATUSD","GRTUSD","ICPUSD","IMXUSD","INJUSD","JASMYUSD","JUPUSD","KAITOUSD","KASUSD","KAVAUSD","KEEPUSD","KNCUSD","KSMUSD","LDOUSD","LINKUSD","LRCUSD","MANAUSD","MELANIAUSD","MEWUSD","MINAUSD","MOGUSD","MOODENGUSD","MORPHOUSD","NANOUSD","NEARUSD","OMGUSD","OMUSD","ONDOUSD","OPUSD","PAXGUSD","PENGUUSD","PEPEUSD","POLUSD","POPCATUSD","PUMPUSD","PYTHUSD","QTUMUSD","RAYUSD","RENDERUSD","RUNEUSD","SAGAUSD","SANDUSD","SCUSD","SEIUSD","SHIBUSD","SNXUSD","SOLUSD","SPXUSD","STBLUSD","STRKUSD","STXUSD","SUIUSD","SUSHIUSD","SYRUPUSD","TAOUSD","TIAUSD","TONUSD","TRUMPUSD","TRXUSD","TURBOUSD","UNIUSD","USDCUSD","USDTUSD","VIRTUALUSD","WIFUSD","WLDUSD","WLFIUSD","WUSD","XCNUSD","XDGUSD","ETCUSD","ETHUSD","LTCUSD","XPLUSD","XTZUSD","XBTUSD","XLMUSD","XMRUSD","XRPUSD","ZECUSD","YFIUSD","ZKUSD","ZROUSD","ZRXUSD"]
bollinger_length = 60
bollinger_std = 5
position_size_pct = 0.10
stop_loss_pct = 0.10

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
    """
    Entry signal:
    - Go SHORT if last closed candle closes ABOVE the upper 5σ Bollinger band (60 bars).
    - Set stop loss 10% above entry price.
    """
    close = last_closed['close']
    upper = last_closed['upper']

    # ✅ Entry trigger: close above upper band
    if close > upper:
        volume = calculate_trade_volume(symbol, leverage=2)
        if volume <= 0:
            print(Fore.YELLOW + f"Skipping {symbol} due to zero volume")
            return

        # Skip if already shorting in memory
        if positions.get(symbol) and any(p['side'].lower() == "sell" for p in positions[symbol]):
            print(Fore.YELLOW + f"⚠️ Already short {symbol}, skipping entry")
            return

        # Skip if already short on Kraken
        open_positions = get_all_open_positions()
        if is_already_short_on_kraken(symbol, open_positions):
            print(Fore.YELLOW + f"⚠️ Already short {symbol} on Kraken, skipping entry")
            return

        # ✅ Place SHORT (sell) order
        result = place_market_order(symbol, "sell", volume, "margin")
        if result:
            vol, price, lvg_type = result
            open_position(symbol, "sell", vol, lvg_type)

def sync_stop_loss_txids():
    """Match open stop-loss orders from Kraken to positions."""
    open_orders = get_open_orders()
    for symbol, pos_list in positions.items():
        for pos in pos_list:
            if pos.get("stop_loss_txid"):
                continue  # already tracked
            # Find a stop-loss for this symbol and volume
            for oid, order in open_orders.items():
                if (order.get("descr", {}).get("pair") == resolve_pair(symbol) and
                    order.get("descr", {}).get("ordertype") == "stop-loss" and
                    float(order.get("vol", 0)) == pos["volume"]):
                    pos["stop_loss_txid"] = oid
                    break
    save_positions()

def close_position(symbol, pos):
    """Close position and cancel its stop-loss before exiting."""
    # Cancel stop-loss if exists
    if pos.get("stop_loss_txid"):
        resp = kraken_private_request("CancelOrder", {"txid": pos["stop_loss_txid"]})
        if resp.get("error"):
            print(Fore.RED + f"Failed to cancel stop-loss {pos['stop_loss_txid']} for {symbol}: {resp['error']}")
        else:
            print(Fore.YELLOW + f"🗑 Canceled stop-loss {pos['stop_loss_txid']} for {symbol}")

    # Place market order to exit
    place_market_order(symbol, "sell", pos['volume'], pos['type'])
    positions[symbol].remove(pos)
    save_positions()
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

    data = {
        "pair": pair,
        "type": side,
        "ordertype": "market",
        "volume": f"{volume:.8f}",
        "userref": BOT_USERREF
    }

    if desired_order_type == "margin":
        data["leverage"] = "2:1"

    resp = kraken_private_request("AddOrder", data)
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
    print(Fore.GREEN + f"✅ {side.upper()} order placed {symbol} @ {price:.4f} | TXID {txid}")

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

    # Exposure & margin
    exposure = volume * price
    leverage = 2 if leverage_type == "margin" else 1
    margin = exposure / leverage

    # Place stop-loss and save txid
    stop_loss_txid = place_stop_loss(symbol, price, side, volume, stop_loss_pct)

    pos = {
        "side": side,
        "volume": volume,
        "entry_price": price,
        "exposure": exposure,
        "margin": margin,
        "leverage": leverage,
        "type": leverage_type,
        "stop_loss_txid": stop_loss_txid,
        "timestamp": time.time(),
        "userref": BOT_USERREF 
    }
    positions[symbol].append(pos)
    save_positions()

    print(Fore.CYAN + f"📌 Position opened: {symbol} {side} {volume:.6f} @ {price:.2f} | "
                       f"Exposure: ${exposure:.2f} | Margin: ${margin:.2f} | Lvg: {leverage}x | Stop-loss TXID: {stop_loss_txid}")

def get_open_orders():
    resp = kraken_private_request("OpenOrders")
    if resp.get("error"):
        print(Fore.RED + f"❌ Error fetching open orders: {resp['error']}")
        return {}
    return resp.get("result", {}).get("open", {})

def cancel_stop_loss_orders(symbol):
    open_orders = get_open_orders()
    pair = resolve_pair(symbol)
    canceled_orders = []

    for oid, order in open_orders.items():
        if order.get("descr", {}).get("pair") == pair and order.get("descr", {}).get("ordertype") == "stop-loss":
            resp = kraken_private_request("CancelOrder", {"txid": oid})
            if resp.get("error"):
                print(Fore.RED + f"Failed to cancel stop-loss {oid} for {symbol}: {resp['error']}")
            else:
                print(Fore.YELLOW + f"🗑 Canceled stop-loss {oid} for {symbol}")
                canceled_orders.append(oid)
    return canceled_orders

# =======================
# Portfolio & exposure
# =======================
def get_account_balance():
    resp = kraken_private_request("Balance")
    if resp.get("error"):
        print(Fore.RED + f"❌ Balance error: {resp['error']}")
        return {}
    return resp["result"]
    
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

def is_already_short_on_kraken(symbol, open_positions):
    pair = resolve_pair(symbol)
    if not pair:
        return False

    for txid, pos in open_positions.items():
        if pos.get("pair") == pair and pos.get("type") == "sell":
            return True
    return False

POSITIONS_FILE = "positions.json"

def save_positions():
    """Save current positions to a JSON file."""
    with open(POSITIONS_FILE, "w") as f:
        json.dump(positions, f, indent=2)

def resolve_symbol_from_pair(pair):
    """Convert Kraken pair string back to symbol, e.g., XXBTZUSD -> BTCUSD"""
    for sym, p in PAIR_CACHE.items():
        if p == pair:
            return sym
    return None
def load_positions():
    """Load positions from JSON file on startup with safe numeric conversion."""
    global positions
    if os.path.isfile(POSITIONS_FILE):
        try:
            with open(POSITIONS_FILE, "r") as f:
                positions = json.load(f)
                for sym, pos_list in positions.items():
                    for pos in pos_list:
                        # Ensure all expected numeric fields are floats
                        pos['volume'] = float(pos.get('volume', 0))
                        pos['entry_price'] = float(pos.get('entry_price', 0))
                        pos['exposure'] = float(pos.get('exposure', 0))
                        pos['margin'] = float(pos.get('margin', 0))
                        pos['leverage'] = float(pos.get('leverage', 1))
                        pos['timestamp'] = float(pos.get('timestamp', time.time()))
                        # Stop-loss TXID may be None
                        pos['stop_loss_txid'] = pos.get('stop_loss_txid')
        except Exception as e:
            print(Fore.RED + f"⚠️ Failed to load positions: {e}")
            positions = {s: [] for s in symbols}
    else:
        positions = {s: [] for s in symbols}

def sync_positions_from_kraken():
    resp = kraken_private_request("OpenPositions", {})
    if resp.get("error"):
        print(Fore.RED + f"Failed to sync positions: {resp['error']}")
        return

    result = resp.get("result", {})
    for txid, pos in result.items():
        pair = pos['pair']
        symbol = resolve_symbol_from_pair(pair)
        if not symbol:
          continue
        volume = float(pos['vol'])
        entry_price = float(pos['cost']) / volume if volume > 0 else 0
        leverage = float(pos.get('leverage', '1').replace(':1', ''))

        # userref may not always be present
        userref = int(pos.get('userref', 0))

        # check if already in positions
        exists = any(p.get("txid") == txid for p in positions.get(symbol, []))
        if exists:
            continue

        positions.setdefault(symbol, []).append({
            "txid": txid,
            "side": pos['type'],
            "entry_price": entry_price,
            "volume": volume,
            "exposure": float(pos['cost']),
            "leverage": leverage,
            "bot_initiated": (userref == BOT_USERREF),  # ✅ only tag bot trades
            "userref": userref
        })
    save_positions()

# =======================
# Flag all existing open positions as bot-initiated
# =======================
def flag_all_open_positions_as_bot_initiated():
    # 👇 Do nothing so this bot does not adopt foreign positions
    print(Fore.YELLOW + "⚠️ Existing positions ignored — bot will only manage its own new ones.")

def get_bot_positions():
    all_positions = get_open_positions()  # gets everything from Kraken
    bot_positions = [
        p for p in all_positions
        if str(p.get("userref")) == str(BOT_USERREF)
    ]
    return bot_positions

if __name__ == "__main__":
    print(Fore.CYAN + "🚀 Kraken Bot starting up...")

    # 1️⃣ Load previous positions from JSON
    load_positions()

    # 2️⃣ Sync currently open positions from Kraken
    sync_positions_from_kraken()

    # 3️⃣ Mark all currently open positions as bot-initiated
    flag_all_open_positions_as_bot_initiated()

    print(Fore.GREEN + "✅ Bot ready. Tracking positions for take-profit and stop-loss.")
  
    last_portfolio_update = 0
    portfolio_update_interval = 300  # 5 minutes
    initial_scan_done = False

    try:
        while True:
            now = time.time()

            # --- Fetch open margin positions ---
            open_positions = get_all_open_positions()

            # --- Fetch spot balances ---
            balances = get_account_balance()

            # --- Handle spot positions (deduplicated) ---
            for symbol in symbols:
                base = symbol.replace("USD", "")
                qty = float(balances.get(base, 0))
                if qty > 0:
                    current_price = get_current_price(symbol)
                    if current_price is None:
                        print(Fore.YELLOW + f"⚠️ Skipping spot position for {symbol} — price not available yet")
                        continue

                    rounded_price = round(current_price, 6)

                    # Remove any previous spot positions for this symbol
                    positions.setdefault(symbol, [])
                    positions[symbol] = [p for p in positions[symbol] if not p.get("spot", False)]

                    # Add a single clean spot position
                    positions[symbol].append({
                        "side": "BUY",
                        "entry_price": rounded_price,
                        "volume": qty,
                        "exposure": qty * rounded_price,
                        "leverage": 1,
                        "spot": True
                    })

            # --- Scan for entries ---
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
                                      f"Close={last_closed['close']:.4f}, Upper={last_closed['upper']:.4f}")

                    # Skip if already long on Kraken or holding spot
                    already_long = is_already_short_on_kraken(symbol, open_positions)
                    spot_amount = float(balances.get(symbol.replace("USD", ""), 0))
                    if already_long or spot_amount > 0:
                        print(Fore.YELLOW + f"⚠️ Already long {symbol} on Kraken — skipping entry")
                        continue

                    # Entry check
                    scan_for_entry(symbol, last_closed)

                    # Close positions if price > mean
                    for pos in positions[symbol][:]:
                        # Only manage bot-initiated positions
                        if not pos.get("bot_initiated", False):
                            continue
                    
                        if pos['side'].lower() == "buy" and last_closed['close'] > last_closed['mean']:
                            close_position(symbol, pos)
                        elif pos['side'].lower() == "sell" and last_closed['close'] < last_closed['mean']:
                            close_position(symbol, pos)


                except Exception as e:
                    print(Fore.RED + f"[{symbol}] Skipping symbol due to error: {e}")

            # --- Portfolio update ---
            if now - last_portfolio_update >= portfolio_update_interval or not initial_scan_done:
                last_portfolio_update = now
                initial_scan_done = True

                total_equity = get_total_equity_usd()
                print(Style.BRIGHT + Fore.MAGENTA + f"\n📊 Portfolio Update @ {datetime.now(timezone.utc)}")

                balances = get_account_balance()
                cash_usd = float(balances.get("ZUSD", 0))
                total_exposure = 0
                total_margin = 0
                total_unrealized = 0

                for sym in symbols:
                    pos_list = positions.get(sym, [])
                    if not pos_list:
                        continue

                    # --- Deduplicate positions ---
                    seen_positions = set()
                    clean_list = []
                    for pos in pos_list:
                        side = pos.get("side")
                        entry_price = pos.get("entry_price", 0)
                        volume = pos.get("volume", 0)
                        if not side or volume <= 0 or entry_price <= 0:
                            continue
                        pos_id = (side, round(entry_price, 6), round(volume, 6))
                        if pos_id in seen_positions:
                            continue
                        seen_positions.add(pos_id)
                        clean_list.append(pos)
                    positions[sym] = clean_list

                    # --- Print positions ---
                    for pos in clean_list:
                        current_price = get_current_price(sym)
                        if current_price is None:
                            continue

                        pos_value = pos['volume'] * current_price
                        margin = pos['exposure'] / pos['leverage']

                        if pos['side'].lower() == "buy":
                            unrealized = (current_price - pos['entry_price']) * pos['volume']
                        else:
                            unrealized = (pos['entry_price'] - current_price) * pos['volume']

                        total_exposure += pos['exposure']
                        total_margin += margin
                        total_unrealized += unrealized

                        print(Fore.LIGHTWHITE_EX +
                              f"[{sym}] Side: {pos['side'].upper()} | "
                              f"Entry: {pos['entry_price']:.4f} | Qty: {pos['volume']:.6f} | "
                              f"Current: {current_price:.4f} | Exposure: ${pos_value:.2f} | "
                              f"Margin: ${margin:.2f} | Lvg: {pos['leverage']}x | "
                              f"PnL: {format_pnl(unrealized)}")

                # --- Print portfolio summary ---
                total_equity = get_total_equity_usd()
                print(Fore.LIGHTBLUE_EX +
                      f"\n💰 Cash: ${cash_usd:.2f} | "
                      f"Total Margin: ${total_margin:.2f} | "
                      f"Total Exposure: ${total_exposure:.2f} | "
                      f"Total Unrealized PnL: {format_pnl(total_unrealized)} | "
                      f"Total Equity: ${total_equity:.2f}\n")

            # --- Countdown to next 4H candle ---
            now_utc = datetime.now(timezone.utc)
            hours = now_utc.hour % 4
            minutes = now_utc.minute
            seconds = now_utc.second
            seconds_until_next_candle = ((3 - hours) * 3600) + ((59 - minutes) * 60) + (60 - seconds)
            print(Fore.LIGHTBLUE_EX +
                  f"⏱ Time until next entry scan: {seconds_until_next_candle // 3600}h "
                  f"{(seconds_until_next_candle % 3600) // 60}m {seconds_until_next_candle % 60}s")
            print(Fore.MAGENTA + "-" * 60)

            time.sleep(10)

    except KeyboardInterrupt:
        print(Fore.RED + "🛑 Bot stopped manually.")
