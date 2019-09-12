from enum import Enum

def json_load(file_path):
  import json
  with open(file_path, 'r') as f:
    return json.load(f)

def save_json_setting(file_path):
  pass

class Status(Enum):
  New = 0
  Waiting = 1
  Working = 2
  Pending = 3
  Completed = 4
  Discontinued = 5
  
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
    import getpass
    username = 'urota'
    print(username)
    password = getpass.getpass()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(
      paramiko.AutoAddPolicy())
    client.connect(self.address,
                   22,username,password)
    _, stdout, stderr = client.exec_command(task.cmd)
    print(stdout.read().decode('utf8'))
    client.close()

class Task (object):
  def __init__(self, name):
    self.name = name
    self.status = Status.New
    self.worker = DefaultWorker()

  def show(self):
    if self.status is Status.Working:
      self.status = self.worker.update_status()
    self.worker.run(self)
    print(self.name, self.status, self.worker.get_status())
  
  def set_worker(self, worker):
    self.worker = worker
    self.status = Status.Waiting

class CmdTask (Task):
  def __init__(self, name, cmd):
    super().__init__(name)
    self.cmd = cmd

class TaskList (object):
  def __init__(self, setting):
    raise NotImplementedError()

  def append(self, task):
    raise NotImplementedError()

class JsonWorkerList (object):
  def __init__(self, setting):
    self.setting = setting

class JsonTaskList (TaskList):
  def __init__(self, setting):
    self.setting = setting

  def append(self, task):
    self.setting['tasks'].append(task)

  def show(self):
    for task in self.setting['tasks']:
      task.show()

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

def main():
  task_list = JsonTaskList(json_load('hoge'))
  programming = Task('programming')
  echo = CmdTask('ls', 'ls -al')
  worker_list = JsonWorkerList(json_load('worker_list'))
  worker = SshWorker('www.mizusawa.work')
  echo.set_worker(worker)
  manager = Manager(task_list)
  manager.add_task(programming)
  manager.add_task(echo)
  manager.show_task()
  manager.loop_flag = False
  manager.run()

if __name__ == '__main__':
  main()
