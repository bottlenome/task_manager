# -*- coding: utf-8 -*-
from enum import Enum
import json


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) is Status:
            return {o.__class__.__name__: o.value}
        else:
            return {o.__class__.__name__: o.__dict__}


def json_decode(dct):
    keys = list(dct.keys())
    # detect class if dict length equal to 1
    if len(keys) == 1 and (keys[0] in globals()):
        cls = globals()[keys[0]]
        if '__dict__' in dir(cls):
            cls = cls.__new__(cls)
            cls.__dict__.update(dct[keys[0]])
            return cls
        else:  # for enum
            return cls(dct[keys[0]])
    else:
        return dct


class Io (object):
    @staticmethod
    def load(path):
        raise NotImplementedError

    @staticmethod
    def save(path, map):
        raise NotImplementedError


class JsonIo(Io):
    @staticmethod
    def load(path):
        import json
        with open(path, 'r') as f:
            return json.load(f, object_hook=json_decode)

    @staticmethod
    def save(path, map):
        import json
        with open(path, 'w') as f:
            json.dump(map, f, cls=JsonEncoder, indent=2)


class Status(Enum):
    New = 'new'
    Waiting = 'waiting'
    Working = 'working'
    Pending = 'pending'
    Completed = 'completed'
    Discontinued = 'discontinued'


class Worker (object):
    def get_status(self):
        raise NotImplementedError

    def update_status(self):
        raise NotImplementedError

    def run(self, task):
        pass


class DefaultWorker(Worker):
    def get_status(self):
        return 'not assigned'


class LocalWorker(Worker):
    def run(self, task):
        import subprocess
        p = subprocess.Popen(task.cmd.split(' '))
        print(p.wait())

    def get_status(self):
        return 'waiting'


class SshWorker(Worker):
    def __init__(self, address):
        self.address = address

    def run(self, task):
        import paramiko
        try:
            import console
            user, passwd = console.login_alert('Login')
        except ImportError:
            import getpass
            user = 'urota'
            passwd = getpass.getpass()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        client.connect(self.address,
                       22, user, passwd)
        for cmd in task.cmd:
            _, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode('utf8'))
        client.close()
        task.done()

    def get_status(self):
        return 'done'


class Task (object):
    def __init__(self, name):
        self.name = name
        self.status = Status.New
        self.worker = DefaultWorker()

    def show(self):
        if self.status is Status.Working:
            self.status = self.worker.update_status()
        if self.status is Status.Completed:
            pass
        else:
            self.worker.run(self)
        print(self.name, self.status, self.worker.get_status())

    def set_worker(self, worker):
        self.worker = worker
        self.status = Status.Waiting

    def done(self):
        self.status = Status.Completed


class CmdTask (Task):
    def __init__(self, name, cmd):
        super().__init__(name)
        self.cmd = cmd


class TaskList (object):
    def __init__(self, setting):
        self.setting = setting

    def append(self, task):
        self.setting.setting['tasks'].append(task)

    def show(self):
        for task in self.setting.setting['tasks']:
            task.show()


class WorkerList (object):
    def __init__(self, setting, io):
        self.setting = setting
        self.io = io

    def save(self):
        pass

    def __del__(self):
        # self.save()
        pass


class Manager (object):
    def __init__(self, task_list):
        self.task_list = task_list
        self.loop_flag = True

    def add_task(self, task):
        self.task_list.append(task)

    def show_task(self):
        self.task_list.show()

    def check_task(self):
        self.task_list.show()

    def run(self):
        while self.loop_flag:
            # slave status check
            self.check_task()
            # self.apply_task()


class Setting (object):
    def __init__(self, directory, io):
        import os
        filename = 'setting.json'
        direcrory_name = '.task_manager'
        setting_directory = directory + os.sep + direcrory_name

        self.io = io

        if not os.path.exists(setting_directory):
            os.mkdir(setting_directory)
        self.setting_path = setting_directory + os.sep + filename
        self.setting = self.load()

    def load(self):
        import os
        if not os.path.exists(self.setting_path):
            setting = {'tasks': []}
            self.io.save(self.setting_path, setting)
        else:
            setting = self.io.load(self.setting_path)
        return setting

    def save(self):
        print(self.setting_path, self.setting)
        self.io.save(self.setting_path, self.setting)

    def __del__(self):
        # self.save()
        pass


def main():
    import os
    home = os.path.expanduser('~')
    setting = Setting(home, JsonIo)
    print(setting.setting)
    task_list = TaskList(setting)
    programming = Task('programming')
    echo = CmdTask('ls', ['cd git/fab/;ls'])
    worker_list = WorkerList(setting, JsonIo)
    # worker = SshWorker('www.mizusawa.work')
    worker = SshWorker('192.168.10.10')
    echo.set_worker(worker)
    manager = Manager(task_list)
    manager.add_task(programming)
    manager.add_task(echo)
    manager.show_task()
    manager.loop_flag = False
    manager.run()
    setting.save()


if __name__ == '__main__':
    main()
