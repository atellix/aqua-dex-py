import json
import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from anchorpy import Program, Provider, Wallet, Context
from anchorpy.idl import Idl
from anchorpy.program.common import translate_address

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

async def main():
    client = AsyncClient("https://api.devnet.solana.com")
    provider = Provider(client, Wallet.local())
    # load the Serum Swap Program (not the Serum dex itself).
    program_id = Pubkey.from_string('AQUAvuZCFUGtSc8uQBaTXfJz3YjMUbinMeXDoDQmZLvX')
    #program = get_program(program_id, provider, 'idl/aqua_dex.json')
    program = await Program.at(program_id, provider)
    print(f'Wallet: {provider.wallet.public_key}')
    market_data = get_market('market_1.json')
    #print(market_data)
    market_agent = program_address([bytes(Pubkey.from_string(market_data['market']))], program_id)
    #print('Agent: ' + market_agent)
    market_agent_pk = Pubkey.from_string(market_agent)
    mint1 = Pubkey.from_string(market_data['tokenMint1'])
    mint2 = Pubkey.from_string(market_data['tokenMint2'])
    user_token1 = associated_token(mint1, provider.wallet.public_key)
    user_token2 = associated_token(mint2, provider.wallet.public_key)
    token_vault1 = associated_token(mint1, market_agent_pk)
    token_vault2 = associated_token(mint2, market_agent_pk)
    accounts = {
        'market': Pubkey.from_string(market_data['market']),
        'state': Pubkey.from_string(market_data['marketState']),
        'agent': market_agent_pk,
        'trade_log': Pubkey.from_string(market_data['tradeLog']),
        'user': provider.wallet.public_key,
        'user_mkt_token': Pubkey.from_string(user_token1),
        'user_prc_token': Pubkey.from_string(user_token2),
        'mkt_vault': Pubkey.from_string(token_vault1),
        'prc_vault': Pubkey.from_string(token_vault2),
        'orders': Pubkey.from_string(market_data['orders']),
        'settle_a': Pubkey.from_string(market_data['settle1']),
        'settle_b': Pubkey.from_string(market_data['settle2']),
        'result': provider.wallet.public_key,
        'spl_token_prog': SPL_TOKEN,
    }
    #print(accounts)
    print(await program.rpc['limit_bid'](
        int(10 * (10**9)),
        int(12.34 * (10**6)),
        True,
        False,
        0,
        False,
        False,
        ctx=Context(accounts=accounts)
    ))
    await program.close()

asyncio.run(main())
