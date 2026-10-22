import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('scheduler_generator', ROOT/'Tools/scheduler_generator.py')
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT/'Tools/system_config.json').read_text())

    def validate(self, config):
        with contextlib.redirect_stdout(io.StringIO()):
            return generator.validate_schedule(config)

    def test_default_configuration_is_valid(self):
        self.assertTrue(self.validate(self.config))

    def test_overlapping_hard_windows_are_rejected(self):
        self.config['tasks'][2]['start_tick'] = 50
        self.assertFalse(self.validate(self.config))

    def test_soft_tasks_can_overlap_hard_windows(self):
        self.config['tasks'][1]['start_tick'] = 50
        self.assertTrue(self.validate(self.config))

    def test_generator_rejects_timing_parameters_it_does_not_apply_to_the_kernel(self):
        for key in ['timeline_period','tick_rate_hz']:
            with self.subTest(key=key):
                config=copy.deepcopy(self.config)
                config[key]=2000
                self.assertFalse(self.validate(config))

    def test_invalid_task_definitions_are_rejected(self):
        for key,value in [('name','invalid-name'),('name',''),('type','OTHER'),('stack_size',0),('start_tick','zero')]:
            with self.subTest(key=key,value=value):
                config=copy.deepcopy(self.config)
                config['tasks'][0][key]=value
                self.assertFalse(self.validate(config))

    def test_duplicate_task_names_are_rejected(self):
        self.config['tasks'][1]['name']=self.config['tasks'][0]['name']
        self.assertFalse(self.validate(self.config))

    def test_output_write_failure_has_a_failing_exit_status(self):
        with tempfile.TemporaryDirectory() as temp:
            result=subprocess.run([sys.executable,str(ROOT/'Tools/scheduler_generator.py'),'-c',str(ROOT/'Tools/system_config.json'),'-o',str(Path(temp)/'missing'/'main.c')],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
