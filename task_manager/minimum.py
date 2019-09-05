from enum import Enum

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

class JsonTaskList (TaskList):
	def __init__(self, file_path):
		import json
		with open(file_path, 'r') as f:
			self.setting = json.load(f)
			
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

def main():
	task_list = JsonTaskList('hoge')
	programming = Task('programming')
	manager = Manager(task_list)
	manager.add_task(programming)
	manager.show_task()
	
if __name__ == '__main__':
	main()
