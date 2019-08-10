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
Primitives for Tax Support
--------------------------
"""


from tendril.utils.types.unitbase import Percentage

from tendril.schema.base import NakedSchemaObject
from tendril.schema.helpers import SchemaObjectList

from .gst import GSTMixin
from .gst import DEFAULT_TAX


class TaxDefinition(NakedSchemaObject):
    def elements(self):
        e = super(TaxDefinition, self).elements()
        e.update({
            'tax':  self._p('tax',  required=True),
            'rate': self._p('rate', required=True, parser=Percentage),
        })
        return e

    @property
    def ident(self):
        return "{0} ({1})".format(self.tax, self.rate)

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self.ident)


class TaxDefinitionList(SchemaObjectList):
    _objtype = TaxDefinition


class TaxMixin(NakedSchemaObject, GSTMixin):
    def elements(self):
        return {'tax': self._p('tax', parser=TaxDefinitionList,
                               required=False, default=DEFAULT_TAX)}

    def override_taxes(self, taxdefinition):
        self.tax = taxdefinition

    def override_tax_rate(self, rate, tax=None):
        if not isinstance(rate, Percentage):
            rate = Percentage(rate)
        if tax:
            self._get_tax(tax).rate = rate
        else:
            for t in self.tax:
                t.rate = rate

    def _get_tax(self, name):
        for tax in self.tax:
            if tax.tax == name:
                return tax

    @property
    def unit_taxes(self):
        for tax in self.tax:
            if tax.rate == 0:
                continue
            yield (tax.ident, self.effective_price * tax.rate)

    @property
    def taxes(self):
        for tax in self.tax:
            if tax.rate == 0:
                continue
            yield (tax.ident, self.extended_price * tax.rate)

    @property
    def total_price(self):
        tp = self.extended_price
        for _, tax in self.taxes:
            tp = tp + tax
        return tp

    def reset_tax_rates(self):
        pass
