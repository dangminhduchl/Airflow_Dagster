from dagster import Definitions, load_assets_from_modules
from . import assets_workflow
from .ops_workflow import order_processing_job

all_assets = load_assets_from_modules([assets_workflow])

defs = Definitions(
    assets=all_assets,
    jobs=[order_processing_job],
)
