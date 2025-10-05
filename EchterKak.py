import time
import pandas as pd
from datetime import datetime, timezone
from colorama import Fore, Style, init
import krakenex
import csv
import os

# =======================
# Initialize
# =======================
init(autoreset=True)

# ====== MANUAL API KEY/SECRET ======
api_key = "NBcae3Tbuc3qupKsDDUX4yiuHCx9qZriNpRy7waABK28hZ9PDULthpWe"
api_secret = "ZOOOjkYN4W9vIBBH7p/ji+qdy9SQuJyvaZ+7911ELMJTETy/ibI+SC9vanb3+1TcVI5aLM0Z1hoURhFmCdNSbg=="
kraken = krakenex.API(key=api_key, secret=api_secret)

trade_log_file = "trades_log.csv"

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
position_size_pct = 0.01  # 1% of current equity
stop_loss_pct = 0.40

positions = {s: [] for s in symbols}
trades = {s: [] for s in symbols}
last_scanned = {s: None for s in symbols}

# =======================
# Helper Functions
# =======================
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

def kraken_private_request(method, data=None):
    resp = kraken.query_private(method, data or {})
    return resp

def log_trade_csv(trade):
    file_exists = os.path.isfile(trade_log_file)
    with open(trade_log_file, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'type', 'symbol', 'entry', 'exit', 'profit', 'entry_time', 'exit_time', 'duration'
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
            'duration': f"{trade.get('duration', ''):.2f}" if trade.get('duration') else ""
        })

def format_pnl(value):
    return Fore.GREEN + f"{value:.2f}" + Style.RESET_ALL if value >= 0 else Fore.RED + f"{value:.2f}" + Style.RESET_ALL

# =======================
# Portfolio / Equity
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

# =======================
# Trading functions
# =======================
def place_market_order(symbol, side, equity_pct=0.01):
    total_equity = get_total_equity_usd()
    if total_equity <= 0:
        print(Fore.RED + "Cannot place order: account equity unavailable")
        return None
    price = get_current_price(symbol)
    if price is None:
        return None
    volume_usd = total_equity * equity_pct
    volume = volume_usd / price
    data = {"pair": symbol, "type": side, "ordertype": "market", "volume": f"{volume:.8f}"}
    resp = kraken_private_request("AddOrder", data)
    if resp.get("error"):
        print(Fore.RED + f"Order error for {symbol}: {resp['error']}")
        return None
    txid = resp['result']['txid'][0]
    print(Fore.GREEN + f"✅ Market order placed: {side.upper()} {volume:.6f} {symbol} | TXID: {txid}")
    return volume, price

def place_stop_loss(symbol, entry_price, side, volume, stop_loss_pct=0.40):
    stop_price = entry_price * (1 - stop_loss_pct) if side == "buy" else entry_price * (1 + stop_loss_pct)
    data = {
        "pair": symbol,
        "type": "sell" if side=="buy" else "buy",
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
    if not txid:
        return
    resp = kraken_private_request("CancelOrder", {"txid": txid})
    if resp.get("error"):
        print(Fore.RED + f"Failed to cancel stop-loss {txid}: {resp['error']}")
    else:
        print(Fore.YELLOW + f"🗑 Stop-loss {txid} canceled")

def scan_for_entry(symbol, last_closed_candle):
    if last_closed_candle['close'] < last_closed_candle['lower'] and len(positions[symbol])==0:
        result = place_market_order(symbol, "buy", position_size_pct)
        if result:
            volume, entry_price = result
            stop_txid = place_stop_loss(symbol, entry_price, "buy", volume, stop_loss_pct)
            trade = {
                'symbol': symbol,
                'type': 'market_buy',
                'entry': entry_price,
                'entry_time': datetime.now(timezone.utc),
                'volume': volume,
                'stop_txid': stop_txid
            }
            trades[symbol].append(trade)
            positions[symbol].append(trade)
            log_trade_csv(trade)
            print(Fore.GREEN + f"[{symbol}] 🚀 Market BUY executed at {entry_price:.4f} with stop-loss set")

def close_position(symbol, position):
    cancel_stop_loss(position.get('stop_txid'))
    volume = position['volume']
    entry_price = position['entry']
    resp = kraken_private_request("AddOrder", {"pair": symbol, "type": "sell", "ordertype": "market", "volume": f"{volume:.8f}"})
    if resp.get("error"):
        print(Fore.RED + f"Error closing {symbol}: {resp['error']}")
        return
    exit_price = get_current_price(symbol)
    profit = (exit_price - entry_price) * volume
    trade = {
        'symbol': symbol,
        'type': 'take_profit',
        'entry': entry_price,
        'exit': exit_price,
        'profit': profit,
        'entry_time': position['entry_time'],
        'exit_time': datetime.now(timezone.utc),
        'duration': (datetime.now(timezone.utc) - position['entry_time']).total_seconds() / 3600
    }
    trades[symbol].append(trade)
    log_trade_csv(trade)
    positions[symbol].remove(position)
    print(Fore.YELLOW + f"[{symbol}] ✅ Trade closed at {exit_price:.4f} | PnL: {profit:.2f}")

# =======================
# Main loop
# =======================
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
            print(Style.BRIGHT + Fore.MAGENTA + f"\n📊 Portfolio Update @ {datetime.now(timezone.utc)} | Cash/Total Equity: ${total_equity:.2f}")

            for sym in symbols:
                for pos in positions[sym]:
                    current_price = get_current_price(sym)
                    if current_price is None:
                        continue
                    pos_value = current_price * pos['volume']
                    unrealized = (current_price - pos['entry']) * pos['volume']
                    print(Fore.LIGHTWHITE_EX + f"[{sym}] Entry: {pos['entry']:.4f} | Qty: {pos['volume']:.4f} | Current: {current_price:.4f} | $ Value: {pos_value:.2f} | PnL: {format_pnl(unrealized)}")

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
