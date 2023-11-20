# Standard library imports
import threading
from unittest.mock import MagicMock

# Related third party imports
import pytest

# Local application/library specific imports
from spectrostaff.broadcasting import Broadcaster, Listener

def test_receive_data():
    mock_callback = MagicMock()
    listener = Listener(mock_callback)
    test_data = "Test data"
    listener.receive_data(test_data)
    mock_callback.assert_called_once_with(test_data)

if __name__ == "__main__":
    pytest.main()