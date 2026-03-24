from typing import List, Any

from talipp.indicator_util import has_valid_values
from talipp.indicators.EMA import EMA
from talipp.indicators.Indicator import Indicator, InputModifierType
from talipp.input import SamplingPeriodType


class ZLEMA(Indicator):
    """Zero Lag Exponential Moving Average.

    Input type: `float`

    Output type: `float`

    Args:
        period: Period.
        input_values: List of input values.
        input_indicator: Input indicator.
        input_modifier: Input modifier.
        input_sampling: Input sampling type.
    """

    def __init__(self, period: int,
                 input_values: List[float] = None,
                 input_indicator: Indicator = None,
                 input_modifier: InputModifierType = None,
                 input_sampling: SamplingPeriodType = None):
        super().__init__(input_modifier=input_modifier,
                         input_sampling=input_sampling)

        self.lag = round((period - 1) / 2.0)

        self.ema = EMA(period)
        self.add_managed_sequence(self.ema)

        self.initialize(input_values, input_indicator)

    def add_input_value(self, value) -> None:
        self._add_single(value)

    def add(self, value) -> None:
        if isinstance(value, list):
            for v in value:
                self._add_single(v)
        else:
            self._add_single(value)

    def _add_single(self, value) -> None:
        if self.input_modifier is not None:
            value = self.input_modifier(value)
        self.input_values.append(value)
        new_output_value = self._calculate_new_value()
        if new_output_value is None and self.output_values:
            new_output_value = self.output_values[-1]
        self.output_values.append(new_output_value)
        for listener in self.output_listeners:
            listener.add(new_output_value)

    def _calculate_new_value(self) -> Any:
        if not has_valid_values(self.input_values, self.lag+1):
            return None

        self.ema.add(self.input_values[-1] + (self.input_values[-1] - self.input_values[-self.lag-1]))

        if not has_valid_values(self.ema):
            return None

        return self.ema[-1]
