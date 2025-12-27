import asyncio
import json
import logging
import sys

# ==========================================
# FIX: Python 3.14 / Windows Event Loop Support
# ==========================================
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
# ==========================================

from ib_insync import *


def get_portfolio_json():
    # Reduce log noise
    util.logToConsole(logging.CRITICAL)

    ib = IB()

    try:
        # Connect (Port 4001 for Gateway, 7496 for TWS)
        ib.connect('127.0.0.1', 4001, clientId=2)

        # -------------------------------------------------------
        # 1. FETCH POSITIONS
        # -------------------------------------------------------
        positions = []
        for p in ib.positions():
            positions.append({
                "symbol": p.contract.symbol,
                "shares": p.position,
                "avg_cost": p.avgCost
            })

        # -------------------------------------------------------
        # 2. FETCH CASH
        # -------------------------------------------------------
        free_cash = 0.0
        summary_list = ib.accountSummary()

        for item in summary_list:
            if item.tag == 'TotalCashValue' and item.currency == 'USD':
                free_cash = float(item.value)
                break

        # -------------------------------------------------------
        # 3. FETCH OPEN ORDERS (The Fix)
        # -------------------------------------------------------
        # 1. Ask TWS for all open orders
        ib.reqAllOpenOrders()
        # 2. Wait for the network response
        ib.sleep(1)

        orders = []
        # FIX: Use openTrades() instead of orders().
        # A 'Trade' object contains both the 'contract' (Symbol) and the 'order' (Action)
        for t in ib.openTrades():
            orders.append({
                "symbol": t.contract.symbol,  # <--- Now valid
                "action": t.order.action,  # Buy/Sell
                "qty": t.order.totalQuantity,
                "type": t.order.orderType,  # LMT/MKT/STP
                "status": t.orderStatus.status,  # Submitted/PreSubmitted
                "stop_price": t.order.auxPrice if t.order.auxPrice else 0.0
            })

        # -------------------------------------------------------
        # CONSTRUCT JSON
        # -------------------------------------------------------
        data = {
            "account": ib.wrapper.accounts[0] if ib.wrapper.accounts else "Unknown",
            "cash_usd": free_cash,
            "positions": positions,
            "open_orders": orders
        }

        return data

    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        ib.disconnect()