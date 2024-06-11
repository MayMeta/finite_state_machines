from typing import Callable

from finite_state_machines import MooreFSM, streak_detector


def solve_toy_problem_with_fsm(example_inputs: str, on_output: Callable, verbose: bool = False):
    if verbose:
        print('creating FSM...')
    my_fsm: MooreFSM = streak_detector(
        ['S', 'L'], n_streak=3, streak_output_template='Error! Too many {input_value} lollipops!'
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


def demonstrate_recoverability(
        example_inputs: str,
        more_inputs: str,
        on_output: Callable,
        fsm_filename: str = 'toy_problem_fsm.json',
) -> None:
    my_fsm: MooreFSM = streak_detector(
        ['S', 'L'], n_streak=3, streak_output_template='Error! Too many {input_value} lollipops!'
    )
    for my_inp in example_inputs:
        my_out = my_fsm.transition(my_inp)
        my_fsm.to_json(fsm_filename)
        if my_out is not None:
            on_output(my_out)
    print('Worker stopped, deleting my_fsm...')
    del my_fsm
    print(f'Restoring from {fsm_filename!r}...')
    restored_fsm = MooreFSM.from_json(fsm_filename)
    for my_inp in more_inputs:
        my_out = restored_fsm.transition(my_inp)
        restored_fsm.to_json(fsm_filename)
        if my_out is not None:
            on_output(my_out)


if __name__ == '__main__':
    print('demonstrating streak detection:')
    solve_toy_problem_with_fsm(
        example_inputs='SLSLSLSSLLSSLLSSSLLLSSSSLLLLSSSSSSSS',
        on_output=print,
        verbose=True,
    )
    print('\ndemonstrating recoverability:')
    demonstrate_recoverability(
        example_inputs='SLSLLLS',
        more_inputs='SSLSLSLLLS',
        on_output=print,
    )
