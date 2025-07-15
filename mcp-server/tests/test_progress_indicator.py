"""
Progress indicator tests
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.core.progress_indicator import (
    ProgressStatus,
    ProgressUpdate,
    ProgressIndicator,
    AsyncProgressIndicator,
    progress_callback_logger,
    progress_callback_user_friendly,
    with_progress,
    simulate_long_operation,
    batch_process_with_progress
)

class TestProgressUpdate:
    """Test ProgressUpdate class"""
    
    def test_progress_update_creation(self):
        """Test progress update creation"""
        update = ProgressUpdate(
            current=5,
            total=10,
            status=ProgressStatus.IN_PROGRESS,
            message="Processing",
            elapsed_time=10.5,
            estimated_remaining=5.2
        )
        
        assert update.current == 5
        assert update.total == 10
        assert update.status == ProgressStatus.IN_PROGRESS
        assert update.message == "Processing"
        assert update.elapsed_time == 10.5
        assert update.estimated_remaining == 5.2
    
    def test_percentage_calculation(self):
        """Test percentage calculation"""
        update = ProgressUpdate(
            current=3,
            total=10,
            status=ProgressStatus.IN_PROGRESS,
            message="Test",
            elapsed_time=5.0
        )
        
        assert update.percentage == 30.0
    
    def test_percentage_calculation_zero_total(self):
        """Test percentage calculation with zero total"""
        update = ProgressUpdate(
            current=3,
            total=0,
            status=ProgressStatus.IN_PROGRESS,
            message="Test",
            elapsed_time=5.0
        )
        
        assert update.percentage == 0.0
    
    def test_progress_bar_generation(self):
        """Test progress bar generation"""
        update = ProgressUpdate(
            current=5,
            total=10,
            status=ProgressStatus.IN_PROGRESS,
            message="Test",
            elapsed_time=5.0
        )
        
        progress_bar = update.progress_bar
        assert "[" in progress_bar
        assert "]" in progress_bar
        assert "50.0%" in progress_bar
        assert "█" in progress_bar
        assert "░" in progress_bar

class TestProgressIndicator:
    """Test ProgressIndicator class"""
    
    def test_progress_indicator_creation(self):
        """Test progress indicator creation"""
        indicator = ProgressIndicator(10, "Test Operation")
        
        assert indicator.total == 10
        assert indicator.description == "Test Operation"
        assert indicator.current == 0
        assert indicator.status == ProgressStatus.STARTING
        assert not indicator.cancelled
    
    def test_update_progress(self):
        """Test progress update"""
        indicator = ProgressIndicator(10, "Test Operation")
        callback_mock = MagicMock()
        indicator.add_callback(callback_mock)
        
        indicator.update(3, "Processing step 1")
        
        assert indicator.current == 3
        assert indicator.status == ProgressStatus.IN_PROGRESS
        callback_mock.assert_called_once()
        
        # Check callback was called with ProgressUpdate
        call_args = callback_mock.call_args[0][0]
        assert isinstance(call_args, ProgressUpdate)
        assert call_args.current == 3
        assert call_args.total == 10
        assert call_args.message == "Processing step 1"
    
    def test_update_progress_complete(self):
        """Test progress update to completion"""
        indicator = ProgressIndicator(10, "Test Operation")
        
        indicator.update(10, "Completed")
        
        assert indicator.current == 10
        assert indicator.status == ProgressStatus.COMPLETED
    
    def test_update_progress_over_total(self):
        """Test progress update over total"""
        indicator = ProgressIndicator(10, "Test Operation")
        
        indicator.update(15, "Over limit")
        
        assert indicator.current == 10  # Should be capped at total
        assert indicator.status == ProgressStatus.COMPLETED
    
    def test_complete_operation(self):
        """Test completing operation"""
        indicator = ProgressIndicator(10, "Test Operation")
        callback_mock = MagicMock()
        indicator.add_callback(callback_mock)
        
        indicator.complete("Done")
        
        assert indicator.current == 10
        assert indicator.status == ProgressStatus.COMPLETED
        callback_mock.assert_called_once()
    
    def test_fail_operation(self):
        """Test failing operation"""
        indicator = ProgressIndicator(10, "Test Operation")
        callback_mock = MagicMock()
        indicator.add_callback(callback_mock)
        
        indicator.fail("Failed")
        
        assert indicator.status == ProgressStatus.FAILED
        callback_mock.assert_called_once()
    
    def test_cancel_operation(self):
        """Test cancelling operation"""
        indicator = ProgressIndicator(10, "Test Operation")
        callback_mock = MagicMock()
        indicator.add_callback(callback_mock)
        
        indicator.cancel()
        
        assert indicator.cancelled
        assert indicator.status == ProgressStatus.CANCELLED
        callback_mock.assert_called_once()
    
    def test_update_cancelled_operation(self):
        """Test updating cancelled operation"""
        indicator = ProgressIndicator(10, "Test Operation")
        callback_mock = MagicMock()
        indicator.add_callback(callback_mock)
        
        indicator.cancel()
        callback_mock.reset_mock()
        
        indicator.update(5, "Should not update")
        
        assert indicator.current == 0  # Should not update
        callback_mock.assert_not_called()
    
    def test_is_complete(self):
        """Test is_complete method"""
        indicator = ProgressIndicator(10, "Test Operation")
        
        assert not indicator.is_complete()
        
        indicator.complete()
        assert indicator.is_complete()
        
        indicator.status = ProgressStatus.FAILED
        assert indicator.is_complete()
        
        indicator.status = ProgressStatus.CANCELLED
        assert indicator.is_complete()
    
    def test_callback_exception_handling(self):
        """Test callback exception handling"""
        indicator = ProgressIndicator(10, "Test Operation")
        
        def failing_callback(update):
            raise Exception("Callback error")
        
        indicator.add_callback(failing_callback)
        
        # Should not raise exception
        indicator.update(1, "Test")
        
        assert indicator.current == 1  # Progress should still update

class TestAsyncProgressIndicator:
    """Test AsyncProgressIndicator class"""
    
    @pytest.mark.asyncio
    async def test_async_progress_indicator_creation(self):
        """Test async progress indicator creation"""
        indicator = AsyncProgressIndicator(10, "Test Operation", 0.05)
        
        assert indicator.indicator.total == 10
        assert indicator.indicator.description == "Test Operation"
        assert indicator.update_interval == 0.05
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test starting and stopping async progress indicator"""
        indicator = AsyncProgressIndicator(10, "Test Operation", 0.01)
        
        await indicator.start()
        assert indicator._update_task is not None
        assert not indicator._update_task.done()
        
        await indicator.stop()
        assert indicator._update_task.done()
    
    @pytest.mark.asyncio
    async def test_update_async(self):
        """Test async progress update"""
        indicator = AsyncProgressIndicator(10, "Test Operation")
        callback_mock = MagicMock()
        indicator.add_callback(callback_mock)
        
        indicator.update(3, "Processing")
        
        assert indicator.indicator.current == 3
        callback_mock.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_complete_async(self):
        """Test async progress completion"""
        indicator = AsyncProgressIndicator(10, "Test Operation")
        
        indicator.complete("Done")
        
        assert indicator.indicator.current == 10
        assert indicator.indicator.status == ProgressStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_current_progress(self):
        """Test getting current progress"""
        indicator = AsyncProgressIndicator(10, "Test Operation")
        
        indicator.update(5, "Halfway")
        
        current = indicator.current_progress
        assert isinstance(current, ProgressUpdate)
        assert current.current == 5
        assert current.total == 10
        assert current.status == ProgressStatus.IN_PROGRESS

class TestProgressCallbacks:
    """Test progress callback functions"""
    
    @patch('src.core.progress_indicator.logger')
    def test_progress_callback_logger(self, mock_logger):
        """Test logger progress callback"""
        update = ProgressUpdate(
            current=5,
            total=10,
            status=ProgressStatus.IN_PROGRESS,
            message="Processing",
            elapsed_time=10.0
        )
        
        progress_callback_logger(update)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "Progress:" in call_args
        assert "Processing" in call_args
    
    def test_progress_callback_user_friendly(self):
        """Test user-friendly progress callback"""
        update = ProgressUpdate(
            current=5,
            total=10,
            status=ProgressStatus.IN_PROGRESS,
            message="Processing",
            elapsed_time=10.5,
            estimated_remaining=5.2
        )
        
        message = progress_callback_user_friendly(update)
        
        assert "実行中 (50.0%)" in message
        assert "経過時間: 10.5s" in message
        assert "残り約5.2s" in message
        assert "[" in message  # Progress bar
    
    def test_progress_callback_user_friendly_no_remaining(self):
        """Test user-friendly progress callback without remaining time"""
        update = ProgressUpdate(
            current=3,
            total=10,
            status=ProgressStatus.IN_PROGRESS,
            message="Processing",
            elapsed_time=5.0
        )
        
        message = progress_callback_user_friendly(update)
        
        assert "実行中 (30.0%)" in message
        assert "経過時間: 5.0s" in message
        assert "残り時間不明" in message
    
    def test_progress_callback_user_friendly_completed(self):
        """Test user-friendly progress callback for completed status"""
        update = ProgressUpdate(
            current=10,
            total=10,
            status=ProgressStatus.COMPLETED,
            message="Done",
            elapsed_time=15.0
        )
        
        message = progress_callback_user_friendly(update)
        
        assert "完了" in message
        assert "経過時間: 15.0s" in message

class TestWithProgress:
    """Test with_progress function"""
    
    @pytest.mark.asyncio
    async def test_with_progress_success(self):
        """Test with_progress with successful operation"""
        async def test_operation(progress: AsyncProgressIndicator):
            progress.update(1, "Step 1")
            await asyncio.sleep(0.01)
            progress.update(1, "Step 2")
            return "Success"
        
        result = await with_progress(test_operation, 2, "Test Operation", False)
        
        assert result == "Success"
    
    @pytest.mark.asyncio
    async def test_with_progress_failure(self):
        """Test with_progress with failing operation"""
        async def failing_operation(progress: AsyncProgressIndicator):
            progress.update(1, "Step 1")
            raise Exception("Operation failed")
        
        with pytest.raises(Exception, match="Operation failed"):
            await with_progress(failing_operation, 2, "Test Operation", False)
    
    @pytest.mark.asyncio
    async def test_with_progress_show_progress(self):
        """Test with_progress with show_progress=True"""
        async def test_operation(progress: AsyncProgressIndicator):
            progress.update(1, "Step 1")
            return "Success"
        
        with patch('src.core.progress_indicator.progress_callback_logger') as mock_callback:
            result = await with_progress(test_operation, 1, "Test Operation", True)
            
            assert result == "Success"
            # Note: callback might not be called due to timing in tests

class TestSimulateLongOperation:
    """Test simulate_long_operation function"""
    
    @pytest.mark.asyncio
    async def test_simulate_long_operation(self):
        """Test simulate_long_operation"""
        progress = AsyncProgressIndicator(3, "Test")
        
        result = await simulate_long_operation(progress, 3)
        
        assert result == "Operation completed successfully"
        assert progress.indicator.current == 3
    
    @pytest.mark.asyncio
    async def test_simulate_long_operation_cancelled(self):
        """Test simulate_long_operation with cancellation"""
        progress = AsyncProgressIndicator(10, "Test")
        
        # Cancel after starting
        progress.cancel()
        
        result = await simulate_long_operation(progress, 10)
        
        assert result == "Operation was cancelled"

class TestBatchProcessWithProgress:
    """Test batch_process_with_progress function"""
    
    @pytest.mark.asyncio
    async def test_batch_process_with_progress_sync(self):
        """Test batch processing with sync function"""
        items = [1, 2, 3, 4, 5]
        
        def process_func(item):
            return item * 2
        
        results = await batch_process_with_progress(items, process_func, "Processing")
        
        assert results == [2, 4, 6, 8, 10]
    
    @pytest.mark.asyncio
    async def test_batch_process_with_progress_async(self):
        """Test batch processing with async function"""
        items = [1, 2, 3]
        
        async def async_process_func(item):
            await asyncio.sleep(0.001)
            return item * 3
        
        results = await batch_process_with_progress(items, async_process_func, "Processing")
        
        assert results == [3, 6, 9]
    
    @pytest.mark.asyncio
    async def test_batch_process_with_progress_error(self):
        """Test batch processing with error in processing"""
        items = [1, 2, 3, 4, 5]
        
        def failing_process_func(item):
            if item == 3:
                raise Exception("Processing error")
            return item * 2
        
        with patch('src.core.progress_indicator.logger') as mock_logger:
            results = await batch_process_with_progress(items, failing_process_func, "Processing")
            
            # Should process other items despite error
            assert len(results) == 4  # 5 items - 1 error
            assert 2 in results  # 1 * 2
            assert 4 in results  # 2 * 2
            assert 8 in results  # 4 * 2
            assert 10 in results  # 5 * 2
            
            # Should log error
            mock_logger.error.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])