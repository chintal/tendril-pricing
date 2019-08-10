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
Specialized Primitives for GST Support
--------------------------------------
"""


# TODO Move to configs
DEFAULT_TAX = [{'tax': 'CGST', 'rate': '9%'},
               {'tax': 'SGST', 'rate': '9%'},
               {'tax': 'IGST', 'rate': '0%'}]


class GSTMixin(object):
    def _get_tax(self, name):
        raise NotImplementedError

    def override_tax_rate(self, rate, tax=None):
        raise NotImplementedError

    def gst_set_national(self):
        sgst = self._get_tax('SGST')
        cgst = self._get_tax('CGST')
        if sgst.rate == 0:
            return
        if cgst.rate == 0:
            return
        self.override_tax_rate(cgst.rate + sgst.rate, tax='IGST')
        self.override_tax_rate(0,                     tax='CGST')
        self.override_tax_rate(0,                     tax='SGST')

    def gst_set_local(self):
        igst = self._get_tax('IGST')
        if igst.rate == 0:
            return
        self.override_tax_rate(igst.rate / 2, tax='SGST')
        self.override_tax_rate(igst.rate / 2, tax='CGST')
        self.override_tax_rate(0,             tax='IGST')
