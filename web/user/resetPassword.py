import json
import sys
import requests
from datetime import datetime

import tornado.web
from bson import ObjectId
from build_config import CONFIG
from util.conn_util import MongoMixin
from util.log_util import Log
from bson.json_util import dumps as bdumps
from helper.jwt_helper import JWT_DECODE_1
from helper.decorators import all_origin

class AddCalComMeetingsHandler(tornado.web.RequestHandler, MongoMixin):
    SUPPORTED_METHODS = ('OPTIONS', 'POST')

    user = MongoMixin.userDb[CONFIG['database'][0]['table'][12]['name']]
    meeting = MongoMixin.userDb[CONFIG['database'][0]['table'][24]['name']]

    def options(self):
        self.set_status(204)
        self.finish()

    async def post(self):
        code = 4100
        status = False
        message = ''
        result = []

        try:
            # Authorization
            token = self.request.headers.get('Authorization')
            if token:
                token = token.replace('Bearer ', '')
            else:
                code = 4211
                message = 'Invalid - [ Authorization ]'
                status = False
                raise Exception

            payload = JWT_DECODE_1(token)
            if payload is None:
                code = 4212
                message = 'Invalid - [ Authorization ]'
                status = False
                raise Exception

            user_id = payload.get('userId')
            company_id = payload.get('companyId')
            role = payload.get('userRole')

            if role not in ['branchManager', 'HR-1', 'HR-2', 'HR-3', 'company', 'PROJECTMANAGER', 'AccountsManager']:
                code = 4003
                message = 'You are not Authorized to use this'
                status = False
                raise Exception

            # Parse request body
            data = json.loads(self.request.body)
            meeting_date = data.get('date')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            title = data.get('title')
            description = data.get('description')

            if not meeting_date or not start_time or not end_time or not title:
                message = 'Missing required meeting details'
                code = 4006
                status = False
                raise Exception

            # Convert string dates and times to datetime objects
            start_datetime = datetime.strptime(f"{meeting_date} {start_time}", '%Y-%m-%d %H:%M')
            end_datetime = datetime.strptime(f"{meeting_date} {end_time}", '%Y-%m-%d %H:%M')

            # Check for existing meetings at the same time
            existing_meetings = await self.meeting.find({
                'branch_id': user_id,
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

            # Insert the new meeting into your database
            meeting_data = {
                'companyId': company_id,
                'branch_id': user_id,
                'date': meeting_date,
                'start_time': start_datetime,
                'end_time': end_datetime,
                'title': title,
                'description': description,
                'created_by': user_id,
                'created_at': datetime.utcnow(),
                'isActive': True,
                'isDeleted': False
            }

            await self.meeting.insert_one(meeting_data)

            # Schedule the meeting in Cal.com
            cal_com_endpoint = "https://api.cal.com/v1/meetings"
            cal_com_data = {
                "title": title,
                "date": meeting_date,
                "start_time": start_time,
                "end_time": end_time,
                "description": description
            }
            cal_com_headers = {
                "Content-Type": "application/json",
                "Authorization": 'cal_live_62d6cc49065c0459b902d6f14e2a2090'
            }
            cal_com_response = requests.post(cal_com_endpoint, data=json.dumps(cal_com_data), headers=cal_com_headers)
            print('***************')
            print('**************',cal_com_response.status_code)#405

            if cal_com_response.status_code == 201:
                code = 2000
                status = True
                message = 'Meeting scheduled successfully in Cal.com and database'
                result = meeting_data
            else:
                message = f'Failed to schedule meeting in Cal.com: {cal_com_response.text}'
                code = 4008
                status = False
                Log.e(f'Cal.com response: {cal_com_response.status_code} {cal_com_response.text}')
                raise Exception

        except Exception as e:
            Log.i(e)
            if not message:
                template = 'Exception: {0}. Argument: {1!r}'
                code = 5010
                message = 'Internal Error, Please Contact the Support Team.'
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = exc_tb.tb_frame.f_code.co_filename
                Log.w('EXC', template.format(type(e).__name__, e.args))
                Log.d('EX2', f'FILE: {fname} LINE: {exc_tb.tb_lineno} TYPE: {exc_type}')

        response = {'code': code, 'status': status, 'message': message, 'result': result}
        Log.d('RSP', response)
        self.write(json.loads(bdumps(response)))
        await self.finish()
