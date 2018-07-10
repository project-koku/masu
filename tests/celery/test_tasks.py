from unittest.mock import Mock, patch

from masu.celery.tasks import check_report_updates
from tests import MasuTestCase

class TestCeleryTasks(MasuTestCase):
    """Test cases for Celery tasks."""

    @patch('masu.celery.tasks.Orchestrator')
    def test_check_report_updates(self, mock_orchestrator):
        """Test that the scheduled task calls the orchestrator."""
        mock_orch = mock_orchestrator()
        check_report_updates()

        mock_orchestrator.assert_called()
        mock_orch.prepare.assert_called()
