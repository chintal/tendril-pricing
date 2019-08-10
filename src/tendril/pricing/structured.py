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
Structured Pricing Primitives
-----------------------------
"""

from tendril.utils.types.currency import CurrencyValue

from .base import PricingBase
from .tax import TaxMixin
from .addons import AddonMixin
from .discount import DiscountMixin


class StructuredUnitPrice(DiscountMixin, TaxMixin, PricingBase, AddonMixin):
    def __init__(self, *args, **kwargs):
        self._parent = kwargs.pop('parent', None)
        super(StructuredUnitPrice, self).__init__(*args, **kwargs)
        self._addons = []
        self._optional_addons = []
        self._discounts = []
        self._taxes = []

    def elements(self):
        e = super(StructuredUnitPrice, self).elements()
        e.update({'base':   self._p('base',   parser=CurrencyValue)})
        e.update(TaxMixin.elements(self))
        e.update(AddonMixin.elements(self))
        return e

    @property
    def base_price(self):
        return self.base

    def reset(self):
        PricingBase.reset_qty(self)
        AddonMixin.reset_addons(self)
        DiscountMixin.reset_dicounts(self)
        TaxMixin.reset_tax_rates(self)
