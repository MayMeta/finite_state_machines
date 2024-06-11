from typing import Callable

from finite_state_machines import FSM


def solve_toy_problem_with_fsm(example_inputs: str, on_output: Callable, verbose: bool = False):
    if verbose:
        print('creating FSM...')
    my_fsm = FSM(
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
    if verbose:
        print(f'initial state: {my_fsm.current_state!r}, initial output: {my_fsm.current_output!r}')
    for i, my_inp in enumerate(example_inputs):
        my_out = my_fsm.transition(my_inp)
        if verbose:
            print(f'{i=}, got input {my_inp!r}, transitioned to: {my_fsm.current_state!r}, output: {my_out!r}')
        if my_out is not None:
            on_output(my_out)
    if verbose:
        print(f'final state: {my_fsm.current_state!r}, final output: {my_fsm.current_output!r}')


if __name__ == '__main__':
    solve_toy_problem_with_fsm(
        example_inputs='SLSLSLSSLLSSLLSSSLLLSSSSLLLLSSSSSSSS',
        on_output=print,
        verbose=True,
    )
