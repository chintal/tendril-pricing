# Copyright (C) 2019 Chintalagiri Shashank
#
# This file is part of Tendril.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Base Pricing Primitives
-----------------------
"""

from tendril.schema.base import NakedSchemaObject
from .discount import DiscountMixin
from .tax import TaxMixin


class PricingBase(NakedSchemaObject):
    def __init__(self, *args, **kwargs):
        self.qty = kwargs.pop('qty', 1)
        self.unit = kwargs.pop('unit', 1)
        super(PricingBase, self).__init__(*args, **kwargs)

    @property
    def base_price(self):
        raise NotImplementedError

    @property
    def effective_price(self):
        return self.base_price

    @property
    def iqty(self):
        return self.qty / self.unit

    @property
    def extended_price(self):
        return self.effective_price * self.iqty

    @property
    def total_price(self):
        return self.extended_price

    def reset_qty(self):
        self.qty = self.unit

    def __repr__(self):
        return "<{0} {1} {2} {3}>" \
               "".format(self.__class__.__name__,
                         self.base_price,
                         self.effective_price,
                         self.total_price)


class SimplePricingRow(DiscountMixin, TaxMixin, PricingBase):
    def __init__(self, *args, **kwargs):
        self.price = kwargs.pop('price', 0)
        self.tax = kwargs.pop('tax', None)
        self.desc = kwargs.pop('desc')
        super(SimplePricingRow, self).__init__({}, *args, **kwargs)
        self._discounts = []

    def elements(self):
        return {}

    @property
    def base_price(self):
        return self.price

    @property
    def included_addons(self):
        return {}
