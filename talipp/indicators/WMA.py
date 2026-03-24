from typing import List, Any

from talipp.indicator_util import has_valid_values
from talipp.indicators.Indicator import Indicator, InputModifierType
from talipp.input import SamplingPeriodType


class WMA(Indicator):
    """Weighted Moving Average.

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

        self.period = period
        self.denom_sum = period * (period + 1) / 2.0
        self._weights = tuple(range(1, period + 1))

        self.initialize(input_values, input_indicator)

    def add_input_value(self, value: Any) -> None:
        self._add_single(value)

    def add(self, value: Any) -> None:
        if isinstance(value, list):
            for v in value:
                self._add_single(v)
        else:
            self._add_single(value)

    def _add_single(self, value: Any) -> None:
        if self.input_modifier is not None:
            value = self.input_modifier(value)
        for sub_indicator in self.sub_indicators:
            sub_indicator.add(value)
        input_values = self.input_values
        input_values.append(value)
        n = len(input_values)
        period = self.period
        if value is None or n < period or input_values[-period] is None:
            new_output_value = None
        else:
            new_output_value = sum(v * w for v, w in zip(input_values[-period:], self._weights)) / self.denom_sum
        if new_output_value is None and self.output_values:
            new_output_value = self.output_values[-1]
        self.output_values.append(new_output_value)
        for listener in self.output_listeners:
            listener.add(new_output_value)

    def _calculate_new_value(self) -> Any:
        if not has_valid_values(self.input_values, self.period):
            return None

        return sum(v * w for v, w in zip(self.input_values[-self.period:], self._weights)) / self.denom_sum
