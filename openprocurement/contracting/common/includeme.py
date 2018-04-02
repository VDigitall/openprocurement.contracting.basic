# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution
from pyramid.interfaces import IRequest

from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.contracting.common.models import ICommonContract, Contract
from openprocurement.contracting.common.adapters import ContractCommonConfigurator


PKG = get_distribution(__package__)

LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('Init contracting.common plugin.')
    config.add_contract_contractType(Contract)
    config.scan("openprocurement.contracting.common.views")
    config.registry.registerAdapter(ContractCommonConfigurator,
                                    (ICommonContract, IRequest),
                                    IContentConfigurator)
