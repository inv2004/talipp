from typing import List, Any

from talipp.indicator_util import has_valid_values
from talipp.indicators.Indicator import Indicator, InputModifierType
from talipp.input import SamplingPeriodType


class SMA(Indicator):
    __slots__ = ('period', '_period_f', '_ready')
    """Simple Moving Average.

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
        self._ready = False

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
        if self._ready:
            if self.input_modifier is not None:
                value = self.input_modifier(value)
            input_values = self.input_values
            ov = self.output_values
            new_v = ov[-1] - (input_values[-self.period] - value) / self._period_f
            input_values.append(value)
            ov.append(new_v)
            if self.output_listeners:
                for listener in self.output_listeners:
                    listener.add(new_v)
            return

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
        elif n == period or input_values[-period - 1] is None:
            new_output_value = sum(input_values[-period:]) / self._period_f
            self._ready = True
        else:
            new_output_value = self.output_values[-1] - (input_values[-period - 1] - value) / self._period_f
            self._ready = True
        if new_output_value is None and self.output_values:
            new_output_value = self.output_values[-1]
        self.output_values.append(new_output_value)
        if self.output_listeners:
            for listener in self.output_listeners:
                listener.add(new_output_value)

    def _remove_custom(self) -> None:
        if len(self.input_values) <= self.period:
            self._ready = False

    def _remove_all_custom(self) -> None:
        self._ready = False

    def _calculate_new_value(self) -> Any:
        if has_valid_values(self.input_values, self.period + 1):
            return self.output_values[-1] - \
                   (self.input_values[-self.period - 1] - self.input_values[-1]) / self._period_f
        elif has_valid_values(self.input_values, self.period, exact=True):
            return sum(self.input_values[-self.period:]) / self._period_f
        else:
            return None
