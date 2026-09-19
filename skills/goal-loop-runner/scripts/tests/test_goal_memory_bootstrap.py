import ctypes
from ctypes import wintypes
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from goal_memory.bootstrap import check_process_running


class WindowsLivenessTests(unittest.TestCase):
    def test_windows_probe_uses_query_handle_without_sending_a_signal(self):
        kernel = MagicMock()
        kernel.OpenProcess.return_value = 42
        def code(handle, output):
            ctypes.cast(output, ctypes.POINTER(wintypes.DWORD)).contents.value = 259
            return True
        kernel.GetExitCodeProcess.side_effect = code
        with patch('goal_memory.bootstrap.os.name', 'nt'), patch('goal_memory.bootstrap.os.kill') as kill, \
             patch.object(ctypes, 'WinDLL', return_value=kernel, create=True):
            check_process_running(123)
        kill.assert_not_called()
        kernel.OpenProcess.assert_called_once_with(0x1000, False, 123)
        kernel.CloseHandle.assert_called_once_with(42)

    def test_inaccessible_owner_is_not_treated_as_stale(self):
        kernel = MagicMock(); kernel.OpenProcess.return_value = None
        with patch('goal_memory.bootstrap.os.name', 'nt'), \
             patch.object(ctypes, 'WinDLL', return_value=kernel, create=True), \
             patch.object(ctypes, 'get_last_error', return_value=5, create=True):
            with self.assertRaises(OSError) as error: check_process_running(123)
        self.assertNotIsInstance(error.exception, ProcessLookupError)


if __name__ == '__main__': unittest.main()
