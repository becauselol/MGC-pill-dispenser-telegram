import firebase_admin
from firebase_admin import credentials, firestore

from classes import User

class A:
	def __init__(self):
		self.lol = 'Hello'

class Patient(User):
	def __init__(self, update, bot, db):
		self.pills = dict()
		super().__init__(update, bot, db)

	def addPill(self, name, dosage):
		self.pills[name] = {
			'name' : name,
			'dosage' : dosage,
		}

class Doctor(User):
	def __init__(self, update, bot, db):
		super().__init__(update, bot, db)


class Caretaker(User):
	def __init__(self, update, bot, db):
		super().__init__(update, bot, db)