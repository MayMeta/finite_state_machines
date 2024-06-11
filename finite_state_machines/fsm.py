import json
from collections.abc import Collection, Generator, Iterable, Mapping
from os import PathLike

from typing_extensions import Self  # replace typing_extensions with typing after upgrading python to 3.11


class FSM:
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
        ensure_transition_completeness: bool = True,
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
        self._transition_mapping = transition_mapping
        self._outputs = outputs
        self._validate_transition_mapping()
        if ensure_transition_completeness:
            self._validate_transitions_completeness()

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
    def outputs(self) -> Mapping[str, str | None]:
        return self._outputs

    @property
    def current_state(self) -> str:
        return self._current_state

    @property
    def current_output(self) -> str | None:
        return self._outputs.get(self._current_state)

    def transition(self, input_value: str) -> str:
        if input_value not in self._unique_alphabet:
            raise ValueError(
                f'Expected input_value to be a part of the alphabet {self._alphabet}, instead got: {input_value!r}'
            )
        current_state_transitions = self._transition_mapping.get(self._current_state, {})
        if input_value not in current_state_transitions:
            raise ValueError(
                f'A transition for input {input_value!r} from {self._current_state} is not defined, '
                'consider setting ensure_transition_completeness to True'
            )
        self._current_state = current_state_transitions[input_value]
        return self.current_output

    def run(self, inputs: Iterable[str]) -> Generator[str]:
        for input_value in inputs:
            yield self.transition(input_value)

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
            outputs={state: output for state, output in self._outputs.items()},
            ensure_transition_completeness=False,
            current_state=self._current_state,
        )

    def to_dict(self) -> dict[str, str | list[str] | dict]:
        return {
            'alphabet': self._alphabet,
            'states': self._states,
            'initial_state': self._initial_state,
            'current_state': self._current_state,
            'transition_mapping': self._transition_mapping,
            'outputs': self._outputs,
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
            outputs=d['outputs'],
            current_state=d['current_state'],
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
