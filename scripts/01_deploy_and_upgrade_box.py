from scripts.util import get_account, encode_function_data, upgrade
from brownie import (
    network,
    Box,
    BoxV2,
    ProxyAdmin,
    Contract,
    TransparentUpgradeableProxy,
    BoxV2,
)


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}.")
    box = Box.deploy(
        {"from": account},
        publish_source=True,
    )
    print(box.retrieve())

    proxy_admin = ProxyAdmin.deploy(
        {"from": account},
        publish_source=True,
    )

    # initializer = box.store, 1
    box_encoded_intializer_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_intializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=True,
    )

    print(f"Proxy deployed to {proxy}. You can now upgrade to v2!")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    tx = proxy_box.store(1, {"from": account})
    tx.wait(1)

    print(proxy_box.retrieve())
    box_v2 = BoxV2.deploy(
        {"from": account},
        publish_source=True,
    )
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)

    tx = proxy_box.increment({"from": account})
    tx.wait(1)
    print(proxy_box.retrieve())
