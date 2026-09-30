"""Regression checks that require neither private data nor model downloads."""
import ast
import contextlib
import dataclasses
import io
import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FOLLOWUP = ROOT / 'notebooks/sequential_binary_followup_experiments.ipynb'


def cells(path=FOLLOWUP):
    return json.loads(path.read_text(encoding='utf-8'))['cells']


def configuration(smoke):
    sources = [''.join(c['source']) for c in cells() if c['cell_type'] == 'code']
    settings = next(s for s in sources if 'LR_TUNING_VALUES =' in s)
    assignments = []
    for node in ast.parse(settings).body:
        if isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if 'THRESHOLDS' in names:
                continue  # numpy grid is unrelated to stage construction
            if 'SMOKE_TEST' in names:
                node.value = ast.Constant(smoke)
            assignments.append(node)
    ns = {'dataclass': dataclasses.dataclass, 'asdict': dataclasses.asdict, 're': re}
    exec(compile(ast.fix_missing_locations(ast.Module(body=assignments, type_ignores=[])), '<settings>', 'exec'), ns)
    definitions = []
    for source in sources:
        for node in ast.parse(source).body:
            if isinstance(node, ast.ClassDef) and node.name in {'ExperimentConfig', 'StageConfigFactory'}:
                definitions.append(node)
            elif isinstance(node, ast.FunctionDef) and node.name in {
                'run_mode_for_config', 'make_config', 'active_validation_check_split_seeds',
                'model_capacity_configs', 'lr_tuning_configs', 'validation_check_configs',
                'esm2_150m_check_configs', 'configs_for_stage',
            }:
                definitions.append(node)
    module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0)] + definitions, type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), '<factories>', 'exec'), ns)
    return ns


class NotebookChecks(unittest.TestCase):
    def test_code_cells_compile(self):
        for path in (ROOT / 'notebooks').glob('*.ipynb'):
            for i, cell in enumerate(cells(path)):
                if cell['cell_type'] == 'code':
                    compile(''.join(cell['source']), f'{path.name}:cell{i}', 'exec')

    def test_full_experiment_factories(self):
        ns = configuration(False)
        self.assertEqual(len(ns['configs_for_stage']('model_capacity')), 2)
        self.assertEqual([c.learning_rate for c in ns['configs_for_stage']('lr_tuning')], [1e-7, 1e-6, 1e-5])
        sensitivity = ns['configs_for_stage']('validation_check')
        self.assertEqual(len(sensitivity), 9)
        self.assertEqual({c.learning_rate for c in sensitivity}, {1e-4})
        self.assertEqual({c.epochs for c in sensitivity}, {20})
        self.assertEqual(len(ns['configs_for_stage']('all')), 14)
        optional, = ns['configs_for_stage']('esm2_150m_check')
        self.assertEqual((optional.learning_rate, optional.epochs), (1e-5, 9))
        self.assertEqual(ns['run_mode_for_config'](optional), 'frozen_150m_9_epoch')

    def test_smoke_factories(self):
        ns = configuration(True)
        self.assertFalse(ns['RUN_HELDOUT_EVALUATION'])
        self.assertEqual(ns['RUN_STAGE'], 'validation_check')
        self.assertEqual(len(ns['configs_for_stage'](ns['RUN_STAGE'])), 3)
        for stage in ['all', 'esm2_150m_check']:
            self.assertTrue(all(c.epochs == 1 for c in ns['configs_for_stage'](stage)))

    def test_drive_cell_without_colab(self):
        for path in (ROOT / 'notebooks').glob('*.ipynb'):
            source = next(''.join(c['source']) for c in cells(path) if 'from google.colab import drive' in ''.join(c['source']))
            with patch.dict(sys.modules, {'google.colab': None}), contextlib.redirect_stdout(io.StringIO()):
                exec(compile(source, '<drive-cell>', 'exec'), {})


if __name__ == '__main__':
    unittest.main()
