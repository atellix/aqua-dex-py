#!/usr/bin/env python3
import json
import time
import base64
import pprint
import krock32
import asyncio
from solders.pubkey import Pubkey
from anchorpy import Provider, Wallet
from solana.rpc.async_api import AsyncClient

from aquadex import AquadexClient
from aquadex_client.accounts import TradeResult

def encode_order_id(buf):
    rbuf = buf[::-1]
    encoder = krock32.Encoder(checksum=False)
    encoder.update(rbuf)
    return encoder.finalize().lower()

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
        sig = await market.order(
            side = 'ask',
            limit = True,
            quantity = 5,
            price = 5.70,
        )
        log = await aqua.fetch_transaction(sig)
        if not(log):
            print('No log')
        else:
            return_data = base64.b64decode(json.loads(log.to_json())['result']['meta']['returnData']['data'][0])
            return_data = TradeResult.discriminator + return_data
            return_data = return_data + bytearray(56 - len(return_data))
            return_data = TradeResult.decode(return_data).to_json()
            print(return_data)
            print(encode_order_id(return_data['order_id'].to_bytes(16, 'little')))

    if False:
        print(await market.cancel_order('ask', '00000000avwt00000000000030'))

    #print(await market.orderbook())

    # close socket
    #await client.close()

asyncio.run(main())

