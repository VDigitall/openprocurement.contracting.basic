# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    context_unpack,
    json_view,
    APIResource,
)
from openprocurement.contracting.api.utils import (
    contractingresource,
    save_contract
)
from openprocurement.contracting.core.utils import (
    apply_patch,
    set_ownership,
)
from openprocurement.contracting.core.validation import (
    validate_patch_contract_data,
    validate_credentials_generate,
    validate_contract_update_not_in_allowed_status,
    validate_terminate_contract_without_amountPaid
)


@contractingresource(name='common:Contract',
                     path='/contracts/{contract_id}',
                     contractType='common',
                     description="Contract")
class ContractResource(APIResource):

    @json_view(permission='view_contract')
    def get(self):
        return {'data': self.request.validated['contract'].serialize("view")}

    @json_view(content_type="application/json", permission='edit_contract',
               validators=(validate_patch_contract_data, validate_contract_update_not_in_allowed_status))
    def patch(self):
        """Contract Edit (partial)
        """
        contract = self.request.validated['contract']
        apply_patch(self.request, save=False, src=self.request.validated['contract_src'])

        validate_terminate_contract_without_amountPaid(self.request)

        if save_contract(self.request):
            self.LOGGER.info('Updated contract {}'.format(contract.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_patch'}))
            return {'data': contract.serialize('view')}


@contractingresource(name='Contract credentials',
                     path='/contracts/{contract_id}/credentials',
                     description="Contract credentials")
class ContractCredentialsResource(APIResource):

    def __init__(self, request, context):
        super(ContractCredentialsResource, self).__init__(request, context)
        self.server = request.registry.couchdb_server

    @json_view(permission='generate_credentials', validators=(validate_credentials_generate,))
    def patch(self):
        contract = self.request.validated['contract']

        set_ownership(contract, self.request)
        if save_contract(self.request):
            self.LOGGER.info('Generate Contract credentials {}'.format(contract.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_patch'}))
            return {
                'data': contract.serialize("view"),
                'access': {
                    'token': contract.owner_token
                }
            }
