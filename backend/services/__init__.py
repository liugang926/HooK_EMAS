"""
业务逻辑服务层 (Service Layer)

遵循 .cursorrules 规约:
- 所有业务逻辑（如资产折旧计算、调拨审批流）必须封装在此目录下
- View 层只负责请求/响应，禁止编写业务逻辑
"""

from .asset_service import AssetService
from .receive_service import ReceiveService
from .borrow_service import BorrowService
from .transfer_service import TransferService
from .disposal_service import DisposalService
from .maintenance_service import MaintenanceService
from .batch_service import BatchImportExportService, BatchOperationService

__all__ = [
    'AssetService',
    'ReceiveService', 
    'BorrowService',
    'TransferService',
    'DisposalService',
    'MaintenanceService',
    'BatchImportExportService',
    'BatchOperationService',
]
