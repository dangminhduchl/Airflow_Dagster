from dagster import Definitions, load_assets_from_modules, load_asset_checks_from_modules

try:
    from invoice_processing import assets as invoice_assets
except ImportError:
    from dagster_demo.invoice_processing import assets as invoice_assets

all_assets = load_assets_from_modules([invoice_assets])
all_checks = load_asset_checks_from_modules([invoice_assets])

defs = Definitions(
    assets=all_assets,
    asset_checks=all_checks,
)
