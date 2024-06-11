import os.path
import unittest

from finite_state_machines import FSM


class TestFSM(unittest.TestCase):
    def setUp(self):
        self.json_file_path = 'tmp_test_fsm.json'
        self.fsm = FSM(
            alphabet='SL',
            states=['Q0', 'S1', 'S2', 'S3', 'S4', 'L1', 'L2', 'L3', 'L4'],
            initial_state='Q0',
            transition_mapping={
                'Q0': {'S': 'S1', 'L': 'L1'},
                'S1': {'S': 'S2', 'L': 'L1'},
                'S2': {'S': 'S3', 'L': 'L1'},
                'S3': {'S': 'S4', 'L': 'L1'},
                'S4': {'S': 'S4', 'L': 'L1'},
                'L1': {'S': 'S1', 'L': 'L2'},
                'L2': {'S': 'S1', 'L': 'L3'},
                'L3': {'S': 'S1', 'L': 'L4'},
                'L4': {'S': 'S1', 'L': 'L4'},
            },
            outputs={
                'S3': 'Error! Too many Strawberry lollipops!',
                'L3': 'Error! Too many Lemon lollipops!',
            },
        )

    def tearDown(self):
        if os.path.exists(self.json_file_path):
            os.remove(self.json_file_path)

    def test_initial_state(self):
        self.assertEqual(self.fsm.current_state, 'Q0')
        self.assertIsNone(self.fsm.current_output)

    def test_valid_transition(self):
        self.fsm.transition('S')
        self.assertEqual(self.fsm.current_state, 'S1')
        self.fsm.transition('S')
        self.assertEqual(self.fsm.current_state, 'S2')
        self.fsm.transition('S')
        self.assertEqual(self.fsm.current_state, 'S3')
        self.assertEqual(self.fsm.current_output, 'Error! Too many Strawberry lollipops!')

    def test_invalid_transition(self):
        with self.assertRaises(ValueError):
            self.fsm.transition('X')

    def test_transition_without_defined_output(self):
        self.fsm.transition('S')
        self.fsm.transition('L')
        self.assertEqual(self.fsm.current_state, 'L1')
        self.assertIsNone(self.fsm.current_output)

    def test_run(self):
        inputs = 'SLS'
        outputs = list(self.fsm.run(inputs))
        self.assertEqual(outputs, [None, None, None])

    def test_reset(self):
        self.fsm.transition('S')
        self.assertEqual(self.fsm.current_state, 'S1')
        self.fsm.reset()
        self.assertEqual(self.fsm.current_state, 'Q0')

    def test_empty_alphabet(self):
        with self.assertRaises(ValueError):
            FSM(alphabet='', states=['Q0'], initial_state='Q0', transition_mapping={'Q0': {'S': 'S1'}}, outputs={})

    def test_non_unique_alphabet(self):
        with self.assertRaises(ValueError):
            FSM(alphabet='SS', states=['Q0'], initial_state='Q0', transition_mapping={'Q0': {'S': 'S1'}}, outputs={})

    def test_empty_states(self):
        with self.assertRaises(ValueError):
            FSM(alphabet='S', states=[], initial_state='Q0', transition_mapping={'Q0': {'S': 'S1'}}, outputs={})

    def test_non_unique_states(self):
        with self.assertRaises(ValueError):
            FSM(alphabet='S', states='QQQQ', initial_state='Q', transition_mapping={'Q': {'S': 'S1'}}, outputs={})

    def test_copy(self):
        self.fsm.transition('S')
        self.assertEqual(self.fsm.current_state, 'S1')
        fsm_copy = self.fsm.copy()
        self.assertIsInstance(fsm_copy, FSM)
        self.assertIsNot(fsm_copy, self.fsm)
        self.assertEqual(fsm_copy.transition_mapping, self.fsm.transition_mapping)
        self.assertIsNot(fsm_copy.transition_mapping, self.fsm.transition_mapping)
        self.assertEqual(fsm_copy.current_state, 'S1')
        fsm_copy.transition('S')
        self.assertEqual(fsm_copy.current_state, 'S2')

    def test_empty_transition_mapping(self):
        with self.assertRaises(ValueError):
            FSM(
                alphabet='S',
                states=['Q0', 'S1'],
                initial_state='Q0',
                transition_mapping={},
                outputs={},
                ensure_transition_completeness=True,
            )

    def test_transition_mapping_missing_some_states(self):
        with self.assertRaises(ValueError):
            FSM(
                alphabet='S',
                states=['Q0', 'S1'],
                initial_state='Q0',
                transition_mapping={'Q0': {'S': 'S1'}},
                outputs={},
                ensure_transition_completeness=True,
            )

    def test_transition_mapping_missing_some_inputs(self):
        with self.assertRaises(ValueError):
            FSM(
                alphabet='SL',
                states=['Q0', 'S1'],
                initial_state='Q0',
                transition_mapping={
                    'Q0': {'S': 'S1', 'L': 'Q0'},
                    'S1': {'S': 'S1'},
                },
                outputs={},
                ensure_transition_completeness=True,
            )

    def test_to_dict(self):
        basic_fsm = FSM(alphabet='A', states='0', initial_state='0', transition_mapping={'0': {'A': '0'}}, outputs={})
        expected_dict = {
            'alphabet': ['A'],
            'states': ['0'],
            'initial_state': '0',
            'current_state': '0',
            'transition_mapping': {'0': {'A': '0'}},
            'outputs': {},
        }
        got_dict = basic_fsm.to_dict()
        self.assertEqual(expected_dict, got_dict)

    def test_repr(self):
        self.fsm.transition('L')
        expected_repr = (
            "FSM(alphabet=['S', 'L'], states=['Q0', 'S1', 'S2', 'S3', 'S4', 'L1', 'L2', 'L3', 'L4'], "
            + "initial_state='Q0', current_state='L1', transition_mapping={'Q0': {'S': 'S1', 'L': 'L1'}, "
            + "'S1': {'S': 'S2', 'L': 'L1'}, 'S2': {'S': 'S3', 'L': 'L1'}, 'S3': {'S': 'S4', 'L': 'L1'}, "
            + "'S4': {'S': 'S4', 'L': 'L1'}, 'L1': {'S': 'S1', 'L': 'L2'}, 'L2': {'S': 'S1', 'L': 'L3'}, "
            + "'L3': {'S': 'S1', 'L': 'L4'}, 'L4': {'S': 'S1', 'L': 'L4'}}, "
            + "outputs={'S3': 'Error! Too many Strawberry lollipops!', 'L3': 'Error! Too many Lemon lollipops!'})"
        )
        got_repr = repr(self.fsm)
        self.assertEqual(expected_repr, got_repr)


if __name__ == '__main__':
    unittest.main()
