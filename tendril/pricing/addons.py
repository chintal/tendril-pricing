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


from tendril.utils.types import ParseException
from tendril.utils.types.time import DateSpan
from tendril.utils.types.currency import CurrencyValue
from tendril.utils.types.unitbase import Percentage

from tendril.schema.base import NakedSchemaObject
from tendril.schema.helpers import SchemaObjectSet

from .tax import TaxDefinitionList
from .tax import DEFAULT_TAX


class AddonDefinition(NakedSchemaObject):
    def elements(self):
        e = super(AddonDefinition, self).elements()
        e.update({
            'desc':     self._p('desc'),
            'price':    self._p('price',    parser=(Percentage, CurrencyValue)),
            'tax':      self._p('tax',      required=False, parser=TaxDefinitionList),
            'unit':     self._p('unit',     required=False, default=1),
            'unittype': self._p('unittype', required=False, default='int'),
        })
        return e

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self.desc, self.price)


class AddonDefinitionSet(SchemaObjectSet):
    _objtype = AddonDefinition


class AddonMixin(NakedSchemaObject):
    def elements(self):
        return {'addons': self._p('addons', parser=AddonDefinitionSet,
                                  required=False, default=[])}

    def include_addon(self, addon, qty=1, price=None, tax='inherit'):
        if addon in self.addons.keys():
            desc = self.addons[addon].desc
            if self.addons[addon].unittype == 'DateSpan':
                unit = DateSpan(self.addons[addon].unit)
            else:
                unit = self.addons[addon].unit
        else:
            desc = addon
            unit = 1

        if price:
            if not isinstance(price, (Percentage, CurrencyValue)):
                try:
                    price = Percentage(price)
                except ParseException:
                    price = CurrencyValue(price)
        else:
            price = self.addons[addon].price

        self._addons.append((desc, qty, price, tax, unit))

    @property
    def included_addons(self):
        for desc, qty, price, tax, unit in self._addons:
            if isinstance(price, Percentage):
                price = self.effective_price * price

            if tax:
                if tax == 'inherit':
                    tax = self.tax
                elif not isinstance(tax, TaxDefinitionList):
                    tax = TaxDefinitionList(content=tax)
            else:
                tax = TaxDefinitionList(content=DEFAULT_TAX)

            yield desc, qty, price, tax, unit

    def reset_addons(self):
        self._addons = []
