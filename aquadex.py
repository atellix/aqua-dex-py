#!/usr/bin/env python3

import json
import math
import struct
import base64
import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from anchorpy import Program, Provider, Wallet, Context
from anchorpy.idl import Idl
from anchorpy.program.common import translate_address
from aquadex_client.accounts import Market

SPL_TOKEN = Pubkey.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
ASC_TOKEN = Pubkey.from_string('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL')

def associated_token(token_mint, wallet, bump_seed=False):
    ata = Pubkey.find_program_address([bytes(wallet), bytes(SPL_TOKEN), bytes(token_mint)], ASC_TOKEN)
    if bump_seed:
        return ata
    return str(ata[0])

def program_address(seeds, program_id, bump_seed=False):
    pda = Pubkey.find_program_address(seeds, program_id)
    if bump_seed:
        return pda
    return str(pda[0])

def get_program(program_id, provider, idl_file):
    with open(idl_file) as f:
        idl = Idl.from_json(json.load(f))
    return Program(idl, translate_address(program_id), provider)

def get_market(market_file):
    with open(market_file) as f:
        market = json.load(f)
    return market

def decode_orders_vec(vec_data, pages):
    print(vec_data)
    header_size = vec_data['header_size']
    offset_size = vec_data['offset_size']
    alloc_items = vec_data['alloc_items']
    #print(offset_size)
    inst_per_page = math.floor((16384 - (header_size + offset_size)) / 32)
    vector_fmt = "<{}s2I{}s".format(offset_size, 16384 - (offset_size + 8))
    order_fmt = "<Qq"
    order_size = struct.calcsize(order_fmt)
    total_pages = math.floor(alloc_items / inst_per_page)
    if (alloc_items % inst_per_page) != 0:
        total_pages = total_pages + 1
    vec_pages = []
    for i in range(total_pages):
        pidx = vec_data['alloc_pages'][i]
        vec_pages.append(pages[pidx])
    order_spec = {'orders': []}
    for i in range(len(vec_pages)):
        res = struct.unpack(vector_fmt, vec_pages[i])
        if i == 0:
            order_spec['free_top'] = res[1]
            order_spec['next_index'] = res[2]
            #print(len(res[0]))
            #print(len(res[3]))
        for order_idx in range(inst_per_page):
            start_index = order_idx * order_size
            end_index = start_index + order_size
            order = struct.unpack(order_fmt, res[3][start_index:end_index])
            #print(order)
            order_spec['orders'].append({
                'amount': order[0],
                'expiry': order[1],
            })
            #print(alloc_items, len(order_spec['orders']))
            if len(order_spec['orders']) == alloc_items:
                i = len(vec_pages)
                break
    return order_spec

def decode_orderbook(orders_data):
    outer_fmt = "<H{}s".format(len(orders_data) - 2)
    inner_fmt = "<3Q16H"
    inner_size = struct.calcsize(inner_fmt)
    page_fmt = "<{}s".format(16384 * 6)
    # Unpack the outer struct
    outer_unpacked = struct.unpack(outer_fmt, orders_data)
    # Unpack the inner structs from the outer struct
    type_page = []
    for i in range(4):
        start_index = i * inner_size
        end_index = start_index + inner_size
        type_data = struct.unpack(inner_fmt, outer_unpacked[1][start_index:end_index])
        type_page.append({
            'header_size': type_data[0],
            'offset_size': type_data[1],
            'alloc_items': type_data[2],
            'alloc_pages': type_data[3:],
        })
    #print(type_page)
    pages = []
    page_data = outer_unpacked[1][end_index:]
    for i in range(6):
        start_index = i * 16384
        end_index = start_index + 16384
        pages.append(page_data[start_index:end_index])
    bid_map = type_page[0]
    ask_map = type_page[1]
    bid_vec = type_page[2]
    ask_vec = type_page[3]
    decode_orders_vec(bid_vec, pages)
    #decode_orders_vec(ask_vec, pages)
    #print(len(outer_unpacked[1][end_index:]) / 6)
    #print(pages[4])
    #pages = struct.unpack(page_fmt, outer_unpacked[2])
    return 'BOOK'

async def main():
    client = AsyncClient("https://api.devnet.solana.com")
    provider = Provider(client, Wallet.local())
    # load the Serum Swap Program (not the Serum dex itself).
    program_id = Pubkey.from_string('AQUAvuZCFUGtSc8uQBaTXfJz3YjMUbinMeXDoDQmZLvX')
    program = get_program(program_id, provider, 'idl/aqua_dex.json')
    #print(f'Wallet: {provider.wallet.public_key}')
    market_data = get_market('market_1.json')
    #print(market_data)
    market = await Market.fetch(client, Pubkey.from_string(market_data['market']))
    #print(market.to_json())
    resp = await client.get_account_info(Pubkey.from_string(market_data['orders']))
    #print(base64.b64decode(resp['result']['value']['data'][0]))
    print(decode_orderbook(base64.b64decode(resp['result']['value']['data'][0])))
    await program.close()

asyncio.run(main())
