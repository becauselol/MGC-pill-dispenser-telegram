import telegram
import pytz
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

#class file
from classes import User
from subClasses import Patient, Caretaker, Doctor

# Use the application default credentials
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
usersCol = db.collection("users")

#set timezone
timezone = pytz.timezone("Singapore")

def telegram_bot(request):
	bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])
	# get parameters
	update = telegram.Update.de_json(request.get_json(force=True), bot)

	#handle the command
	if request.method == "POST":
		user = initializer(update, bot, db)
		user.getCommand()
		commandHandler(user)

		if user.update is not None:
			if user.firebaseDoc.get().exists:
				user.updateFirebase()
			else:
				user.setFirebase()
		user.sendMessage()
	return "okay"

def commandHandler(user):
	start = {
		"conversationList" : {
			0: user.start,
			1: user.getName,
			2: user.getAge,
			3: user.updateAge
		},
		"fallback" : user.fallback
	}

	commandList = {
		"start": start
	}

	fallback = {
		"conversationList" : {
			0: user.fallback
		},
		"fallback" : user.fallback
	}
	conversationHandler(user, **commandList.get(user.conversation["command"], fallback))

def conversationHandler(user, conversationList, fallback):
	function = conversationList.get(user.conversation["state"], fallback)
	function()

def initializer(update, bot, db):
	if update.message:
		user_id = update.message.from_user.id
	elif update.callback_query:
		user_id = update.callback_query.from_user.id
	else:
		user_id = None
	userDoc = usersCol.document(str(user_id)).get()
	startRes = ['Patient', 'Caretaker', 'Doctor']
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

