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

    if True:
        result = await market.order(
            side = 'ask',
            limit = True,
            quantity = 5,
            price = 5.70,
        )
        print(result)

    if False:
        print(await market.cancel_order('ask', '00000000avwt00000000000030'))

    #print(await market.orderbook())

    # close socket
    #await client.close()

asyncio.run(main())

