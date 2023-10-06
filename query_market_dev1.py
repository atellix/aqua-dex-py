#!/usr/bin/env python3
import json
import pprint
import asyncio
from solders.pubkey import Pubkey
from anchorpy import Provider, Wallet
from solana.rpc.async_api import AsyncClient

from aquadex import AquadexClient

async def main():
    client = AsyncClient("https://api.devnet.solana.com")
    provider = Provider(client, Wallet.local())

    dev_program_id = 'AQUAvuZCFUGtSc8uQBaTXfJz3YjMUbinMeXDoDQmZLvX'
    aqua = AquadexClient(client, provider, dev_program_id)

    market_file = 'market_dev_sol_usdc.json'
    with open(market_file) as f:
        market_data = json.load(f)
    #print(market_data)

    # load market data
    market = await aqua.load_market(market_data['market'])

    # print orderbook
    print('Orderbook')
    book = await market.orderbook()
    #pprint.pprint(book)

    if True:
        for order in book['asks']:
            print('Ask ' + order['key'])
            await market.cancel_order('ask', order['key'])
        for order in book['bids']:
            print('Bid ' + order['key'])
            await market.cancel_order('ask', order['key'])

    # close socket
    await client.close()

asyncio.run(main())

