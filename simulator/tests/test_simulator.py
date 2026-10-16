import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

SCRIPT = Path(__file__).resolve().parents[1] / 'single_device_simulator.py'

def load(index, directory):
    with patch.dict(os.environ, {'NODE_INDEX': str(index), 'STATE_DIR': directory}, clear=False):
        spec = importlib.util.spec_from_file_location('station_simulator', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

class SimulatorTests(unittest.TestCase):
    def test_identity_and_token_survive_recreation(self):
        with tempfile.TemporaryDirectory() as state:
            first = load(0, state)
            first.save_token('test-credential')
            recreated = load(0, state)
            self.assertEqual(recreated.DEVICE_NAME, 'VN-HCM-001')
            self.assertEqual(recreated.load_token(), 'test-credential')
            self.assertEqual(load(49, state).DEVICE_NAME, 'VN-HCM-050')
            self.assertIsNone(load(1, state).load_token())

    def test_all_replicas_have_unique_fixed_stations(self):
        with tempfile.TemporaryDirectory() as state:
            modules = [load(index, state) for index in range(50)]
            self.assertEqual(len({m.DEVICE_NAME for m in modules}), 50)
            self.assertEqual([m.assigned_station['node_num'] for m in modules], list(range(1, 51)))

    def test_publish_failure_is_not_reported_as_success_and_client_stops(self):
        with tempfile.TemporaryDirectory() as state:
            module = load(0, state)
            client = MagicMock()
            client.loop_start.side_effect = lambda: client.on_connect(client, None, {}, 0)
            client.publish.return_value.rc = 4
            with patch.object(module.mqtt, 'Client', return_value=client), patch('builtins.print'):
                with self.assertRaisesRegex(RuntimeError, 'publish'):
                    module.run_simulation('test')
            client.disconnect.assert_called_once()
            client.loop_stop.assert_called_once()

if __name__ == '__main__': unittest.main()
