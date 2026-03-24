from math import sqrt
from typing import List, Any

from talipp.indicator_util import has_valid_values
from talipp.indicators.Indicator import Indicator, InputModifierType
from talipp.input import SamplingPeriodType


class StdDev(Indicator):
    """Standard Deviation.

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
        self._period_f = float(period)

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
        period = self.period
        if len(input_values) < period:
            new_output_value = None
        else:
            window = input_values[-period:]
            period_f = self._period_f
            mean = sum(window) / period_f
            new_output_value = sqrt(sum((x - mean) * (x - mean) for x in window) / period_f)
        if new_output_value is None and self.output_values:
            new_output_value = self.output_values[-1]
        self.output_values.append(new_output_value)
        for listener in self.output_listeners:
            listener.add(new_output_value)

    def _calculate_new_value(self) -> Any:
        if not has_valid_values(self.input_values, self.period):
            return None

        window = self.input_values[-self.period:]
        period_f = self._period_f
        mean = sum(window) / period_f
        return sqrt(sum((x - mean) * (x - mean) for x in window) / period_f)
