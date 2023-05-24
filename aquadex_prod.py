#!/usr/bin/env python3

import json
import math
import struct
import base64
import asyncio
import krock32
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from anchorpy import Program, Provider, Wallet, Context, Idl
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
        idl = Idl.from_json(f.read())
    return Program(idl, translate_address(program_id), provider)

def get_market(market_file):
    with open(market_file) as f:
        market = json.load(f)
    return market

def encode_order_id(buf):
    rbuf = buf[::-1]
    encoder = krock32.Encoder(checksum=False)
    encoder.update(rbuf)
    return encoder.finalize().lower()

def decode_node(tag, blob):
    data = None
    if tag == 1:
        node_fmt = '<I16s3I24s'
        rec = struct.unpack(node_fmt, blob)
        data = {
            'tag': rec[0],
            'key': rec[1],
            'prefix_len': rec[2],
            'children': [rec[3], rec[4]],
        }
    if tag == 2:
        node_fmt = '<2I16s32s'
        rec = struct.unpack(node_fmt, blob)
        data = {
            'tag': rec[0],
            'slot': rec[1],
            'key': rec[2],
            'owner': Pubkey(rec[3]),
        }
        price_fmt = '<8sQ'
        price_rec = struct.unpack(price_fmt, data['key'])
        data['price'] = price_rec[1]
        data['key'] = encode_order_id(data['key'])
    if tag == 3 or tag == 4:
        node_fmt = '<2I48s'
        rec = struct.unpack(node_fmt, blob)
        data = {
            'tag': rec[0],
            'next': rec[1],
        }
    return data

def decode_orders_map(map_data, pages):
    header_size = map_data['header_size']
    offset_size = map_data['offset_size']
    alloc_items = map_data['alloc_items']
    inst_per_page = math.floor((16384 - (header_size + offset_size)) / 56)
    vector_fmt = "<{}s2Q2IQ{}s".format(offset_size, 16384 - (offset_size + 32))
    node_fmt = "<I52s"
    node_size = struct.calcsize(node_fmt)
    total_pages = math.floor(alloc_items / inst_per_page)
    if (alloc_items % inst_per_page) != 0:
        total_pages = total_pages + 1
    map_pages = []
    for i in range(total_pages):
        pidx = map_data['alloc_pages'][i]
        map_pages.append(pages[pidx])
    node_spec = {'nodes': []}
    for i in range(len(map_pages)):
        res = struct.unpack(vector_fmt, map_pages[i])
        if i == 0:
            node_spec['bump_index'] = res[1]
            node_spec['free_list_len'] = res[2]
            node_spec['free_list_head'] = res[3]
            node_spec['root_node'] = res[4]
            node_spec['leaf_count'] = res[5]
        for node_idx in range(inst_per_page):
            start_index = node_idx * node_size
            end_index = start_index + node_size
            node_blob = res[6][start_index:end_index]
            node = struct.unpack(node_fmt, node_blob)
            node_tag = node[0]
            node_spec['nodes'].append(decode_node(node_tag, node_blob))
            if len(node_spec['nodes']) == alloc_items:
                i = len(map_pages)
                break
    return node_spec

def decode_orders_vec(vec_data, pages):
    header_size = vec_data['header_size']
    offset_size = vec_data['offset_size']
    alloc_items = vec_data['alloc_items']
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
        for order_idx in range(inst_per_page):
            start_index = order_idx * order_size
            end_index = start_index + order_size
            order = struct.unpack(order_fmt, res[3][start_index:end_index])
            order_spec['orders'].append({
                'amount': order[0],
                'expiry': order[1],
            })
            if len(order_spec['orders']) == alloc_items:
                i = len(vec_pages)
                break
    return order_spec

def decode_orderbook_side(side, map_data, vec_data):
    book = []
    for i in range(len(map_data['nodes'])):
        node = map_data['nodes'][i]
        if node and node['tag'] == 2:
            order = vec_data['orders'][node['slot']]
            order_item = {
                'type': side,
                'key': node['key'],
                'price': node['price'],
                'owner': node['owner'],
                'amount': order['amount'],
                'expiry': order['expiry'],
            }
            book.append(order_item)
    return book

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
    bid_map_data = decode_orders_map(bid_map, pages)
    ask_map_data = decode_orders_map(ask_map, pages)
    bid_vec_data = decode_orders_vec(bid_vec, pages)
    ask_vec_data = decode_orders_vec(ask_vec, pages)
    bids = decode_orderbook_side('bid', bid_map_data, bid_vec_data)
    asks = decode_orderbook_side('ask', ask_map_data, ask_vec_data)
    return {
        'bids': bids,
        'asks': asks,
    }

def decode_settlement_map(map_data, pages):
    header_size = map_data['header_size']
    offset_size = map_data['offset_size']
    alloc_items = map_data['alloc_items']
    inst_per_page = math.floor((16384 - (header_size + offset_size)) / 56)
    vector_fmt = "<{}s2Q2IQ{}s".format(offset_size, 16384 - (offset_size + 32))
    node_fmt = "<I52s"
    node_size = struct.calcsize(node_fmt)
    total_pages = math.floor(alloc_items / inst_per_page)
    if (alloc_items % inst_per_page) != 0:
        total_pages = total_pages + 1
    map_pages = []
    for i in range(total_pages):
        pidx = map_data['alloc_pages'][i]
        map_pages.append(pages[pidx])
    node_spec = {'nodes': []}
    for i in range(len(map_pages)):
        res = struct.unpack(vector_fmt, map_pages[i])
        if i == 0:
            node_spec['bump_index'] = res[1]
            node_spec['free_list_len'] = res[2]
            node_spec['free_list_head'] = res[3]
            node_spec['root_node'] = res[4]
            node_spec['leaf_count'] = res[5]
        for node_idx in range(inst_per_page):
            start_index = node_idx * node_size
            end_index = start_index + node_size
            node_blob = res[6][start_index:end_index]
            node = struct.unpack(node_fmt, node_blob)
            node_tag = node[0]
            node_spec['nodes'].append(decode_node(node_tag, node_blob))
            if len(node_spec['nodes']) == alloc_items:
                i = len(map_pages)
                break
    return node_spec

def decode_settlement_vec(vec_data, pages):
    header_size = vec_data['header_size']
    offset_size = vec_data['offset_size']
    alloc_items = vec_data['alloc_items']
    inst_per_page = math.floor((16384 - (header_size + offset_size)) / 24)
    vector_fmt = "<{}s2I{}s".format(offset_size, 16384 - (offset_size + 8))
    entry_fmt = "<QQq"
    entry_size = struct.calcsize(entry_fmt)
    total_pages = math.floor(alloc_items / inst_per_page)
    if (alloc_items % inst_per_page) != 0:
        total_pages = total_pages + 1
    vec_pages = []
    for i in range(total_pages):
        pidx = vec_data['alloc_pages'][i]
        vec_pages.append(pages[pidx])
    entry_spec = {'entries': []}
    for i in range(len(vec_pages)):
        res = struct.unpack(vector_fmt, vec_pages[i])
        if i == 0:
            entry_spec['free_top'] = res[1]
            entry_spec['next_index'] = res[2]
        for entry_idx in range(inst_per_page):
            start_index = entry_idx * entry_size
            end_index = start_index + entry_size
            entry = struct.unpack(entry_fmt, res[3][start_index:end_index])
            entry_spec['entries'].append({
                'mkt_token_balance': entry[0],
                'prc_token_balance': entry[1],
                'ts_updated': entry[2],
            })
            if len(entry_spec['entries']) == alloc_items:
                i = len(vec_pages)
                break
    return entry_spec

def decode_settlement_log(settle_data, user_wallet=None):
    outer_fmt = "<32s32s32sIH{}s".format(len(settle_data) - (32 + 32 + 32 + 4 + 2))
    inner_fmt = "<3Q16H"
    inner_size = struct.calcsize(inner_fmt)
    page_fmt = "<{}s".format(16384 * 6)
    # Unpack the outer struct
    outer_unpacked = struct.unpack(outer_fmt, settle_data)
    # Unpack the inner structs from the outer struct
    type_page = []
    for i in range(4):
        start_index = i * inner_size
        end_index = start_index + inner_size
        type_data = struct.unpack(inner_fmt, outer_unpacked[5][start_index:end_index])
        type_page.append({
            'header_size': type_data[0],
            'offset_size': type_data[1],
            'alloc_items': type_data[2],
            'alloc_pages': type_data[3:],
        })
    pages = []
    page_data = outer_unpacked[5][end_index:]
    for i in range(6):
        start_index = i * 16384
        end_index = start_index + 16384
        pages.append(page_data[start_index:end_index])
    result = {
        'header': {
            'market': Pubkey(outer_unpacked[0]),
            'prev': Pubkey(outer_unpacked[1]),
            'next': Pubkey(outer_unpacked[2]),
        },
    }
    settle_map = type_page[0]
    settle_vec = type_page[1]
    map_data = decode_settlement_map(settle_map, pages)
    vec_data = decode_settlement_vec(settle_vec, pages)
    entries = []
    for i in range(len(map_data['nodes'])):
        node = map_data['nodes'][i]
        if node and node['tag'] == 2:
            entry = vec_data['entries'][node['slot']]
            if user_wallet is None or (user_wallet is not None and user_wallet == node['owner']):
                entry_item = {
                    'owner': node['owner'],
                    'mkt_token_balance': entry['mkt_token_balance'],
                    'prc_token_balance': entry['prc_token_balance'],
                }
                entries.append(entry_item)
    result['entries'] = entries
    return result

async def main():
    client = AsyncClient('https://api.mainnet-beta.solana.com')
    provider = Provider(client, Wallet.local())
    # load the Serum Swap Program (not the Serum dex itself).
    program_id = Pubkey.from_string('AQUA3y76EwUE2CgxbaMUMpa54G8PyGRExRdhLK8bN4VR')
    program = get_program(program_id, provider, 'idl/aqua_dex.json')
    #print(f'Wallet: {provider.wallet.public_key}')
    #market_data = get_market('market_1.json')
    #print(market_data)
    market = await Market.fetch(client, Pubkey.from_string('H9ZWkoB6FVDM7BFaxFAtvAdmMSzFmumaGTMzunQoLMYK'))
    #print(market.to_json())
    market_spec = market.to_json()
    resp = await client.get_account_info(Pubkey.from_string(market_spec['orders']))
    #print(resp.value.data)
    print(decode_orderbook(resp.value.data))
    #resp = await client.get_account_info(Pubkey.from_string(market_data['settle1']))
    #print(decode_settlement_log(base64.b64decode(resp['result']['value']['data'][0])))
    #print(base64.b64decode(resp['result']['value']['data'][0]))
    await program.close()

asyncio.run(main())
