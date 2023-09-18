from tonsdk.utils import Address, bytes_to_b64str
from tonsdk.boc import Cell, begin_cell
from typing import Union, Type
from .pool_type import PoolType
from ..common.asset import Asset
from ...jettons import JettonWallet
from ....api import Provider

class Pool:
    def __init__(
        address: Union[Address, str]
    ):
        self.address = Address(address) if type(address) == str else address
    
    @staticmethod
    def create_from_address(address: Union[Address, str]) -> Type["Pool"]:
        return Pool(address)
    
    async def get_pool_type(provider: Provider) -> PoolType:
        stack = await provider.runGetMethod(address=self.address,
                                            method="is_stable")
        return stack[0]["value"]
    
    async def get_assets(provider: Provider) -> [Asset, Asset]:
        stack = await provider.runGetMethod(address=self.address,
                                            method="get_assets")
        return [
            Asset.from_slice(stack[0]["value"].begin_parse()),
            Asset.from_slice(stack[1]["value"].begin_parse())
        ]
    
    async def get_estimated_swap_out(
        asset_in: Asset,
        amount_in: int,
        provider: Provider
    ) -> list:
        stack = await provider.runGetMethod(address=self.address,
                                            method="estimate_swap_out",
                                            stack=[
                                                [
                                                    "tvm.Slice",
                                                    bytes_to_b64str(asset_in.to_slice().to_boc())
                                                ],
                                                [
                                                    "int",
                                                    str(amount_in)
                                                ]
                                            ])
        return {
            "asset_out": Asset.from_slice(stack[0]["result"]),
            "amount_out": stack[1]["result"],
            "trade_fee": stack[2]["result"]
        }
    
    async def get_estimate_deposit_out(
        amounts: [int, int],
        provider: Provider
    ) -> list:
        stack = await provider.runGetMethod(address=self.address,
                                            method="estimate_swap_out",
                                            stack=[
                                                [
                                                    "int",
                                                    str(amounts[0])
                                                ],
                                                [
                                                    "int",
                                                    str(amounts[1])
                                                ]
                                            ])
        
        return {
            "deposits": [stack[0]["value"], stack[1]["value"]],
            "fair_supply": stack[2]["value"]
        }
    
    async def get_reserves(provider: Provider) -> list:
        stack = await provider.runGetMethod(address=self.address,
                                            method="get_reserves")
        return [stack[0]["value"], stack[1]["value"]]
    
    async def get_trade_fee(provider: Provider) -> int:
        stack = await provider.runGetMethod(address=self.address,
                                            method="get_trade_fee")

        numerator = stack[0]["value"]
        denominator = stack[1]["value"]

        return numerator / denominator

    async def get_wallet_address(owner_address: Address, provider: Provider) -> Address:
        stack = await provider.runGetMethod(address=self.address,
                                            method="get_wallet_address",
                                            stack=[[
                                                "tvm.Slice",
                                                bytes_to_b64str(begin_cell().store_address(owner_address).end_cell().to_boc())
                                            ]])
        return stack[0].read_msg_addr()

    async def get_wallet(owner_address: Address, provider: Provider) -> JettonWallet:
        return JettonWallet.create_from_address(await self.get_wallet_address(owner_address, provider))