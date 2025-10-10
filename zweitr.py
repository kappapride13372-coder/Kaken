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

# =======================
# Strategy parameters
# =======================
symbols = [
    # your symbols...
]
bollinger_length = 180
bollinger_std = 3
position_size_pct = 0.2  # fraction of total equity to risk per position
stop_loss_pct = 0.40

# Positions structure:
# positions[symbol] = [
#     {entry, volume, entry_time, stop_txid, order_type, take_profit_enabled, strategy_type, tp_points}
# ]
positions = {s: [] for s in symbols}
trades = {s: [] for s in symbols}
last_scanned = {s: None for s in symbols}

# =======================
# Helper functions
# =======================
def kraken_private_request(method, data=None):
    resp = kraken.query_private(method, data or {})
    return resp

def fetch_ohlc(symbol, interval=240, since=None):
    params = {"pair": symbol, "interval": interval}
    if since:
        params["since"] = since
    resp = kraken.query_public("OHLC", params)
    if resp.get("error"):
        print(Fore.RED + f"Error fetching OHLC for {symbol}: {resp['error']}")
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
    try:
        resp = kraken.query_public("Ticker", {"pair": symbol})
        if resp.get("error"):
            print(Fore.RED + f"Error fetching price for {symbol}: {resp['error']}")
            return None
        return float(resp['result'][symbol]['c'][0])
    except Exception as e:
        print(Fore.RED + f"Exception getting price for {symbol}: {e}")
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
    resp = kraken_private_request("Balance")
    if resp.get("error"):
        print(Fore.RED + f"Error fetching balance: {resp['error']}")
        return 0
    balances = resp['result']
    total_equity = 0.0
    for asset, amount in balances.items():
        amount = float(amount)
        if amount <= 0:
            continue
        if asset in ["ZUSD", "USDT"]:
            total_equity += amount
        else:
            pair = f"X{asset}ZUSD" if asset != "XBT" else "XXBTZUSD"
            price = get_current_price(pair)
            if price:
                total_equity += amount * price
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
# Persistent storage
# =======================
def save_positions():
    with open(positions_file, "w") as f:
        serializable_positions = {}
        for sym, pos_list in positions.items():
            serializable_positions[sym] = []
            for pos in pos_list:
                pos_copy = pos.copy()
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
    total_equity = get_total_equity_usd()
    risk_cap_usd = total_equity * risk_pct

    available_margin = get_available_margin()
    if available_margin > 0:
        max_margin_volume = available_margin / price
        volume = min(max_margin_volume, risk_cap_usd / price)
        return volume, "margin"

    spot_balance = get_spot_balance("ZUSD")
    if spot_balance <= 0:
        return 0, None
    max_spot_volume = spot_balance / price
    volume = min(max_spot_volume, risk_cap_usd / price)
    return volume, "spot"

def place_market_order(symbol, side, volume, order_type="spot"):
    if volume <= 0:
        return None
    data = {"pair": symbol, "type": side, "ordertype": "market", "volume": f"{volume:.8f}"}
    if order_type == "margin":
        data["oflags"] = "fciq"
    resp = kraken_private_request("AddOrder", data)
    if resp.get("error"):
        print(Fore.RED + f"Order error for {symbol}: {resp['error']}")
        return None
    txid = resp['result']['txid'][0]
    return volume, get_current_price(symbol)

def place_stop_loss(symbol, entry_price, side, volume, stop_loss_pct=0.4):
    stop_price = entry_price * (1 - stop_loss_pct) if side=="buy" else entry_price * (1 + stop_loss_pct)
    data = {"pair": symbol, "type": "sell" if side=="buy" else "buy", "ordertype": "stop-loss", "price": f"{stop_price:.4f}", "volume": f"{volume:.8f}"}
    resp = kraken_private_request("AddOrder", data)
    if resp.get("error"):
        return None
    return resp['result']['txid'][0]

def cancel_stop_loss(txid):
    if not txid: return
    kraken_private_request("CancelOrder", {"txid": txid})

# =======================
# Trading logic
# =======================
def scan_for_entry(symbol, last_closed_candle):
    if last_closed_candle['close'] < last_closed_candle['lower'] and len(positions[symbol])==0:
        price = last_closed_candle['close']
        volume, order_type = calculate_order_volume(symbol, price, position_size_pct)
        if volume <= 0:
            return
        result = place_market_order(symbol, "buy", volume, order_type)
        if result:
            vol, entry_price = result
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
                'tp_points': [entry_price * 1.02, entry_price * 1.05]  # example
            }
            positions[symbol].append(trade)
            trades.setdefault(symbol, []).append(trade)
            save_positions()
            log_trade_csv(trade)

def close_position(symbol, position):
    cancel_stop_loss(position.get('stop_txid'))
    volume = position['volume']
    entry_price = position['entry']
    kraken_private_request("AddOrder", {"pair": symbol, "type": "sell", "ordertype": "market", "volume": f"{volume:.8f}"})
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

# =======================
# Load existing positions
# =======================
load_positions()

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
                if df is None or len(df) < bollinger_length: continue
                df = calculate_bollinger(df)
                last_closed = df.iloc[-2]
                if last_scanned[symbol] == last_closed['time']: continue
                last_scanned[symbol] = last_closed['time']
                scan_for_entry(symbol, last_closed)
                for pos in positions[symbol][:]:
                    if last_closed['close'] > last_closed['mean'] and pos.get('take_profit_enabled'):
                        close_position(symbol, pos)
            except Exception as e:
                print(Fore.RED + f"[{symbol}] Skipping symbol due to error: {e}")

        if now - last_portfolio_update >= portfolio_update_interval or not initial_scan_done:
            last_portfolio_update = now
            initial_scan_done = True
            total_equity = get_total_equity_usd()
            print(Style.BRIGHT + Fore.MAGENTA + f"\n📊 Portfolio Update @ {datetime.now(timezone.utc)} | Cash/Total Equity: ${total_equity:.2f}")
            for sym in symbols:
                for pos in positions[sym]:
                    current_price = get_current_price(sym)
                    if current_price is None: continue
                    pos_value = current_price * pos['volume']
                    unrealized = (current_price - pos['entry']) * pos['volume']
                    duration_hours = (datetime.now(timezone.utc) - pos['entry_time']).total_seconds() / 3600
                    print(Fore.LIGHTWHITE_EX + f"[{sym}] Entry: {pos['entry']:.4f} | Qty: {pos['volume']:.4f} | Current: {current_price:.4f} | $ Value: {pos_value:.2f} | PnL: {format_pnl(unrealized)} | Duration: {duration_hours:.2f}h | Type: {pos['order_type']} | Strategy: {pos.get('strategy_type','')}")
        time.sleep(10)

except KeyboardInterrupt:
    print(Fore.RED + "🛑 Bot stopped manually.")
