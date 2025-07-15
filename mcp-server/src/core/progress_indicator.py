"""
Progress indicator utilities for long-running operations
"""

import asyncio
import time
from typing import Optional, AsyncIterator, Callable, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ProgressStatus(Enum):
    """Progress status types"""
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ProgressUpdate:
    """Progress update information"""
    current: int
    total: int
    status: ProgressStatus
    message: str
    elapsed_time: float
    estimated_remaining: Optional[float] = None
    
    @property
    def percentage(self) -> float:
        """Calculate percentage complete"""
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100
    
    @property
    def progress_bar(self) -> str:
        """Generate a text progress bar"""
        bar_length = 20
        filled_length = int(bar_length * self.current / self.total) if self.total > 0 else 0
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        return f"[{bar}] {self.percentage:.1f}%"

class ProgressIndicator:
    """Progress indicator for long-running operations"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.description = description
        self.current = 0
        self.status = ProgressStatus.STARTING
        self.start_time = time.time()
        self.update_callbacks: list[Callable[[ProgressUpdate], None]] = []
        self.cancelled = False
        
    def add_callback(self, callback: Callable[[ProgressUpdate], None]) -> None:
        """Add a callback to be called on progress updates"""
        self.update_callbacks.append(callback)
    
    def update(self, increment: int = 1, message: str = "") -> None:
        """Update progress"""
        if self.cancelled:
            return
            
        self.current = min(self.current + increment, self.total)
        
        if self.current >= self.total:
            self.status = ProgressStatus.COMPLETED
        elif self.current > 0:
            self.status = ProgressStatus.IN_PROGRESS
        
        elapsed_time = time.time() - self.start_time
        
        # Estimate remaining time
        estimated_remaining = None
        if self.current > 0 and self.status == ProgressStatus.IN_PROGRESS:
            rate = self.current / elapsed_time
            remaining_items = self.total - self.current
            estimated_remaining = remaining_items / rate if rate > 0 else None
        
        # Create progress update
        progress_update = ProgressUpdate(
            current=self.current,
            total=self.total,
            status=self.status,
            message=message or f"{self.description}: {self.current}/{self.total}",
            elapsed_time=elapsed_time,
            estimated_remaining=estimated_remaining
        )
        
        # Call callbacks
        for callback in self.update_callbacks:
            try:
                callback(progress_update)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")
    
    def complete(self, message: str = "Complete") -> None:
        """Mark operation as complete"""
        self.current = self.total
        self.status = ProgressStatus.COMPLETED
        self.update(0, message)
    
    def fail(self, message: str = "Failed") -> None:
        """Mark operation as failed"""
        self.status = ProgressStatus.FAILED
        self.update(0, message)
    
    def cancel(self) -> None:
        """Cancel the operation"""
        self.cancelled = True
        self.status = ProgressStatus.CANCELLED
        self.update(0, "Cancelled")
    
    def is_complete(self) -> bool:
        """Check if operation is complete"""
        return self.status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED, ProgressStatus.CANCELLED]

class AsyncProgressIndicator:
    """Async progress indicator for long-running operations"""
    
    def __init__(self, total: int, description: str = "Processing", update_interval: float = 0.1):
        self.indicator = ProgressIndicator(total, description)
        self.update_interval = update_interval
        self._update_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the progress indicator"""
        self._update_task = asyncio.create_task(self._update_loop())
    
    async def stop(self) -> None:
        """Stop the progress indicator"""
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
    
    async def _update_loop(self) -> None:
        """Update loop for continuous progress updates"""
        while not self.indicator.is_complete():
            await asyncio.sleep(self.update_interval)
            # The indicator will be updated by the actual operation
    
    def update(self, increment: int = 1, message: str = "") -> None:
        """Update progress"""
        self.indicator.update(increment, message)
    
    def complete(self, message: str = "Complete") -> None:
        """Mark operation as complete"""
        self.indicator.complete(message)
    
    def fail(self, message: str = "Failed") -> None:
        """Mark operation as failed"""
        self.indicator.fail(message)
    
    def cancel(self) -> None:
        """Cancel the operation"""
        self.indicator.cancel()
    
    def add_callback(self, callback: Callable[[ProgressUpdate], None]) -> None:
        """Add a callback to be called on progress updates"""
        self.indicator.add_callback(callback)
    
    @property
    def current_progress(self) -> ProgressUpdate:
        """Get current progress"""
        return ProgressUpdate(
            current=self.indicator.current,
            total=self.indicator.total,
            status=self.indicator.status,
            message=f"{self.indicator.description}: {self.indicator.current}/{self.indicator.total}",
            elapsed_time=time.time() - self.indicator.start_time
        )

def progress_callback_logger(update: ProgressUpdate) -> None:
    """Logger callback for progress updates"""
    logger.info(f"Progress: {update.progress_bar} {update.message}")

def progress_callback_user_friendly(update: ProgressUpdate) -> str:
    """User-friendly progress message"""
    elapsed_str = f"{update.elapsed_time:.1f}s"
    
    if update.estimated_remaining:
        remaining_str = f"残り約{update.estimated_remaining:.1f}s"
    else:
        remaining_str = "残り時間不明"
    
    status_messages = {
        ProgressStatus.STARTING: "開始中...",
        ProgressStatus.IN_PROGRESS: f"実行中 ({update.percentage:.1f}%)",
        ProgressStatus.COMPLETED: "完了",
        ProgressStatus.FAILED: "失敗",
        ProgressStatus.CANCELLED: "キャンセル"
    }
    
    status_msg = status_messages.get(update.status, "不明")
    
    return f"{update.progress_bar} {status_msg} | 経過時間: {elapsed_str} | {remaining_str}"

async def with_progress(
    operation: Callable[[AsyncProgressIndicator], Any],
    total: int,
    description: str = "Processing",
    show_progress: bool = True
) -> Any:
    """
    Run an operation with progress indication
    
    Args:
        operation: The operation to run
        total: Total number of items to process
        description: Description of the operation
        show_progress: Whether to show progress updates
        
    Returns:
        Result of the operation
    """
    progress = AsyncProgressIndicator(total, description)
    
    if show_progress:
        progress.add_callback(progress_callback_logger)
    
    try:
        await progress.start()
        result = await operation(progress)
        progress.complete()
        return result
    except Exception as e:
        progress.fail(f"Error: {e}")
        raise
    finally:
        await progress.stop()

# Example usage functions

async def simulate_long_operation(progress: AsyncProgressIndicator, items: int = 10) -> str:
    """Simulate a long-running operation with progress updates"""
    for i in range(items):
        # Simulate work
        await asyncio.sleep(0.1)
        
        # Update progress
        progress.update(1, f"Processing item {i+1}")
        
        # Check if cancelled
        if progress.indicator.cancelled:
            return "Operation was cancelled"
    
    return "Operation completed successfully"

async def batch_process_with_progress(
    items: list[Any],
    process_func: Callable[[Any], Any],
    description: str = "Processing items"
) -> list[Any]:
    """
    Process items in batch with progress indication
    
    Args:
        items: List of items to process
        process_func: Function to process each item
        description: Description of the operation
        
    Returns:
        List of processed results
    """
    results = []
    
    async def process_operation(progress: AsyncProgressIndicator) -> list[Any]:
        for item in items:
            if progress.indicator.cancelled:
                break
                
            try:
                result = await process_func(item) if asyncio.iscoroutinefunction(process_func) else process_func(item)
                results.append(result)
                progress.update(1, f"Processed {len(results)} items")
            except Exception as e:
                logger.error(f"Error processing item {item}: {e}")
                progress.update(1, f"Error processing item: {e}")
        
        return results
    
    return await with_progress(process_operation, len(items), description)