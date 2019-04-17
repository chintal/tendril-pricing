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


from tendril.utils.types.currency import CurrencyValue
from tendril.schema.base import NakedSchemaObject
from .tax import TaxMixin
from .addons import AddonMixin


class PricingBase(NakedSchemaObject):
    def __init__(self, *args, **kwargs):
        super(PricingBase, self).__init__(*args, **kwargs)

    @property
    def base_price(self):
        raise NotImplementedError

    @property
    def effective_price(self):
        raise NotImplementedError

    @property
    def total_price(self):
        raise NotImplementedError

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__,
                                  self.effective_price)


class StructuredUnitPrice(PricingBase, TaxMixin, AddonMixin):
    def __init__(self, *args, **kwargs):
        self._parent = kwargs.pop('parent', None)
        super(StructuredUnitPrice, self).__init__(*args, **kwargs)
        self._addons = []
        self._discounts = []
        self._taxes = []

    def elements(self):
        e = super(PricingBase, self).elements()
        e.update({
            'base':   self._p('base',   parser=CurrencyValue),
        })
        e.update(TaxMixin.elements(self))
        e.update(AddonMixin.elements(self))
        return e

    @property
    def base_price(self):
        return self.base

    def apply_discount(self, discount, desc):
        self._discounts.append((desc, discount))

    @property
    def discounts(self):
        for discount in self._discounts:
            yield discount

    @property
    def effective_price(self):
        ep = self.base
        for _, discount in self.discounts:
            ep = ep - discount
        return ep

    @property
    def total_price(self):
        tp = self.effective_price
        for _, tax in self.taxes:
            tp = tp + tax
        return tp


class PriceCollector(object):
    pass
