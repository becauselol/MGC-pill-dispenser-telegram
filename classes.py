import datetime
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


class User:
	def __init__(self, update, bot, db):
		self.update = update
		if self.update.message:
			self.chat_id = update.message.chat.id
			self.text = update.message.text
			self.user_id = update.message.from_user.id
		elif self.update.callback_query:
			self.query = update.callback_query
			self.chat_id = self.query.message.chat_id
			self.user_id = self.query.from_user.id
			self.text = self.query.message.text
			self.callback_data = self.query.data
		else:
			self.user_id = None
			self.chat_id = None
			self.text = None

		self.bot = bot
		self.firebaseDoc = db.collection("users").document(str(self.user_id))
		self.reply = "Oops, something went wrong!"
		self.reply_markup = None
		self.update = dict()
		self.firebaseDict = None
		self.conversation = {
			"command": None,
			"start": None,
			"state": 0
		}
		self.requiredKeys = ["conversation", "name", "role", "age", "user_id"]

	def start(self):
		self.update = {
			"user_id": self.user_id,
			"conversation": {
				"command": "start",
				"state": 1,
				"start": datetime.datetime.now()
			},
			"role" : None
		}

		self.reply = """
			Welcome to <b>Pill Dispenser</b>, thank you for using my service

			Let's first proceed with registration.
			Please indicate if you are a Patient, Caretaker or Doctor
		"""
		keyboard = [
			[
				KeyboardButton("Patient")
			],
			[
				KeyboardButton("Caretaker")
			],
			[
				KeyboardButton("Doctor")
			]
		]
		self.reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

	def getName(self):
		self.update = {
			"role": self.text.lower(),
			"conversation.state": 2
		}

		self.reply = """
				We will now proceed with setting you up and getting your basic information
				Please enter your name
			"""

	def getAge(self):
		self.update = {
			"name": self.text,
			"conversation.state": 3
		}

		self.reply = """
			Now please enter your age
		"""

	def updateAge(self):
		if self.text.isnumeric():
			self.update = {
				"age": int(self.text),
				"conversation": {
					"state": 0
				}
			}

			self.reply = """
				Thanks for completing set up
			"""
		else:
			self.reply = """
						I'm sorry I didn't understand that, please key in your age again
					"""

	#Adapted Firebase commands
	def updateFirebase(self):
		self.firebaseDoc.update(self.update)

	def getFirebase(self):
		self.firebaseDoc.get()

	def setFirebase(self):
		self.firebaseDoc.set(self.update)

	def getFirebaseInfo(self):
		if self.firebaseDoc.get().exists:
			self.firebaseDict = self.firebaseDoc.get().to_dict()
		else:
			self.firebaseDict = None

	def unpackFirebaseInfo(self):
		#Probably there is a better way to unpack via a for loop
		if self.firebaseDict is not None:
			for key, value in self.firebaseDict.items():
				if key in self.requiredKeys:
					self.__dict__[key] = value
			print("updated")

	#Adapted Telegram bot commands
	def sendMessage(self):
		self.bot.sendMessage(self.chat_id, self.reply, reply_markup=self.reply_markup)

