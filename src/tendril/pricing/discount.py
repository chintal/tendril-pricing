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
Primitives for Discounts Support
--------------------------------
"""


from tendril.utils.types import ParseException
from tendril.utils.types.unitbase import Percentage
from tendril.utils.types.currency import CurrencyValue


class DiscountMixin(object):
    def apply_discount(self, discount, desc):
        if not isinstance(discount, (Percentage, CurrencyValue)):
            try:
                discount = CurrencyValue(discount)
            except ParseException:
                discount = Percentage(discount)
        self._discounts.append((desc, discount))

    @property
    def discounts(self):
        ep = self.base_price
        for name, discount in self._discounts:
            if isinstance(discount, Percentage):
                name = "{0} ({1})".format(name, discount)
                discount = ep * discount
            ep = ep - discount
            yield name, discount

    @property
    def effective_price(self):
        ep = self.base_price
        for _, discount in self.discounts:
            ep = ep - discount
        return ep

    def reset_dicounts(self):
        self._discounts = []
