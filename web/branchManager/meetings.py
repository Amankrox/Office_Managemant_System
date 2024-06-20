from asyncio import log
import json
import sys
from datetime import date, datetime, timedelta

import tornado.web
from bson import ObjectId
from build_config import CONFIG
from lib.fernet_crypto import FN_DECRYPT
from util.conn_util import MongoMixin
from util.log_util import Log
from util.time_util import timeNow
from bson.json_util import dumps as bdumps
from helper.jwt_helper import JWT_DECODE_1, JWT_ENCODE_1
from helper.decorators import all_origin

class AddMeetingsHandler(tornado.web.RequestHandler,MongoMixin):
    SUPPORTED_METHODS=('OPTIONS','POST','GET')

    user = MongoMixin.userDb[
        CONFIG['database'][0]['table'][12]['name']
    ]
    holiday=MongoMixin.userDb[
        CONFIG['database'][0]['table'][20]['name']
    ]
    meeting=MongoMixin.userDb[
        CONFIG['database'][0]['table'][24]['name']
    ]

    #if there is same for all handlers
    def options(self):
        code =4100
        status=False
        message=''
        result=[]
    async def post(self):
        code =4100
        status=False
        message=''
        result=[]

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

            if role not in ['branchManager', 'HR-1', 'HR-2', 'HR-3','company','PROJECTMANAGER','AccountsManager']:
                code=4003
                message='You are not Authorized to use this'
                status=False
                raise Exception
            #converting the body into json
            try:
                self.request.arguments=json.loads(self.request.body)

            except Exception as e:
                code=4004      
                message='Expected request type json'
                status=False
                raise Exception
            
            userQ= self.user.find(
                {
                    '_id':ObjectId(user_id)
                },
                limit=1
            )

            user=[]
            async for i in userQ:
                user.append(i)

            print('*****************',user)
            if not user:
                message='user not found'
                code=4005
                status=False
                raise Exception
            branch_id=user[0]['branchId']
            print("breach _id is",branch_id)

            # Get meeting details from request
            meeting_date = self.request.arguments.get('date')
            start_time = self.request.arguments.get('start_time')
            end_time = self.request.arguments.get('end_time')
            title = self.request.arguments.get('title')
            description = self.request.arguments.get('description')

            if not meeting_date or not start_time or not end_time or not title:
                message = 'Missing required meeting details'
                code = 4006
                status = False
                raise Exception

            # Convert string date and times to datetime objects
            meeting_datetime = datetime.strptime(meeting_date, '%Y-%m-%d')
            start_datetime = datetime.strptime(f"{meeting_date} {start_time}", '%Y-%m-%d %H:%M')
            end_datetime = datetime.strptime(f"{meeting_date} {end_time}", '%Y-%m-%d %H:%M')

            # Check for existing meetings at the same time
            existing_meetings = await self.meeting.find({
                'branch_id': branch_id,
                'date': meeting_date,
                '$or': [
                    {'start_time': {'$lte': start_datetime}, 'end_time': {'$gt': start_datetime}},
                    {'start_time': {'$lt': end_datetime}, 'end_time': {'$gte': end_datetime}},
                    {'start_time': {'$gte': start_datetime}, 'end_time': {'$lte': end_datetime}}
                ]
            }).to_list(length=None)

            if existing_meetings:
                message = 'A meeting is already scheduled during this time.'
                code = 4007
                status = False
                raise Exception

            # Insert the new meeting
            meeting_data = {
                'companyId':company_id,
                'branch_id': branch_id,
                'date': meeting_date,
                'start_time': start_datetime,
                'end_time': end_datetime,
                'title': title,
                'description': description,
                'created_by': user_id,
                'created_at': datetime.utcnow(),
                'isActive':True,
                'isDeleted':False
            }

            await self.meeting.insert_one(meeting_data)

            code = 2000
            status = True
            message = 'Meeting scheduled successfully'
            result = meeting_data


          



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

    