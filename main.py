import telegram
import pytz
from google.cloud import firestore
import os

# class file
from classes import User
from subClasses import Patient, Caretaker, Doctor

# Use the application default credentials
db = firestore.Client()
usersCol = db.collection("users")

# set timezone
timezone = pytz.timezone("Singapore")

def telegram_bot(request):
	bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])
	# get parameters
	update = telegram.Update.de_json(request.get_json(force=True), bot)

	# handle the command
	if request.method == "POST":
		user = initializer(update, bot, db)
		# Checks what the ongoing command is
		user.getCommand()
		# Handles the situation based on the command
		commandHandler(user)

		# Updates the firebase database
		if user.update != []:
			user.updateFirebase()

		# Sends a reply to the user
		user.sendMessage()
	return "okay"

def commandHandler(user):
	# Declare each command as a dictionary with two keys
	# one key is declared as conversationList
	# it lists the different functions that will be used at each state of the 'conversation'
	# since this code runs each time a message is sent to the bot
	# the other key is the fallback, for now just put user.fallback as the fallback
	#
	# follow the example below for the start command
	#
	# exampleCommand = {
	# 	"conversationList": {
	# 		0: user.firstFunc,
	# 		1: user.secondFunc,
	# 		.
	# 		.
	# 		.
	# 	},
	# 	"fallback": user.fallback
	# }

	start = {
		"conversationList": {
			0: "start",
			1: "getName",
			2: "getAge",
			3: "updateAge"
		},
		"fallback": "fallback"
	}

	addPill = {
		"conversationList": {
			0: "addPill",
			1: "getPillFrequency",
			2: "getPillConsume",
			3: "getPillCount",
			4: "updatePillCount"
		},
		"fallback": "fallback"
	}

	commandList = {
		"start": start,
		"addPill": addPill
		# Add new commands here. e.g. "command": command
	}

	fallback = {
		"conversationList": {
			0: "fallback"
		},
		"fallback": "fallback"
	}
	if hasattr(user, user.conversation["command"]):
		conversationHandler(user, **commandList.get(user.conversation["command"], fallback))
	elif user.conversation["command"] is None:
		user.reply = "Sorry, I don't understand what command this is"
	elif user.conversation["command"] is None and user.text[0] != '/':
		user.reply = "Please input a command that starts with a /"
	else:
		user.reply = "Sorry, you are not allowed to use that command"


def conversationHandler(user, conversationList, fallback):
	functionName = conversationList.get(user.conversation["state"], fallback)
	if hasattr(user, functionName):
		function = getattr(user, functionName)
		function()
	else:
		user.reply = "Function does not exist"
		user.sendMessage()

	if user.conversation["state"] == max(list(conversationList.keys())) and user.update != dict():
		user.resetState()
	elif user.update == []:
		pass
	else:
		user.incrementState()


def initializer(update, bot, db):
	if update.message:
		user_id = update.message.from_user.id
	elif update.callback_query:
		user_id = update.callback_query.from_user.id
	else:
		user_id = None
	userDoc = usersCol.document(str(user_id)).get()
	startRes = ['patient', 'caretaker', 'doctor']
	if userDoc.exists:
		userInfo = userDoc.to_dict()
		if userInfo['role'] == startRes[0]:
			user = Patient(update, bot, db)
		elif userInfo['role'] == startRes[1]:
			user = Caretaker(update, bot, db)
		elif userInfo['role'] == startRes[2]:
			user = Doctor(update, bot, db)
		else:
			user = User(update, bot, db)
	else:
		user = User(update, bot, db)

	user.getFirebaseInfo()
	if user.firebaseDict is not None:
		user.unpackFirebaseInfo()
	return user
