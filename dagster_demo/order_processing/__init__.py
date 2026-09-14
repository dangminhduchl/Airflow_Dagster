from dagster import (
    Definitions,
    load_assets_from_modules,
    load_asset_checks_from_modules,
    define_asset_job,
)
from . import assets_workflow
from .ops_workflow import document_processing_job

all_assets = load_assets_from_modules([assets_workflow])
all_checks = load_asset_checks_from_modules([assets_workflow])

# Tạo Job riêng cho Asset Pipeline để hiển thị trực tiếp trong tab Jobs
document_asset_job = define_asset_job(
    name="document_asset_pipeline_job",
    selection=all_assets,
    description="Job cập nhật tự động toàn bộ Document Assets (PDF -> AI Extracted -> Invoices / Contracts / eKYC / Quarantined)",
)

defs = Definitions(
    assets=all_assets,
    asset_checks=all_checks,
    jobs=[
        document_processing_job,     # Job 1: Triển khai theo Ops / Step Functions
        document_asset_job,          # Job 2: Triển khai theo Asset Pipeline
    ],
)
