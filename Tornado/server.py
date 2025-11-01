import tornado.ioloop
import tornado.web
from apscheduler.schedulers.tornado import TornadoScheduler
import subprocess
from datetime import datetime
import TaskTornado.test as tt


def run_py(path, task_name):
    task_path = f'{path}{task_name}'
    current_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    print(f'▋ [Run Task] {task_name} at {current_time}')
    subprocess.Popen(['python', task_path])


def run_def(task_function, *args):
    current_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    print(f'▋ [Run Task] {task_function.__name__} at {current_time}')
    task_function(*args)
    

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('This is a Tornado web application with scheduled tasks!')


def make_app():
    return tornado.web.Application([ (r'/', MainHandler), ])
        

if __name__ == "__main__":
    app = make_app()
    scheduler = TornadoScheduler(timezone='Asia/Taipei')

    scheduler.add_job( lambda: run_task( tt.test, ), 'cron', hour='14', minute='15' ) 

    scheduler.start()
    app.listen(5300)
    print('RPA server is running on http://localhost:5300')
    tornado.ioloop.IOLoop.current().start()
    