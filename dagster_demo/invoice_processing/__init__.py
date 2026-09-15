from dagster import Definitions, load_assets_from_modules, load_asset_checks_from_modules
from . import assets

all_invoice_assets = load_assets_from_modules([assets])
all_invoice_checks = load_asset_checks_from_modules([assets])

defs = Definitions(
    assets=all_invoice_assets,
    asset_checks=all_invoice_checks,
)
