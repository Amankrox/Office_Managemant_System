import json
import sys
from datetime import datetime, timedelta

import tornado.web
from bson import ObjectId
from build_config import CONFIG
from util.conn_util import MongoMixin
from util.log_util import Log
from util.time_util import timeNow
from bson.json_util import dumps as bdumps
from helper.jwt_helper import JWT_DECODE_1, JWT_ENCODE_1
from helper.decorators import all_origin


class ProjectAssignToEmpHandler(tornado.web.RequestHandler, MongoMixin):
    SUPPORTED_METHODS = ('OPTIONS', 'GET', 'POST')

    user = MongoMixin.userDb[
        CONFIG['database'][0]['table'][12]['name']
    ]

    company = MongoMixin.userDb[
        CONFIG['database'][0]['table'][13]['name']
    ]

    branch = MongoMixin.userDb[
        CONFIG['database'][0]['table'][14]['name']
    ]

    obBoard = MongoMixin.userDb[
        CONFIG['database'][0]['table'][16]['name']
    ]

    project = MongoMixin.userDb[
        CONFIG['database'][0]['table'][19]['name']
    ]
    assignProject = MongoMixin.userDb[
        CONFIG['database'][0]['table'][25]['name']
    ]

    def options(self):
        status = False
        code = 4100
        message = ''
        result = []

    async def post(self):
        status = False
        code = 4100
        message = ''
        result = []

        try:
            try:
                token = self.request.headers.get('Authorization')
                if token:
                    token = token.replace('Bearer ', '')
                else:
                    code = 4211
                    message = 'Invalid - [ Authorization ]'
                    status = False
                    raise Exception

                # Decode the token
                payload = JWT_DECODE_1(token)
                if payload is None:
                    code = 4212
                    message = 'Invalid - [ Authorization ]'
                    status = False
                    raise Exception
            except Exception as e:
                Log.i(e)
                code = 4334
                message = 'Invalid - [ Authorization ]'
                status = False
                raise Exception

            user_id = payload.get('userId')
            company_id = payload.get('companyId')
            role = payload.get('userRole')

            # Giving access which user
            if role != 'branchManager':
                code = 4563
                message = 'You are not authorized to access this resource.'
                status = False
                raise Exception
            else:
                try:
                    self.request.arguments = json.loads(self.request.body)
                except Exception as e:
                    code = 4743
                    message = 'Excepted Request Type JSON'
                    raise Exception
                 
                

                # extract branch id from user_id
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
                    message = 'User not found in database.'
                    code = 6587
                    status = False
                    raise Exception

                branch_id = user[0]['branchId']
                if not branch_id:
                    message = 'Branch not found.'
                    code = 6588
                    status = False
                    raise Exception

                # Get project manager ID
                projectManagerId = self.request.arguments.get('pmId')
                if not projectManagerId or not isinstance(projectManagerId, str):
                    code = 4512
                    message = 'Invalid - [ Project Manager ID ]'
                    status = False
                    raise Exception

                # Get list of user IDs
                userIds = self.request.arguments.get('userIds')
                if not userIds or not isinstance(userIds, list) or not all(isinstance(uid, str) for uid in userIds):
                    code = 4513
                    message = 'Invalid - [ User IDs ]'
                    status = False
                    raise Exception

                # Get list of tasks
                tasks = self.request.arguments.get('tasks')
                if not tasks or not isinstance(tasks, list):
                    code = 4514
                    message = 'Invalid - [ Tasks ]'
                    status = False
                    raise Exception

                projectDetail = {
                    'project_id': ObjectId(),  # Create a new ObjectId for the project
                    'isActive': True,
                    'createdBy': ObjectId(user_id),
                    'companyId': ObjectId(company_id),
                    'branchId': ObjectId(branch_id),
                    'AssignedOn': datetime.now(),
                    'users': [ObjectId(uid) for uid in userIds],  # List of user IDs
                    'tasks': tasks,  # List of tasks
                    'isDelivered': False,
                    'deliveredOn': None,
                    'deleted': False,
                }

                self.assignProject.insert_one(projectDetail)

                status = True
                code = 2000
                message = 'Project assigned successfully'
                result = projectDetail

        except Exception as e:
            status = False
            if not len(message):
                template = 'Exception: {0}. Argument: {1!r}'
                code = 5010
                iMessage = template.format(type(e).__name__, e.args)
                message = 'Internal Error, Please Contact the Support Team.'
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = exc_tb.tb_frame.f_code.co_filename
                Log.w('EXC', iMessage)
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
            return
        except Exception as e:
            status = False
            template = 'Exception: {0}. Argument: {1!r}'
            code = 5011
            iMessage = template.format(type(e).__name__, e.args)
            message = 'Internal Error, Please Contact the Support Team.'
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename
            Log.w('EXC', iMessage)
            Log.d('EX2', 'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
            response = {
                'code': code,
                'status': status,
                'message': message
            }
            self.write(json.loads(bdumps(response)))
            await self.finish()
