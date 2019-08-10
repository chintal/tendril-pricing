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
Infrastructure for Composite Pricing
------------------------------------
"""

from six import iteritems
from .base import PricingBase
from .tax import TaxMixin
from .addons import AddonMixin


class PriceCollector(TaxMixin, PricingBase, AddonMixin):
    def __init__(self, *args, **kwargs):
        self.unit = 1
        self.qty = 1
        super(PriceCollector, self).__init__({}, *args, **kwargs)
        self.tax = None
        self.items = []
        self.optional_items = []
        self.addons = {}
        self._addons = []
        self._optional_addons = []

    def elements(self):
        return {}

    @property
    def base_price(self):
        return sum([i.base_price * i.iqty for i in self.items])

    @property
    def effective_price(self):
        return sum([i.effective_price * i.iqty for i in self.items])

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
            qty = litem.iqty
            for lident, ldiscount in litem.discounts:
                if lident in collector.keys():
                    collector[lident] += ldiscount * qty
                else:
                    collector[lident] = ldiscount * qty

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
                    collector[laddon.desc].add_item(laddon)
                else:
                    collector[laddon.desc] = PriceCollector()
                    collector[laddon.desc].desc = laddon.desc
                    collector[laddon.desc].add_item(laddon)

        for item in self.items:
            _get_item_addons(item)

        for _, addon in iteritems(collector):
            yield addon

        for row in super(PriceCollector, self).included_addons:
            yield row

    @property
    def optional_addons(self):
        collector = {}

        def _get_item_optional_addons(litem):
            for laddon in litem.optional_addons:
                if laddon.desc in collector.keys():
                    collector[laddon.desc].add_item(laddon)
                else:
                    collector[laddon.desc] = PriceCollector()
                    collector[laddon.desc].desc = laddon.desc
                    collector[laddon.desc].add_item(laddon)

        for item in self.items:
            _get_item_optional_addons(item)

        for _, addon in iteritems(collector):
            yield addon

        for row in super(PriceCollector, self).optional_addons:
            yield row

    def add_item(self, item, optional=False):
        if self.tax is None:
            self.tax = item.tax
        if not optional:
            self.items.append(item)
        else:
            self.optional_items.append(item)

    def __len__(self):
        return len(self.items)
