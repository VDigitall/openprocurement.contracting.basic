# -*- coding: utf-8 -*-
from zope.interface import implementer, Interface
from schematics.types import StringType
from openprocurement.contracting.core.models import Contract as BaseContract


class ICommonContract(Interface):
    """ Contract marker interface """


@implementer(ICommonContract)
class Contract(BaseContract):
    """ Common Contract """
    contractType = StringType()
