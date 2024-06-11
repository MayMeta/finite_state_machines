import json
from collections.abc import Collection, Generator, Iterable, Mapping
from os import PathLike

from typing_extensions import Self  # replace typing_extensions with typing after upgrading python to 3.11


class BaseFSM:
    """Base class for all Finite-State Machines.

    https://en.wikipedia.org/wiki/Finite-state_machine
    """

    def __init__(
        self,
        alphabet: Collection[str],
        states: Collection[str],
        initial_state: str,
        transition_mapping: Mapping[str, Mapping[str, str]],
        on_missing_transitions: str = 'raise',
        error_state: str | None = None,
        current_state: str | None = None,
    ):
        self._alphabet = list(alphabet)
        self._states = list(states)
        self._unique_alphabet = set(self._alphabet)
        self._unique_states = set(self._states)
        if not self._alphabet or len(self._alphabet) > len(self._unique_alphabet):
            raise ValueError(f'Expected alphabet to be non-empty and contain unique elements, instead got: {alphabet}')
        if not self._states or len(self._states) > len(self._unique_states):
            raise ValueError(f'Expected alphabet to be non-empty and contain unique elements, instead got: {states}')
        if initial_state not in self._unique_states:
            raise ValueError(f'Expected initial_state to be one of {states!r}, instead got: {initial_state!r}')
        if current_state is not None and current_state not in self._unique_states:
            raise ValueError(f'Expected current_state to be None or one of {states!r}, instead got: {current_state!r}')
        self._initial_state = initial_state
        self._current_state = initial_state if current_state is None else current_state
        self._transition_mapping = {state: transitions for state, transitions in transition_mapping.items()}
        self._validate_transition_mapping()
        if on_missing_transitions == 'raise':
            self._validate_transitions_completeness()
        elif on_missing_transitions == 'go_to_error_state':
            self._add_error_state_for_missing_transitions(error_state=error_state)
        elif on_missing_transitions != 'ignore':
            raise ValueError(
                "Expected on_missing_transitions to be either 'raise', 'go_to_error_state', or 'ignore', "
                f'instead got: {on_missing_transitions!r}'
            )

    def _validate_transition_mapping(self) -> None:
        for state, state_transitions in self._transition_mapping.items():
            for input_value, target_state in state_transitions.items():
                if input_value not in self._unique_alphabet:
                    raise ValueError(
                        f'Expected each state to map inputs from the given alphabet {self._alphabet!r}, '
                        f'instead state {state!r} has a mapping for {input_value!r}'
                    )
                if target_state not in self._unique_states:
                    raise ValueError(
                        f'Expected each state to map to existing states {self._states!r}, '
                        f'instead state {state!r} has a mapping to {target_state!r}'
                    )

    def _validate_transitions_completeness(self) -> None:
        states_without_transitions = [s for s in self._unique_states if s not in self._transition_mapping]
        if states_without_transitions:
            raise ValueError(
                'Expected all states to have transition mappings, '
                f'instead could not find {states_without_transitions!r} in transition_mapping'
            )
        for state, state_transitions in self._transition_mapping.items():
            inputs_without_transitions = [inp for inp in self._unique_alphabet if inp not in state_transitions]
            if inputs_without_transitions:
                raise ValueError(
                    f'Expected state {state!r} to have transitions for all possible inputs, '
                    f'instead could not find {inputs_without_transitions!r} in state_transitions'
                )

    def _add_error_state_for_missing_transitions(self, error_state: str | None = None) -> None:
        if error_state is None:
            error_state = 'ERR'
        full_err_transitions = {inp: error_state for inp in self._alphabet}
        some_transitions_were_added = False
        for state in self._states:
            state_transitions = self._transition_mapping.get(state, {})
            if len(state_transitions) < len(self._alphabet):
                self._transition_mapping[state] = full_err_transitions | state_transitions
                some_transitions_were_added = True
        if some_transitions_were_added and error_state not in self._unique_states:
            self._states.append(error_state)
            self._unique_states.add(error_state)
            self._transition_mapping[error_state] = full_err_transitions

    @property
    def alphabet(self) -> list[str]:
        return self._alphabet

    @property
    def states(self) -> list[str]:
        return self._states

    @property
    def initial_state(self) -> str:
        return self._initial_state

    @property
    def transition_mapping(self) -> Mapping[str, Mapping[str, str]]:
        return self._transition_mapping

    @property
    def current_state(self) -> str:
        return self._current_state

    def transition(self, input_value: str) -> None:
        if input_value not in self._unique_alphabet:
            raise ValueError(
                f'Expected input_value to be a part of the alphabet {self._alphabet!r}, instead got: {input_value!r}'
            )
        current_state_transitions = self._transition_mapping.get(self._current_state, {})
        if input_value not in current_state_transitions:
            raise ValueError(
                f'A transition for input {input_value!r} from {self._current_state!r} is not defined, '
                'consider setting ensure_transition_completeness to True'
            )
        self._current_state = current_state_transitions[input_value]

    def run(self, inputs: Iterable[str]) -> None:
        for input_value in inputs:
            self.transition(input_value)

    def reset(self) -> None:
        self._current_state = self._initial_state

    def copy(self) -> Self:
        return type(self)(
            alphabet=self._alphabet,
            states=self._states,
            initial_state=self._initial_state,
            transition_mapping={
                state: {inp: target_state for inp, target_state in transitions.items()}
                for state, transitions in self._transition_mapping.items()
            },
            on_missing_transitions='ignore',
            current_state=self._current_state,
        )

    def to_dict(self) -> dict[str, str | list[str] | dict]:
        return {
            'alphabet': self._alphabet,
            'states': self._states,
            'initial_state': self._initial_state,
            'current_state': self._current_state,
            'transition_mapping': self._transition_mapping,
        }

    def to_json(self, dst: str | PathLike, **kwargs) -> None:
        dumped_dict = self.to_dict()
        with open(dst, 'w', encoding='utf8') as f:
            json.dump(dumped_dict, f, **kwargs)

    @classmethod
    def from_dict(cls, d: dict[str, str | list[str] | dict]) -> Self:
        return cls(
            alphabet=d['alphabet'],
            states=d['states'],
            initial_state=d['initial_state'],
            transition_mapping=d['transition_mapping'],
            current_state=d['current_state'],
            on_missing_transitions='ignore',
        )

    @classmethod
    def from_json(cls, src: str | PathLike) -> Self:
        with open(src, 'r', encoding='utf8') as f:
            d = json.load(f)
        return cls.from_dict(d)

    def __repr__(self) -> str:
        d = self.to_dict()
        arguments = ', '.join(f'{k!s}={v!r}' for k, v in d.items())
        return f'{self.__class__.__qualname__}({arguments})'


class AcceptorFSM(BaseFSM):
    """Acceptor Finite-State Machine implementation.

    https://en.wikipedia.org/wiki/Finite-state_machine#Acceptors
    """

    def __init__(
        self,
        alphabet: Collection[str],
        states: Collection[str],
        initial_state: str,
        transition_mapping: Mapping[str, Mapping[str, str]],
        accepting_states: Collection[str],
        on_missing_transitions: str = 'raise',
        error_state: str | None = None,
        current_state: str | None = None,
    ):
        super().__init__(
            alphabet=alphabet,
            states=states,
            initial_state=initial_state,
            transition_mapping=transition_mapping,
            on_missing_transitions=on_missing_transitions,
            error_state=error_state,
            current_state=current_state,
        )
        self._accepting_states = list(accepting_states)
        self._unique_accepting_states = set(self._accepting_states)
        if len(self._accepting_states) > len(self._unique_accepting_states):
            raise ValueError(
                f'Expected accepting_states to contain unique elements, instead got: {accepting_states}'
            )

    @property
    def accepting_states(self) -> list[str]:
        return self._accepting_states

    @property
    def is_accepting(self) -> bool:
        return self._current_state in self._unique_accepting_states

    def transition(self, input_value: str) -> bool:
        super().transition(input_value)
        return self.is_accepting

    def run(self, inputs: Iterable[str]) -> Generator[bool]:
        for input_value in inputs:
            yield self.transition(input_value)

    def copy(self) -> Self:
        return type(self)(
            alphabet=self._alphabet,
            states=self._states,
            initial_state=self._initial_state,
            transition_mapping={
                state: {inp: target_state for inp, target_state in transitions.items()}
                for state, transitions in self._transition_mapping.items()
            },
            accepting_states=self._accepting_states,
            on_missing_transitions='ignore',
            current_state=self._current_state,
        )

    def to_dict(self) -> dict[str, str | list[str] | dict]:
        return super().to_dict() | {'accepting_states': self._accepting_states}

    @classmethod
    def from_dict(cls, d: dict[str, str | list[str] | dict]) -> Self:
        return cls(
            alphabet=d['alphabet'],
            states=d['states'],
            initial_state=d['initial_state'],
            transition_mapping=d['transition_mapping'],
            accepting_states=d['accepting_states'],
            current_state=d['current_state'],
            on_missing_transitions='ignore',
        )


class MooreFSM(BaseFSM):
    """A Moore Finite-State Machine implementation.

    https://en.wikipedia.org/wiki/Moore_machine
    """

    def __init__(
        self,
        alphabet: Collection[str],
        states: Collection[str],
        initial_state: str,
        transition_mapping: Mapping[str, Mapping[str, str]],
        outputs: Mapping[str, str],
        on_missing_transitions: str = 'raise',
        error_state: str | None = None,
        current_state: str | None = None,
    ):
        super().__init__(
            alphabet=alphabet,
            states=states,
            initial_state=initial_state,
            transition_mapping=transition_mapping,
            on_missing_transitions=on_missing_transitions,
            error_state=error_state,
            current_state=current_state,
        )
        self._outputs = outputs

    @property
    def outputs(self) -> Mapping[str, str | None]:
        return self._outputs

    @property
    def current_output(self) -> str | None:
        return self._outputs.get(self._current_state)

    def transition(self, input_value: str) -> str:
        super().transition(input_value)
        return self.current_output

    def run(self, inputs: Iterable[str]) -> Generator[str]:
        for input_value in inputs:
            yield self.transition(input_value)

    def copy(self) -> Self:
        return type(self)(
            alphabet=self._alphabet,
            states=self._states,
            initial_state=self._initial_state,
            transition_mapping={
                state: {inp: target_state for inp, target_state in transitions.items()}
                for state, transitions in self._transition_mapping.items()
            },
            outputs={state: output for state, output in self._outputs.items()},
            on_missing_transitions='ignore',
            current_state=self._current_state,
        )

    def to_dict(self) -> dict[str, str | list[str] | dict]:
        return super().to_dict() | {'outputs': self._outputs}

    @classmethod
    def from_dict(cls, d: dict[str, str | list[str] | dict]) -> Self:
        return cls(
            alphabet=d['alphabet'],
            states=d['states'],
            initial_state=d['initial_state'],
            transition_mapping=d['transition_mapping'],
            outputs=d['outputs'],
            current_state=d['current_state'],
            on_missing_transitions='ignore',
        )


def streak_detector(
    alphabet: Collection[str],
    n_streak: int = 3,
    initial_state: str = 'Q0',
    below_streak_output_template: str | None = None,
    streak_output_template: str | None = '{input_value} streak detected!',
    above_streak_output_template: str | None = None,
) -> MooreFSM:
    """This helper function creates a simple MooreFSM to detect streaks (sequences of repeats) in the input stream.

    After reading some `input_value` for the first time the streak detector FSM will go to '{input_value}1' state;
    If the read `input_value` repeats, then the detector goes to '{input_value}2', '{input_value}3' and so on,
    outputting values according to `below_streak_output_template`;
    When it reaches '{input_value}{n_streak}' its output value switches to `streak_output_template`.
    After that, the detector will stay in the '{input_value}{n_streak + 1}' state,
    outputting values according to `above_streak_output_template`.

    Example:
        streak_detector(['S', 'L'], n_streak=3, streak_output_template='Error! Too many {input_value} lollipops!')
        # will create the following MooreFSM:
        MooreFSM(
            alphabet=['S', 'L'],
            states=['Q0', 'S1', 'S2', 'S3', 'S4', 'L1', 'L2', 'L3', 'L4'],
            initial_state='Q0',
            transition_mapping={
                'Q0': {'S': 'S1', 'L': 'L1'},
                'S1': {'S': 'S2', 'L': 'L1'}, 'S2': {'S': 'S3', 'L': 'L1'},
                'S3': {'S': 'S4', 'L': 'L1'}, 'S4': {'S': 'S4', 'L': 'L1'},
                'L1': {'S': 'S1', 'L': 'L2'}, 'L2': {'S': 'S1', 'L': 'L3'},
                'L3': {'S': 'S1', 'L': 'L4'}, 'L4': {'S': 'S1', 'L': 'L4'}
            },
            outputs={'S3': 'Error! Too many S lollipops!', 'L3': 'Error! Too many L lollipops!'}
        )
    """
    if not isinstance(n_streak, int) or n_streak < 1:
        raise ValueError(f'Expected n_streak to be an integer >= 1, instead got: {n_streak!r}')
    n_first, n_final = 1, n_streak + 1
    default_transitions = {input_value: f'{input_value}{n_first}' for input_value in alphabet}
    transitions = {initial_state: default_transitions.copy()}
    states = [initial_state]
    outputs = {}
    for input_value in alphabet:
        for i in range(1, n_final + 1):
            state = f'{input_value}{i}'
            next_state = f'{input_value}{min(i + 1, n_final)}'  # final state will transition to itself
            states.append(state)
            transitions[state] = default_transitions.copy()
            transitions[state][input_value] = next_state
            if below_streak_output_template and i < n_streak:
                outputs[state] = below_streak_output_template.format(input_value=input_value)
            if streak_output_template and i == n_streak:
                outputs[state] = streak_output_template.format(input_value=input_value)
            if above_streak_output_template and i > n_streak:
                outputs[state] = above_streak_output_template.format(input_value=input_value)
    res = MooreFSM(
        alphabet=alphabet,
        states=states,
        initial_state=initial_state,
        transition_mapping=transitions,
        outputs=outputs,
    )
    return res
