from enum import Enum

class PaymentStatusEnum(Enum):
    COMPLETED = ('complete', 'Payment completed successfully')
    FAILED = ('failed', 'The payment failed')

    def __init__(self, name, description):
        self._value_ = name
        self.description = description

    @property
    def name(self):
        return self._value_