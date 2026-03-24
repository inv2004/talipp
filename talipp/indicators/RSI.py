from typing import List, Any

from talipp.indicator_util import has_valid_values
from talipp.indicators.Indicator import Indicator, InputModifierType
from talipp.input import SamplingPeriodType


class RSI(Indicator):
    __slots__ = ('period', '_period_f', '_period_m1', 'avg_gain', 'avg_loss')
    """Relative Strength Index.

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
        self._period_m1 = period - 1

        self.avg_gain = []
        self.avg_loss = []

        self.add_managed_sequence(self.avg_gain)
        self.add_managed_sequence(self.avg_loss)

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
        period = self.period
        period_f = self._period_f
        period_m1 = self._period_m1
        input_values = self.input_values
        n = len(input_values)

        if n < period + 1:
            return None

        if n == period + 1:
            # calculate initial changes in price
            init_changes = [input_values[i] - input_values[i - 1] for i in range(1, period)]
            self.avg_gain.append(sum(c for c in init_changes if c > 0) / period_m1)
            self.avg_loss.append(sum(-c for c in init_changes if c < 0) / period_m1)

        change = input_values[-1] - input_values[-2]
        gain = change if change > 0 else 0.0
        loss = -change if change < 0 else 0.0

        avg_gain = self.avg_gain
        avg_loss = self.avg_loss
        avg_gain.append((avg_gain[-1] * period_m1 + gain) / period_f)
        avg_loss.append((avg_loss[-1] * period_m1 + loss) / period_f)

        avg_loss_last = avg_loss[-1]
        if avg_loss_last == 0:
            return 100.0
        rs = avg_gain[-1] / avg_loss_last
        return 100.0 - (100.0 / (1.0 + rs))
