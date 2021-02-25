import websocket
import json
import ssl
import sys
import os

class CricLive:
	def __init__(self,url):
		try:
			self.clearScreen()
			self.url=url
			self.ws = websocket.create_connection(self.url,sslopt={"cert_reqs": ssl.CERT_NONE})
			self.data={}
			self.match=None
			self.lineWidth=70
			self.indicates={"B":"Ball Started","BS":"Bowler Stopped","WK":"Wicket","OC":"Over Completed","WD":"Wide","FH":"Free Hit","C":"Cancel"}
			self.params={"p1":"Player1","p2":"Player2","b1s":"player1Score","b2s":"player2Score","bw":"bowler","lw":"lastWicket",
						 "i1":"innings1Score","i2":"innings2Score","i":"inningsNow","pb":"playerBoard","cs":"DisplayCard",
						 "os":"position"}
			self.initialLoad() # Loading the preLoaders
			self.initialSetup() # Loading for initial setup
		except KeyboardInterrupt:
			print("Thank you,see you soon")

	def clearScreen(self):
		# For clearing screen
		if (sys.platform=='win32'):
			os.system('cls')
		else:
			os.system('clear')

	def initialLoad(self):
		self.ws.recv()
		self.ws.send('{"t":"d","d":{"a":"s","r":0,"b":{"c":{"sdk.android.19-4-0":1}}}}')
		self.ws.send('{"t":"d","d":{"a":"q","r":1,"b":{"p":"\/","h":""}}}')
		self.ws.recv()

	def initialSetup(self):
		data=(json.loads(self.ws.recv()))["d"]["b"]["d"]
		# Selecting the live match
		for i in data:
			try:
				if (data[i]['con']['mstus']=='L'):
					if (input('*** '+data[i]["t1"]["f"]+" VS "+data[i]["t2"]["f"]+"   Press Y for this match or N for other match:    ").lower()=='y'):
						self.match=i
						break
			except Exception:
				print("failed for",end=' ')
				print(data[i],"issue @https://github.com/datta07/Live-Cricket-Scores/")

		if (self.match!=None):
			self.data["stadium"]=data[self.match]["con"]["g"]
			self.data["matchType"]=data[self.match]["con"]["sr"]
			self.data["toss"]=data[self.match]["con"]["lt"]
			self.data["team1"]=data[self.match]["t1"]["f"]
			self.data["team2"]=data[self.match]["t2"]["f"]
		else:
			print("NO MORE ONGOING LIVE MATCHS..., COME BACK LATER")
			exit()

		self.parseData(data[self.match],self.match)
		self.ws.recv()

	def parseData(self,data,match):
		if (match!=self.match):
			return
		for i in self.params:
			if (i in data):
				self.data[self.params[i]]=data[i]
		self.printScren()

	def update_process(self):
		data=json.loads(self.ws.recv())
		try:
			self.parseData(data["d"]["b"]["d"],data["d"]["b"]["p"])
		except Exception:
			print("failed at",data)

	def continous_update(self):
		while True:
			self.update_process()

	def spacingEdge(self,keywords):
		if (len(keywords)==1):
			lenght=(self.lineWidth-len(keywords[0]))//2
			return ' '*lenght+keywords[0]+'\n'
		elif (len(keywords)==2):
			lenght=(self.lineWidth-len(keywords[0])-len(keywords[1]))
			return keywords[0]+' '*lenght+keywords[1]+'\n'

	def freeLine(self):
		return '-'*self.lineWidth+'\n'

	def printScren(self):
		self.clearScreen()
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

		matter=self.spacingEdge([data['matchType']])+self.spacingEdge([data['team1']+'  vs  '+data['team2']])+self.freeLine()+self.spacingEdge([data['DisplayCard']['msg']])+self.freeLine()+self.spacingEdge(['     '+data['team1']+'(i1)',data['team2']+'(i2)'+'     '])+self.spacingEdge(['       '+data['innings1Score']['sc']+'-'+data['innings1Score']['wk'],data['innings2Score']['sc']+'-'+data['innings2Score']['wk']+'        '])+self.spacingEdge(['       '+data['innings1Score']['ov'],data['innings2Score']['ov']+'        '])+self.freeLine()+'     '+data['Player1']+'  : '+player1Score+'\n'+'     '+data['Player2']+'  : '+player2Score+'\n'+'     Bowler  : '+data['bowler']+'\n'+self.freeLine()+'     Latest Wicket:   '+data['lastWicket']+'\n'+'     Last 24 balls:   '+data['playerBoard']+'\n'+self.freeLine()
		print(matter)

liveProcess=CricLive('wss://criclive-72dee-43d33.firebaseio.com/.ws?ns=criclive-72dee-43d33&v=5')
liveProcess.continous_update()
