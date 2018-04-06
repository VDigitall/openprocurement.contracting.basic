# -*- coding: utf-8 -*-
import os
import json
from copy import deepcopy
from webtest import TestApp

from openprocurement.contracting.api.tests.base import (
    BaseWebTest as BaseBaseWebTest
)
from openprocurement.contracting.core.tests.base import (
    test_contract_data,
    test_contract_data_wo_items
)


test_common_contract_data = deepcopy(test_contract_data)
test_common_contract_data['contractType'] = 'common'
test_common_contract_data_wo_items = deepcopy(test_contract_data_wo_items)
test_common_contract_data_wo_items['contractType'] = 'common'


class DumpsTestAppwebtest(TestApp):
    """ Class used for docs """
    hostname = "api-sandbox.openprocurement.org"

    def do_request(self, req, status=None, expect_errors=None):
        req.headers.environ["HTTP_HOST"] = self.hostname
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            self.file_obj.write(req.as_bytes(True))
            self.file_obj.write("\n")
            if req.body:
                try:
                    self.file_obj.write(
                            'DATA:\n' + json.dumps(json.loads(req.body), indent=2, ensure_ascii=False).encode('utf8'))
                    self.file_obj.write("\n")
                except:
                    pass
            self.file_obj.write("\n")
        resp = super(DumpsTestAppwebtest, self).do_request(req, status=status, expect_errors=expect_errors)
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            headers = [(n.title(), v)
                       for n, v in resp.headerlist
                       if n.lower() != 'content-length']
            headers.sort()
            self.file_obj.write(str('Response: %s\n%s\n') % (
                resp.status,
                str('\n').join([str('%s: %s') % (n, v) for n, v in headers]),
            ))

            if resp.testbody:
                try:
                    self.file_obj.write(json.dumps(json.loads(resp.testbody), indent=2, ensure_ascii=False).encode('utf8'))
                except:
                    pass
            self.file_obj.write("\n\n")
        return resp


class BaseWebTest(BaseBaseWebTest):
    """Base Web Test to test openprocurement.contractning.common.api.

    It setups the database before each test and delete it after.
    """
    relative_to = os.path.dirname(__file__)


class BaseContractWebTest(BaseWebTest):
    initial_data = test_common_contract_data

    def setUp(self):
        super(BaseContractWebTest, self).setUp()
        self.create_contract()

    def create_contract(self):
        data = deepcopy(self.initial_data)

        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('contracting', ''))
        response = self.app.post_json('/contracts', {'data': data})
        self.contract = response.json['data']
        # self.contract_token = response.json['access']['token']
        self.contract_id = self.contract['id']
        self.app.authorization = orig_auth

    def tearDown(self):
        del self.db[self.contract_id]
        super(BaseContractWebTest, self).tearDown()


class BaseContractContentWebTest(BaseContractWebTest):

    def setUp(self):
        super(BaseContractContentWebTest, self).setUp()
        response = self.app.patch_json('/contracts/{}/credentials?acc_token={}'.format(
            self.contract_id, self.initial_data['tender_token']), {'data': {}})
        self.contract_token = response.json['access']['token']
