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


if __name__ == '__main__':
    solve_toy_problem_with_fsm(
        example_inputs='SLSLSLSSLLSSLLSSSLLLSSSSLLLLSSSSSSSS',
        on_output=print,
        verbose=True,
    )
