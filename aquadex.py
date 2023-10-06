#!/usr/bin/env python3

import math
import struct
import base64
import asyncio
import krock32
from decimal import Decimal
from aquadex_client import program_id as client_program_id
from solana.transaction import Transaction
from solders.pubkey import Pubkey
from anchorpy import Program, Context, Idl
from anchorpy.program.common import translate_address
from aquadex_client.accounts import Market, MarketState
from aquadex_client.instructions import limit_bid, limit_ask, market_bid, market_ask, cancel_order, withdraw as log_withdraw, vault_withdraw

__all__ = ['AquadexMarket', 'Market']

DEFAULT_AQUADEX_PROGRAM_ID = Pubkey.from_string('AQUA3y76EwUE2CgxbaMUMpa54G8PyGRExRdhLK8bN4VR')

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

def encode_order_id(buf):
    rbuf = buf[::-1]
    encoder = krock32.Encoder(checksum=False)
    encoder.update(rbuf)
    return encoder.finalize().lower()

def decode_order_id(order_id):
    decoder = krock32.Decoder(checksum=False)
    decoder.update(order_id)
    buf = decoder.finalize()
    rbuf = buf[::-1]
    return int.from_bytes(buf, byteorder='big')

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

class AquadexOrder(object):
    def __init__(self,
        side = 'bid', # or 'ask'
        quantity = 0,
        price = 0,
        limit = True,
        post = True,
        by_quantity = True,
        net_price = None,
        fill = False,
        expires = 0,
        preview = False,
        rollover = False,
    ):
        if not(side == 'bid' or side == 'ask'):
            raise Exception('Invalid side')
        if limit:
            order_type = 'limit_' + side
        else:
            if not(by_quantity) and net_price is None:
                raise Exception('Net price not specified')
            order_type = 'market_' + side
        self.order_type = order_type
        self.quantity = quantity
        self.fill = fill
        self.preview = preview
        self.rollover = rollover
        if limit:
            self.price = price
            self.post = post
            self.expires = expires
        else:
            self.by_quantity = by_quantity
            if by_quantity:
                self.net_price = 0
            else:
                self.net_price = net_price
                self.quantity = 0

class AquadexMarket(object):
    def __init__(self, client, market_account_id):
        self.client = client
        self.market_id = market_account_id

    def format_decimals(self, amount, token):
        market_data = self.client.market[self.market_id]
        exponent = Decimal(10) ** Decimal(market_data['{}_decimals'.format(token)])
        value = Decimal(amount) * exponent
        return int(value.quantize(Decimal('1')))

    def get_decimal(self, amount, token):
        market_data = self.client.market[self.market_id]
        exponent = Decimal(10) ** Decimal(market_data['{}_decimals'.format(token)])
        value = Decimal(amount) / exponent
        return value

    async def orderbook(self, data=None):
        if data is None:
            market_data = self.client.market[self.market_id]
            resp = await self.client.async_client.get_account_info(Pubkey.from_string(market_data['orders']))
            data = resp.value.data
        book = self.client.decode_orderbook(data)
        for order in book['asks']:
            order['amount'] = self.get_decimal(order['amount'], 'mkt')
            order['price'] = self.get_decimal(order['price'], 'prc')
        for order in book['bids']:
            order['amount'] = self.get_decimal(order['amount'], 'mkt')
            order['price'] = self.get_decimal(order['price'], 'prc')
        return book

    def market_accounts(self, mode='trade'):
        market_data = self.client.market[self.market_id]
        market_state = self.client.market_state[market_data['state']]
        user_pk = self.client.provider.wallet.public_key
        mkt_mint_pk = Pubkey.from_string(market_data['mkt_mint'])
        prc_mint_pk = Pubkey.from_string(market_data['prc_mint'])
        user_mkt_token_id = associated_token(mkt_mint_pk, user_pk)
        user_prc_token_id = associated_token(prc_mint_pk, user_pk)
        result = {
            'market': Pubkey.from_string(self.market_id),
            'state': Pubkey.from_string(market_data['state']),
            'agent': Pubkey.from_string(market_data['agent']),
            'user_mkt_token': Pubkey.from_string(user_mkt_token_id),
            'user_prc_token': Pubkey.from_string(user_prc_token_id),
            'mkt_vault': Pubkey.from_string(market_data['mkt_vault']),
            'prc_vault': Pubkey.from_string(market_data['prc_vault']),
            'orders': Pubkey.from_string(market_data['orders']),
            'spl_token_prog': SPL_TOKEN,
        }
        if mode == 'trade':
            result.update({
                'user': user_pk,
                'result': user_pk,
                'trade_log': Pubkey.from_string(market_data['trade_log']),
                'settle_a': Pubkey.from_string(market_state['settle_a']),
                'settle_b': Pubkey.from_string(market_state['settle_b']),
            })
        elif mode == 'cancel':
            result.update({
                'owner': user_pk,
                'result': user_pk,
            })
        return result

    async def order(self, *order, **order_spec):
        if len(order) > 0:
            order_rec = order[0]
        else:
            order_rec = AquadexOrder(**order_spec)
        ot = order_rec.order_type
        if ot == 'limit_bid':
            ix = limit_bid({
                'inp_quantity': self.format_decimals(order_rec.quantity, 'mkt'),
                'inp_price_request': self.format_decimals(order_rec.price, 'prc'),
                'inp_post': order_rec.post,
                'inp_fill': order_rec.fill,
                'inp_expires': order_rec.expires,
                'inp_preview': order_rec.preview,
                'inp_rollover': order_rec.rollover,
            }, self.market_accounts(), program_id=self.client.program_id)
        elif ot == 'limit_ask':
            ix = limit_ask({
                'inp_quantity': self.format_decimals(order_rec.quantity, 'mkt'),
                'inp_price_request': self.format_decimals(order_rec.price, 'prc'),
                'inp_post': order_rec.post,
                'inp_fill': order_rec.fill,
                'inp_expires': order_rec.expires,
                'inp_preview': order_rec.preview,
                'inp_rollover': order_rec.rollover,
            }, self.market_accounts(), program_id=self.client.program_id)
        elif ot == 'market_bid':
            ix = market_bid({
                'inp_by_quantity': self.by_quantity,
                'inp_quantity': self.format_decimals(order_rec.quantity, 'mkt'),
                'inp_net_price': self.format_decimals(order_rec.net_price, 'prc'),
                'inp_fill': order_rec.fill,
                'inp_preview': order_rec.preview,
                'inp_rollover': order_rec.rollover,
            }, self.market_accounts(), program_id=self.client.program_id)
        elif ot == 'market_ask':
            ix = market_ask({
                'inp_by_quantity': self.by_quantity,
                'inp_quantity': self.format_decimals(order_rec.quantity, 'mkt'),
                'inp_net_price': self.format_decimals(order_rec.net_price, 'prc'),
                'inp_fill': order_rec.fill,
                'inp_preview': order_rec.preview,
                'inp_rollover': order_rec.rollover,
            }, self.market_accounts(), program_id=self.client.program_id)
        recent_blockhash = (
            await self.client.provider.connection.get_latest_blockhash('confirmed')
        ).value.blockhash
        tx = Transaction(recent_blockhash=recent_blockhash)
        tx.add(ix)
        self.client.provider.wallet.sign_transaction(tx)
        return await self.client.provider.send(tx)

    async def cancel_order(self, side, order_id):
        if side == 'bid':
            side_code = 0
        elif side == 'ask':
            side_code = 1
        else:
            raise Exception('Invalid orderbook side')
        ix = cancel_order({
            'inp_side': side_code,
            'inp_order_id': decode_order_id(order_id),
        }, self.market_accounts('cancel'), program_id=self.client.program_id)
        recent_blockhash = (
            await self.client.provider.connection.get_latest_blockhash('confirmed')
        ).value.blockhash
        tx = Transaction(recent_blockhash=recent_blockhash)
        tx.add(ix)
        self.client.provider.wallet.sign_transaction(tx)
        return await self.client.provider.send(tx)

    async def get_settlement_logs(self, user_wallet=None):
        log_data = {}
        log_seq = []
        log_entries = []
        log_item = self.client.market[self.market_id]['settle0']
        while True:
            log_resp = await self.client.async_client.get_account_info(Pubkey.from_string(log_item))
            sl = self.client.decode_settlement_log(log_resp.value.data, user_wallet)
            log_data[log_item] = sl
            for e in sl['entries']:
                prev_log = sl['header']['prev']
                next_log = sl['header']['next']
                if str(prev_log) == '11111111111111111111111111111111':
                    prev_log = Pubkey.from_string(log_item)
                if str(next_log) == '11111111111111111111111111111111':
                    next_log = Pubkey.from_string(log_item)
                log_entries.append({
                    'log': Pubkey.from_string(log_item),
                    'prev': prev_log,
                    'next': next_log,
                })
            log_seq.append(log_item)
            log_item = str(sl['header']['next'])
            if log_item == '11111111111111111111111111111111':
                break
        return {
            'entries': log_entries,
            'data': log_data,
            'logs': log_seq,
        }

    async def has_withdraw(self):
        # loop through settlement logs
        logs = await self.get_settlement_logs(user_wallet=self.client.provider.wallet.public_key)
        if len(logs['entries']) > 0:
            return logs['entries']
        # TODO: check user vault
        return None

    async def withdraw(self, log_entries=None, vault=False):
        if log_entries is None:
            logs = await self.get_settlement_logs(user_wallet=self.client.provider.wallet.public_key)
            log_entries = logs['entries']
        recent_blockhash = (
            await self.client.provider.connection.get_latest_blockhash('confirmed')
        ).value.blockhash
        tx = Transaction(recent_blockhash=recent_blockhash)
        market_data = self.client.market[self.market_id]
        market_state = self.client.market_state[market_data['state']]
        user_pk = self.client.provider.wallet.public_key
        mkt_mint_pk = Pubkey.from_string(market_data['mkt_mint'])
        prc_mint_pk = Pubkey.from_string(market_data['prc_mint'])
        user_mkt_token_id = associated_token(mkt_mint_pk, user_pk)
        user_prc_token_id = associated_token(prc_mint_pk, user_pk)
        for entry in log_entries:
            print('Withdraw from: ' + str(entry['log']))
            ix = log_withdraw({
                'market': Pubkey.from_string(self.market_id),
                'state': Pubkey.from_string(market_data['state']),
                'agent': Pubkey.from_string(market_data['agent']),
                'user_mkt_token': Pubkey.from_string(user_mkt_token_id),
                'user_prc_token': Pubkey.from_string(user_prc_token_id),
                'mkt_vault': Pubkey.from_string(market_data['mkt_vault']),
                'prc_vault': Pubkey.from_string(market_data['prc_vault']),
                'owner': user_pk,
                'settle': entry['log'],
                'settle_prev': entry['prev'],
                'settle_next': entry['next'],
                'result': user_pk,
                'spl_token_prog': SPL_TOKEN,
            }, program_id=self.client.program_id)
            tx.add(ix)
        if len(log_entries) > 0:
            self.client.provider.wallet.sign_transaction(tx)
            return await self.client.provider.send(tx)
        else:
            return None

class AquadexClient(object):
    def __init__(self, async_client, provider, program_id=None, idl_file='idl/aqua_dex.json'):
        self.async_client = async_client
        self.provider = provider
        self.idl_file = idl_file
        self.market = {}
        self.market_state = {}
        if program_id is None:
            self.program_id = DEFAULT_AQUADEX_PROGRAM_ID
        else:
            self.program_id = Pubkey.from_string(program_id)

    async def load_market(self, market_account_id, state=True):
        if market_account_id not in self.market:
            info = await self.fetch_market(market_account_id)
            self.market[market_account_id] = info.to_json()
        if state:
            await self.load_market_state(self.market[market_account_id]['state'])
        return AquadexMarket(self, market_account_id)

    async def load_market_state(self, state_account_id, refresh=False):
        if refresh or state_account_id not in self.market_state:
            info = await self.fetch_market_state(state_account_id)
            self.market_state[state_account_id] = info.to_json()
            return info
        return self.market_state[state_account_id]

    async def fetch_market(self, market_account_id):
        return await Market.fetch(self.async_client, Pubkey.from_string(market_account_id), program_id=self.program_id)

    async def fetch_market_state(self, state_account_id):
        return await MarketState.fetch(self.async_client, Pubkey.from_string(state_account_id), program_id=self.program_id)

    def decode_settlement_log(self, settle_data, user_wallet=None):
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

    def decode_orderbook(self, orders_data):
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

