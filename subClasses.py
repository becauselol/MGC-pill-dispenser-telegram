import datetime
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from classes import User

class Patient(User):
	def __init__(self, update, bot, db):
		self.pills = dict()
		super().__init__(update, bot, db)
		self.pillsRef = self.firebaseDoc.collection("pills")

	def addPill(self):
		update = {
			"conversation": {
				"command": self.conversation["command"],
				"start": datetime.datetime.now()
			}
		}
		self.addUpdate(update)

		self.reply = """
			Hi, Please enter the name of the pill
		"""

	def getPillFrequency(self):
		updateConv = {
			"conversation.pillName": self.text
		}
		self.addUpdate(updateConv)

		self.conversation["pillName"] = self.text
		updateLocation = self.pillsRef.document(str(self.conversation["pillName"]))
		updateName = {
			"name": self.text,
		}
		self.addUpdate(updateName, updateLocation)

		self.reply = """
			Hi Please key in the interval that this pill needs to be consumed at, in number of hours
		"""

	def getPillConsume(self):
		if self.text.isnumeric():
			updateFreqLocation = self.pillsRef.document(str(self.conversation["pillName"]))
			updateFreq = {
				"frequency": int(self.text)
			}
			self.addUpdate(updateFreq, updateFreqLocation)

			self.reply = """
				Hi, please key in the number of pills that have to be consumed each time
			"""
		else:
			self.reply = "I'm sorry I didn't understand that"

	def getPillCount(self):
		if self.text.isnumeric():
			updateNumberLocation = self.pillsRef.document(str(self.conversation["pillName"]))
			updateNumber = {
				"number": int(self.text)
			}
			self.addUpdate(updateNumber, updateNumberLocation)

			self.reply = """
				Hi, please key in the number of pills that have been dispensed to you
			"""
		else:
			self.reply = "I'm sorry I didn't understand that"

	def updatePillCount(self):
		updateCountLocation = self.pillsRef.document(str(self.conversation["pillName"]))
		updateCount = {
			"pillCount": int(self.text)
		}
		self.addUpdate(updateCount, updateCountLocation)

		self.reply = "Thank you, " + str(self.conversation["pillName"]) + " has been added"


class Doctor(User):
	def __init__(self, update, bot, db):
		super().__init__(update, bot, db)


class Caretaker(User):
	def __init__(self, update, bot, db):
		super().__init__(update, bot, db)