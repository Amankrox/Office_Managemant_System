import json
import sys
from datetime import date, datetime
import io

import tornado.web
from bson import ObjectId
from build_config import CONFIG
from util.conn_util import MongoMixin
from util.log_util import Log
from bson.json_util import dumps as bdumps
from helper.jwt_helper import JWT_DECODE_1
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class getSalarypdfHandler(tornado.web.RequestHandler, MongoMixin):
    SUPPORTED_METHODS = ('OPTIONS', 'GET')

    user = MongoMixin.userDb[
        CONFIG['database'][0]['table'][12]['name']
    ]

    account = MongoMixin.userDb[
        CONFIG['database'][0]['table'][21]['name']
    ]

    paySlip = MongoMixin.userDb[
        CONFIG['database'][0]['table'][23]['name']
    ]

    def options(self):
        status = False
        code = 4100
        message = ''
        result = []

    async def get(self):
        code = 4100
        message = ''
        status = False
        result = []

        try:
            try:
                # get the token from header
                token = self.request.headers.get('Authorization')
                if token:
                    token = token.replace('Bearer ', '')
                else:
                    code = 4001
                    message = 'Invalid - [ Authorization ]'
                    status = False
                    raise Exception

                # decode the token
                payload = JWT_DECODE_1(token)
                if payload is None:
                    code = 4001
                    message = 'Invalid - [ Authorization ]'
                    status = False
                    raise Exception
            except Exception as e:
                Log.i(e)
                code = 4001
                message = 'Invalid - [ Authorization ]'
                status = False
                raise Exception

            user_id = payload.get('userId')
            print('*********the user_id', user_id)


            paySlipQ = self.paySlip.aggregate(
                [
                    {
                        '$match': {
                            'userId': ObjectId(user_id)
                        }
                    }
                ]
            )

            salary = []
            async for i in paySlipQ:
                salary.append(i)
            print('****************',salary)
            if not salary:
                code = 4004
                status = False
                message = 'Salary not found'
                raise Exception
            month=date.today().month

            baseSalary=salary[0]['baseSalary']
            finalSalary=salary[0]['finalSalary']
            performanceBounous=salary[0]['performanceBounous']
            finalSalary=round(salary[0]['finalSalary'])


            # Generate PDF
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.setFont("Helvetica", 12)

            # Assuming salary is a list of dicts with salary details
            p.drawString(100, 750, f"Salary Slip for User ID: {user_id}")
            p.drawString(100, 730, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            y = 700
            for item in salary:
                p.drawString(100, y, f"Month: {item.get('month', month)}")
                p.drawString(100, y - 20, f"Basic: {item.get('basic', baseSalary)}")
                p.drawString(100, y - 40, f"performance Bonous: {item.get('hra', performanceBounous)}")
                p.drawString(100, y - 60, f"Other Allowances: {item.get('other_allowances', 'N/A')}")
                p.drawString(100, y - 80, f"Total: {item.get('total', finalSalary)}")
                y -= 100

            p.showPage()
            p.save()

            buffer.seek(0)
            self.set_header('Content-Type', 'application/pdf')
            self.set_header('Content-Disposition', f'attachment; filename=salary_slip_{user_id}.pdf')
            self.write(buffer.read())
            await self.finish()
            return

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
