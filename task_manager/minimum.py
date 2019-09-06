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

class Task (object):
  def __init__(self, name):
    self.name = name
    self.status = Status.New

  def show(self):
    print(self.name, self.status)

class TaskList (object):
  def __init__(self, setting):
    raise NotImplementedError()

  def append(self, task):
    raise NotImplementedError()

class Worker (object):
  def __init__(self, address):
    self.address = address

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

  def add_task(self, task):
    self.task_list.append(task)

  def show_task(self):
    self.task_list.show()

  def run():
    while True:
      # slave status check
      # self.check_task()
      # self.apply_task()
      pass

def main():
  task_list = JsonTaskList(json_load('hoge'))
  programming = Task('programming')
  worker_list = JsonWorkerList(json_load('worker_list'))
  worker = Worker('localhost')
  manager = Manager(task_list)
  manager.add_task(programming)
  manager.show_task()

if __name__ == '__main__':
  main()
