from typing import List, Any

from talipp.indicator_util import has_valid_values
from talipp.indicators.Indicator import Indicator, InputModifierType
from talipp.input import SamplingPeriodType
from talipp.ohlcv import OHLCV


class ATR(Indicator):
    """Average True Range

    Input type: [OHLCV][talipp.ohlcv.OHLCV]

    Output type: `float`

    Args:
        period: Period.
        input_values: List of input values.
        input_indicator: Input indicator.
        input_modifier: Input modifier.
        input_sampling: Input sampling type.
    """

    def __init__(self, period: int,
                 input_values: List[OHLCV] = None,
                 input_indicator: Indicator = None,
                 input_modifier: InputModifierType = None,
                 input_sampling: SamplingPeriodType = None):
        super(ATR, self).__init__(input_modifier=input_modifier,
                                  input_sampling=input_sampling)

        self.period = period
        self.tr = []

        self.add_managed_sequence(self.tr)

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
        high = self.input_values[-1].high
        low = self.input_values[-1].low

        if has_valid_values(self.input_values, 1, exact=True):
            self.tr.append(high - low)
        else:
            close2 = self.input_values[-2].close
            self.tr.append(max(
                high - low,
                abs(high - close2),
                abs(low - close2),
            ))

        if len(self.input_values) < self.period:
            return None
        elif len(self.input_values) == self.period:
            return sum(self.tr) / self.period
        else:
            return (self.output_values[-1] * (self.period - 1) + self.tr[-1]) / self.period
