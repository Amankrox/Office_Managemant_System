import json
import sys
import tornado.web
from bson import ObjectId
from build_config import CONFIG
from util.conn_util import MongoMixin
from util.log_util import Log
from bson.json_util import dumps as bdumps
from helper.jwt_helper import JWT_DECODE_1

class getEmployeesByBranchHandler(tornado.web.RequestHandler, MongoMixin):
    SUPPORTED_METHODS = ('OPTIONS' 'GET')

    user = MongoMixin.userDb[
        CONFIG['database'][0]['table'][12]['name']
    ]

    def options(self):
        self.set_status(204)
        self.finish()

    async def get(self):
        code = 4100
        status = False
        message = ''
        result = []

        try:
            token = self.request.headers.get('Authorization')
            if token:
                token = token.replace('Bearer ', '')
            else:
                code = 4211
                message = 'Invalid - [ Authorization ]'
                status = False
                raise Exception(message)

            payload = JWT_DECODE_1(token)
            if payload is None:
                code = 4212
                message = 'Invalid - [ Authorization ]'
                status = False
                raise Exception(message)

            user_id = payload.get('userId')
            role = payload.get('userRole')

            if role not in ['branchManager', 'HR-1', 'HR-2', 'HR-3', 'company', 'PROJECTMANAGER', 'AccountsManager']:
                code = 4003
                message = 'You are not Authorized to use this'
                status = False
                raise Exception(message)

            try:
                self.request.arguments = json.loads(self.request.body)
            except Exception as e:
                code = 4004
                message = 'Expected request type json'
                status = False
                raise Exception(message)

            userQ = self.user.find(
                {
                    '_id': ObjectId(user_id)
                },
                limit=1
            )

            user = []
            async for i in userQ:
                user.append(i)

            if not user:
                message = 'User not found'
                code = 4005
                status = False
                raise Exception(message)

            branch_id = user[0]['branchId']

            role_id = self.request.arguments.get('role_id')
            if not role_id:
                code = 4007
                message = 'Missing role_id in request'
                raise Exception(message)

            employeesQ = self.user.aggregate(
                [
                    {
                        '$match': {
                            'role': ObjectId(role_id),
                            'branchId': ObjectId(branch_id)
                        }
                    }, {
                        '$project': {
                            'companyId': 1,
                            'branchId': 1,
                            'role': 1,
                            'PersonalInfo': 1,
                            'email': 1,
                            'active': 1
                        }
                    }
                ]
            )
            employees = []
            async for i in employeesQ:
                employees.append(i)
            
            if not employees:
                code = 4005
                message = 'List of employees not found'
                status = False
                raise Exception(message)

            code = 2000
            status = True
            message = 'Success'
            result = employees

        except Exception as e:
            status = False
            if not len(message):
                template = 'Exception: {0}. Argument: {1!r}'
                code = 5010
                message = 'Internal Error, Please Contact the Support Team.'
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = exc_tb.tb_frame.f_code.co_filename
                Log.w('EXC', template.format(type(e).__name__, e.args))
                Log.d('EX2', 'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))

        response = {
            'code': code,
            'status': status,
            'message': message,
            'result': result
        }
        Log.d('RSP', response)
        try:
            self.write(json.loads(bdumps(response)))
            await self.finish()
        except Exception as e:
            template = 'Exception: {0}. Argument: {1!r}'
            code = 5011
            message = 'Internal Error, Please Contact the Support Team.'
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename
            Log.w('EXC', template.format(type(e).__name__, e.args))
            Log.d('EX2', 'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
            response = {
                'code': code,
                'status': status,
                'message': message
            }
            self.write(json.loads(bdumps(response)))
            await self.finish()

