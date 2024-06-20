import asyncio
from abc import ABCMeta
import tornado.ioloop
import tornado.web
from build_config import WEB_SERVER_PORT
from util.conn_util import MongoMixin
from util.file_util import FileUtil
from util.log_util import Log

from web.attendance.test import Testhandler
from web.login import LoginHandler
from web.company.addCompany import CompanyCreateHandler
from web.company.addBranch import AddBranchHandler
from web.company.addBranchManager import AddBranchManagerHandler
from web.branchManager.addRole import RoleHandler
from web.branchManager.addHoliday import AddHolidayHandler
from web.branchManager.addPayscale import PayScaleHandler
from web.branchManager.addEmployee import AddEmployeeHandler
from web.branchManager.meetings import AddMeetingsHandler
from web.branchManager.getSchudledMeetings import GetScheduledMeetingsHandler 
from web.attendance.attendance import AttendanceHandler
from web.attendance.leave import LeaveHandler
from web.hr.onBoarding import OnBoardingHandler
from web.hr.leaveAproval import LeaveApprovalHandler
from web.hr.getHoliday import GetHolidayListHandler
from web.project.addProject import AddProjectHandler
from web.project.assignProject import ProjectAssignHandler
from web.accountManagement.account import AccountHandler
from web.accountManagement.salary import getPaySlipHandler
from web.accountManagement.getSalary import getSalaryHandler
from web.accountManagement.getSalarypdf import getSalarypdfHandler
from web.user.getEmployeeDetail import getEmployeeDetailHandler
from web.user.resetPassword import AddCalComMeetingsHandler
from web.project.assignProjectToEmp import ProjectAssignToEmpHandler

class IndexHandler(tornado.web.RequestHandler, metaclass=ABCMeta):
    fu = FileUtil()

    async def prepare(self):
        if not self.request.connection.stream.closed():
            self.set_status(404)
            try:
                with open('./lib/http_error/404.html', 'r') as error_page_file:
                    error_page = error_page_file.read()
                self.write(error_page.format(self.fu.serverUrl))
            except FileNotFoundError:
                self.write("404 Page Not Found")
        await asyncio.sleep(0.001)


class App(tornado.web.Application, MongoMixin):
    def __init__(self):
        settings = {
            'debug': True
        }
        super(App, self).__init__(
            handlers=[
                (r'/', IndexHandler),
                (r'/v1/api/create/company', CompanyCreateHandler),
                (r'/v1/api/login', LoginHandler),
                (r'/v1/api/add/branch', AddBranchHandler),
                (r'/v1/api/add/branch/manager', AddBranchManagerHandler),
                (r'/v1/api/add/employee', AddEmployeeHandler),
                (r'/v1/api/role', RoleHandler),
                (r'/v1/api/onboard', OnBoardingHandler),
                (r'/v1/api/payscale', PayScaleHandler),
                (r'/v1/api/attendance', AttendanceHandler),
                (r'/v1/api/add/project', AddProjectHandler),
                (r'/v1/api/assign/project', ProjectAssignHandler),
                (r'/v1/api/add/holiday',AddHolidayHandler),
                (r'/v1/api/get/holiday',GetHolidayListHandler),
                (r'/v1/api/add/paySlip',AccountHandler),
                (r'/v1/api/add/leave',LeaveHandler),
                (r'/v1/api/add/salary',getPaySlipHandler),
                (r'/test', Testhandler),
                (r'/v1/api/get/getSalary',getSalaryHandler),
                (r'/v1/api/put/leaveAproval',LeaveApprovalHandler),
                (r'/v1/api/add/meetings',AddMeetingsHandler),
                (r'/v1/api/get/meetings',GetScheduledMeetingsHandler),
                (r'/v1/api/get/getSalarypdf',getSalarypdfHandler),
                (r"/schedule-meeting", AddCalComMeetingsHandler),
                (r'/v1/api/get/getemployeeDetail',getEmployeeDetailHandler),
                (r'/v1/api/post/assignProjectToEmp',ProjectAssignToEmpHandler),

            ],
            **settings,
            default_handler_class=IndexHandler
        )
        Log.i('APP', 'Running Tornado Application Port - [ {} ]'.format(WEB_SERVER_PORT))


if __name__ == "__main__":
    app = App()
    app.listen(WEB_SERVER_PORT)
    tornado.ioloop.IOLoop.current().start()
