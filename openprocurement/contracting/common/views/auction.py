# -*- coding: utf-8 -*-
from hashlib import sha512
from openprocurement.api.utils import (
    json_view,
    APIResource,
)

from openprocurement.auctions.core.utils import opresource


@opresource(
    name='Auction credentials',
    path='/auctions/{auction_id}/extract_credentials',
    description="Open Contracting compatible data exchange format. ' \
    'See http://ocds.open-contracting.org/standard/r/master/#tender for more info"
)
class AuctionResource(APIResource):

    @json_view(permission='extract_credentials')
    def get(self):
        self.LOGGER.info('Extract credentials for auction {}'.format(self.context.id))
        auction = self.request.validated['auction']
        data = auction.serialize('contracting')
        data['auction_token'] = sha512(auction.owner_token).hexdigest()
        return {'data': data}
