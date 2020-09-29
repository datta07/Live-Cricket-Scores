import websocket
import json
import requests
import ssl
import sys
import os
os.system('cls')


class CricLive:
	def __init__(self,url):
		self.url=url
		self.ws = websocket.create_connection(self.url,sslopt={"cert_reqs": ssl.CERT_NONE})
		self.data={}
		self.match=None
		self.indicates={"B":"Ball Started","BS":"Bowler Stopped","WK":"Wicket","OC":"Over Completed","WD":"Wide","FH":"Free Hit","C":"Cancel"}
		self.params={"p1":"Player1","p2":"Player2","b1s":"player1Score","b2s":"player2Score","bw":"bowler","lw":"lastWicket",
					 "i1":"innings1Score","i2":"innings2Score","i":"inningsNow","pb":"playerBoard","cs":"DisplayCard",
					 "os":"position"}
		self.initialLoad() # Loading the preLoaders
		self.initialSetup() # Loading for initial setup

	def initialLoad(self):
		self.ws.recv()
		self.ws.send('{"t":"d","d":{"a":"s","r":0,"b":{"c":{"sdk.android.19-4-0":1}}}}')
		self.ws.send('{"t":"d","d":{"a":"q","r":1,"b":{"p":"\/","h":""}}}')
		self.ws.recv()

	def initialSetup(self):
		data=(json.loads(self.ws.recv()))["d"]["b"]["d"]
		# Selecting the live match
		for i in data:
			if (data[i]['con']['mstus']=='L'):
				self.match=i
				if (input('*** '+data[i]["t1"]["f"]+" VS "+data[i]["t2"]["f"]+"   Press Y for this match or N for other match:    ").lower()=='y'):
					break

		if (self.match!=None):
			self.data["stadium"]=data[self.match]["con"]["g"]
			self.data["matchType"]=data[self.match]["con"]["sr"]
			self.data["toss"]=data[self.match]["con"]["lt"]
			self.data["team1"]=data[self.match]["t1"]["f"]
			self.data["team2"]=data[self.match]["t2"]["f"]
		else:
			print("No current live match")
			exit()

		self.parseData(data[self.match],self.match)
		self.ws.recv()

	def parseData(self,data,match):
		if (match!=self.match):
			return
		for i in self.params:
			if (i in data):
				self.data[self.params[i]]=data[i]

	def update_process(self):
		data=json.loads(self.ws.recv())
		try:
			self.parseData(data["d"]["b"]["d"],data["d"]["b"]["p"])
		except Exception:
			print("failed at",data)
		self.printScren()

	def continous_update(self):
		while True:
			self.update_process()

	def printScren(self):
		os.system('cls')
		data=self.data
		player1Score=data['player1Score'].split(',')

		data['Player1']=data['Player1'].replace(' *','')
		data['Player2']=data['Player2'].replace(' *','')
		
		if (data["position"]=='p1'):
			data['Player1']+=' *'
		else:
			data['Player2']+=' *'
		try:
			data["DisplayCard"]["msg"]=self.indicates[data["DisplayCard"]["msg"]]
		except Exception:
			pass
		if (len(player1Score)>1):
			player1Score=player1Score[0]+'('+player1Score[1]+')'+'  [4-'+player1Score[2]+',6-'+player1Score[3]+']'
		else:
			player1Score=''
		player2Score=data['player2Score'].split(',')
		if (len(player2Score)>1):
			player2Score=player2Score[0]+'('+player2Score[1]+')'+'  [4-'+player2Score[2]+',6-'+player2Score[3]+']'
		else:
			player2Score=''
		matter='                    '+data['matchType']+'\n'+'                           '+data['team1']+'  vs  '+data['team2']+'\n'+'-'*60+'\n'+'                        '+data['DisplayCard']['msg']+'\n'+'-'*60+'\n'+'    innings1                                innings2\n'+'    '+data['innings1Score']['sc']+'-'+data['innings1Score']['wk']+'                                       '+data['innings2Score']['sc']+'-'+data['innings2Score']['wk']+'\n'+'    '+data['innings1Score']['ov']+'                                         '+data['innings2Score']['ov']+'\n'+'-'*60+'\n'+'     '+data['Player1']+'  : '+player1Score+'\n'+'     '+data['Player2']+'  : '+player2Score+'\n'+'     Bowler  : '+data['bowler']+'\n'+'-'*60+'\n'+'     Latest Wicket:   '+data['lastWicket']+'\n'+'     Last 24 balls:   '+data['playerBoard']+'\n'+'-'*60
		print(matter)

liveProcess=CricLive('wss://criclive-72dee-43d33.firebaseio.com/.ws?ns=criclive-72dee-43d33&v=5')
liveProcess.continous_update()