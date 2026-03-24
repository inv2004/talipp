from typing import List, Any

from talipp.indicator_util import has_valid_values
from talipp.indicators.Indicator import Indicator, InputModifierType
from talipp.input import SamplingPeriodType


class KAMA(Indicator):
    """Kaufman's Adaptive Moving Average.

    Input type: `float`

    Output type: `float`

    Args:
        period: Volatility period.
        fast_ema_constant_period: Fast EMA smoothing factor.
        slow_ema_constant_period: Slow EMA smoothing factor.
        input_values: List of input values.
        input_indicator: Input indicator.
        input_modifier: Input modifier.
        input_sampling: Input sampling type.
    """

    def __init__(self, period: int,
                 fast_ema_constant_period: int,
                 slow_ema_constant_period: int,
                 input_values: List[float] = None,
                 input_indicator: Indicator = None,
                 input_modifier: InputModifierType = None,
                 input_sampling: SamplingPeriodType = None):
        super().__init__(input_modifier=input_modifier,
                         input_sampling=input_sampling)

        self.period = period

        self.fast_smoothing_constant = 2.0 / (fast_ema_constant_period + 1)
        self.slow_smoothing_constant = 2.0 / (slow_ema_constant_period + 1)
        self._sc_diff = self.fast_smoothing_constant - self.slow_smoothing_constant

        self.volatility = []
        self.add_managed_sequence(self.volatility)

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
        self.input_values.append(value)
        new_output_value = self._calculate_new_value()
        if new_output_value is None and self.output_values:
            new_output_value = self.output_values[-1]
        self.output_values.append(new_output_value)
        for listener in self.output_listeners:
            listener.add(new_output_value)

    def _calculate_new_value(self) -> Any:
        input_values = self.input_values
        n = len(input_values)

        if n < 2:
            return None

        self.volatility.append(abs(input_values[-1] - input_values[-2]))

        period = self.period
        if not has_valid_values(self.volatility, period):
            return None

        volatility = sum(self.volatility[-period:])
        change = abs(input_values[-1] - input_values[-period - 1])

        if volatility != 0:
            efficiency_ratio = change / volatility
        else:
            efficiency_ratio = 0

        sc = (efficiency_ratio * self._sc_diff + self.slow_smoothing_constant) ** 2

        output_values = self.output_values
        prev_kama = output_values[-1] if (output_values and output_values[-1] is not None) else input_values[-2]

        return prev_kama + sc * (input_values[-1] - prev_kama)
