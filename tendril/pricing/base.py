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


from six import iteritems
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
    def extended_price(self):
        return self.effective_price * (self.qty / self.unit)

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


class PriceCollector(PricingBase):
    def __init__(self, *args, **kwargs):
        self.unit = 1
        self.qty = 1
        super(PriceCollector, self).__init__({}, *args, **kwargs)
        self.items = []

    def elements(self):
        return {}

    @property
    def base_price(self):
        return sum([i.base_price * (i.qty/i.unit) for i in self.items])

    @property
    def effective_price(self):
        return sum([i.effective_price * (i.qty/i.unit) for i in self.items])

    @property
    def extended_price(self):
        return sum([i.extended_price for i in self.items])

    @property
    def total_price(self):
        return sum([i.total_price for i in self.items])

    @property
    def grand_total(self):
        return self.extended_price + \
               sum([x[1] for x in self.taxes]) + \
               sum(x.extended_price for x in self.included_addons)

    @property
    def discounts(self):
        collector = {}

        def _get_item_discounts(litem):
            for lident, ldiscount in litem.discounts:
                if lident in collector.keys():
                    collector[lident] += ldiscount
                else:
                    collector[lident] = ldiscount

        for item in self.items:
            _get_item_discounts(item)

        for item in self.included_addons:
            _get_item_discounts(item)

        for ident, discount in iteritems(collector):
            yield (ident, discount)

    @property
    def taxes(self):
        collector = {}

        def _get_item_taxes(litem):
            for lident, ltax in litem.taxes:
                if lident in collector.keys():
                    collector[lident] += ltax
                else:
                    collector[lident] = ltax

        for item in self.items:
            _get_item_taxes(item)

        for item in self.included_addons:
            _get_item_taxes(item)

        for ident, tax in iteritems(collector):
            yield (ident, tax)

    @property
    def included_addons(self):
        collector = {}

        def _get_item_addons(litem):
            for laddon in litem.included_addons:
                if laddon.desc in collector.keys():
                    collector[laddon.desc].append(laddon)
                else:
                    collector[laddon.desc] = PriceCollector()
                    collector[laddon.desc].desc = laddon.desc
                    collector[laddon.desc].append(laddon)

        for item in self.items:
            _get_item_addons(item)

        for _, addon in iteritems(collector):
            yield addon

    def append(self, item):
        self.items.append(item)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, item):
        return self.items[item]
