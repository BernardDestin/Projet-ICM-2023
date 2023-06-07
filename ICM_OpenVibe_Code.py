"""
ICM_OpenVibe_Code.py
Réalisé par Gatien AUBRY
Tous droits réservés
"""
import numpy as np
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import warnings
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
import pygame
import sys
from pygame.locals import *
import time

#Connexion
import paho.mqtt.publish as publish

class MyOVBox(OVBox):
	def __init__(self):
		"""Création de la classe de la Box OpenVibe"""
		OVBox.__init__(self)
		self.signalHeader = None
		self.models = []
		self.debugage = ""
		self.donnes = []
		self.positifs = 0
		self.precedente = -666
		self.a = 0
		self.b = 0
		self.c = 0
		self.d = 0
		#Désactivation des warnings de version futures
		warnings.simplefilter(action='ignore', category=FutureWarning)

		self.MQTT_SERVER = "172.20.10.6"
		self.MQTT_PATH = "test_channel"
		self.boool = True

		self.__init__Tkinter()
		self.updateTk()
		self.directionsTxt = ["forward", "right", "backward", "left"]
	
	def initialize(self):
		##A l'initialisation
		#Chargement des modèles
		
		self.models.append(('LR', LogisticRegression(solver='liblinear', multi_class='ovr')))
		self.models.append(('LDA', LinearDiscriminantAnalysis()))
		self.models.append(('KNN', KNeighborsClassifier()))
		self.models.append(('CART', DecisionTreeClassifier()))
		self.models.append(('NB', GaussianNB()))
		"""
		#self.models.append(('LR', joblib.load("C:\Applications\Model_V2_LR.joblib")))
		self.models.append(('LDA', joblib.load("C:\Applications\Model_V2_C_LDA.joblib")))
		self.models.append(('KNN', joblib.load("C:\Applications\Model_V2_C_KNN.joblib")))
		self.models.append(('CART', joblib.load("C:\Applications\Model_V2_C_CART.joblib")))
		self.models.append(('NB', joblib.load("C:\Applications\Model_V2_C_NB.joblib")))
		"""
		#Chargement des données des modèles
		dataset=read_csv("C:\Applications\papuche_V2_C.csv")
		#Insertion des données dans les modèles
		array = dataset.values
		X = array[:,1:10]
		y = array[:,10]
		X_train, X_validation, Y_train, Y_validation = train_test_split(X, y, test_size=0.10, random_state=2)
		#print(X_train[1])
		#print(X_validation[1])
		kfold = StratifiedKFold(n_splits=10, random_state=1, shuffle=True)
		for name, model in self.models :
			cv_results = cross_val_score(model, X_train, Y_train, cv=kfold, scoring='accuracy')
			model.fit(X_train, Y_train)
			predictions = model.predict(X_validation)
			print(classification_report(Y_validation, predictions))
		print("finished")

	def process(self):
		##Main loop (lancé à chaque itération)
		#Analyse des données d'entrée
		for chunkIndex in range(len(self.input[0])):
			if(type(self.input[0][chunkIndex]) == OVSignalHeader): #Si c'est un header (début de transmission)
				tps = self.input[0].pop()
				self.header(tps)
			elif(type(self.input[0][chunkIndex]) == OVSignalBuffer): #Si ce sont des données utiles
				infos = self.input[0].pop()
				numpyBuffer = np.array(infos).reshape(tuple(self.signalHeader.dimensionSizes))
				infos2 = numpyBuffer[1].tolist()
				tps = self.traitement(infos2)
				self.donnes += tps
				self.middle(infos2,infos)
			elif(type(self.input[0][chunkIndex]) == OVSignalEnd): #Si c'est une fin de transmission
				tps = self.input[0].pop()
				self.ending(self)
		#Lancement de l'analyse s'il y a suffisament de données
		if len(self.donnes) > 150 :
			rep = self.isAction(self.donnes[0:150])
			self.donnes = self.donnes[10:]
			if rep :
				self.positifs += 1
				self.donnes = self.donnes[140:]
				print("Double Clignotement")
				self.send(self.directionsTxt[self.get_mouvement()])
				print(self.directionsTxt[self.get_mouvement()])
		self.updateTk()
	
	def uninitialize(self):
		print(self.positifs)
		print("======"+str(self.a)+"="+str(self.b)+"="+str(self.c)+"="+str(self.d))
		return

	def traitement(self, tab):
		"""Fonction de traitement du signal, permet de lisser le signal afin de faciliter son analyse"""
		if (self.precedente == -666): self.precedente = tab[0]
		for i in range(len(tab)):
			tab[i] = tab[i] * 0.1 + self.precedente * 0.9
			self.precedente = tab[i]
		return tab

	def isAction(self, tab):
		"""Fonction d'analyse de signal permettant de détecter des clignements simples et doubles des yeux"""
		#Descripteurs
		pts1,pts2,pts3 = 0,0,0
		maxi1 = max(tab)
		pts1 = tab.index(maxi1)
		papuche = pts1
		if papuche >=140 : return False
		papuche += 1
		while tab[papuche] - tab[papuche-1] < 0:
			if papuche >=140 : return False
			papuche += 1
		mini1 = tab[papuche]
		pts2 = papuche
		papuche += 1
		while tab[papuche] - tab[papuche-1] > 0:
			if papuche >=140 : return False
			papuche += 1
		maxi2 = tab[papuche]
		pts3 = papuche
		papuche += 1
		while tab[papuche] - tab[papuche-1] < 0:
			if papuche >=140 : return False
			papuche += 1
		mini2 = tab[papuche]
		disti12 = pts1 - pts2
		disti23 = pts2 - pts3
		disti13 = pts1 - pts3
		meani = np.mean(tab)
		stdi = np.std(tab)
		#print("===="+str(pts1)+" "+str(pts2)+" "+str(pts3))
		stidiSpe = np.std(tab[pts1:pts3])
		ensemble = [maxi1,mini1,maxi2,mini2,disti12,disti23,disti13,meani,stidiSpe]
		
		#Lancement de l'analyse par les modèles d'IA
		NombreDePositif = 0
		test = 0
		for model in self.models:
			tempo = model[1].predict(np.array(ensemble).reshape(1,-1))
			if (tempo[0] == 0): self.a += 1
			if (tempo[0] == 1): 
				self.b += 1
				test += 1
			if (tempo[0] == 3):
				self.c += 1
				NombreDePositif += 1
				#print("detec")
			if (tempo[0] == 4): self.d += 1
		#if (test >= 3): print("Simple Clignotement")
		if (NombreDePositif >= 3):
			return True
		else :
			return False
	#Fonction de vérification :
	#Ces fonctions permettent de connaître l'état du signal analysé par le code python en le renvoyant à la sortie du bloc pour affichage
	def header(self, tps):
		self.signalHeader = tps
		outputHeader = OVSignalHeader(self.signalHeader.startTime,self.signalHeader.endTime,[1, self.signalHeader.dimensionSizes[1]],['Coucou']+self.signalHeader.dimensionSizes[1]*[''],self.signalHeader.samplingRate)
		self.output[0].append(outputHeader)
	def middle(self, infos, tps):
		chunk = OVSignalBuffer(tps.startTime, tps.endTime, infos)
		self.output[0].append(chunk)
	def ending(self, tps):
		self.output[0].append(tps)

	#Réseau
	def send(self,directionRobot):
		publish.single(self.MQTT_PATH, directionRobot, hostname=self.MQTT_SERVER) #send data 

	#Tkinter
	def __init__Tkinter(self):
		#super().__init__()  # Appel au constructeur de la classe parent Sprite
		# Initialisation de la fenêtre et autres variables
		pygame.init()
		self.width = 1250
		self.height = 660
		self.fond=(255,255,255)
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("fenetre de commande")
		self.screen.fill(self.fond)
		
		#IMAGES
		self.DEFAULT_IMAGE_SIZE = (150, 150)
		
		#image logo
		self.image_logo_O = pygame.image.load("logo_moving_brain.png").convert_alpha()
		self.image_logo = pygame.transform.scale(self.image_logo_O, (165,130))
		self.screen.blit(self.image_logo, (self.width-170,self.height-660))
		
		#image deplacement
		self.image_deplacement_O = pygame.image.load("fleche_deplacement.png").convert_alpha()
		self.image_deplacement = pygame.transform.scale(self.image_deplacement_O, self.DEFAULT_IMAGE_SIZE)
		#pygame.draw.circle(self.screen,'peach puff', (self.width-1025+75,self.height-520+75), 100)
		#self.screen.blit(self.image_deplacement, (self.width-1025,self.height-520))
 
		
		#image avant
		self.image_avant_O = pygame.image.load("fleche_haut.png").convert_alpha()
		self.image_avant = pygame.transform.scale(self.image_avant_O, self.DEFAULT_IMAGE_SIZE)
		self.screen.blit(self.image_avant, (self.width-400,self.height-575))
		#image arriere
		self.image_arriere_O = pygame.image.load('fleche_arriere.png').convert_alpha()
		self.image_arriere = pygame.transform.scale(self.image_arriere_O, self.DEFAULT_IMAGE_SIZE)
		self.screen.blit(self.image_arriere, (self.width-400,self.height-325))
		#image droite
		self.image_droite_O = pygame.image.load('fleche_droite.png').convert_alpha()
		self.image_droite = pygame.transform.scale(self.image_droite_O, self.DEFAULT_IMAGE_SIZE)
		self.screen.blit(self.image_droite, (self.width-250,self.height-450))
		
		self.image_gauche_O = pygame.image.load('fleche_gauche.png').convert_alpha()
		self.image_gauche = pygame.transform.scale(self.image_gauche_O, self.DEFAULT_IMAGE_SIZE)
		self.screen.blit(self.image_gauche, (self.width-550,self.height-450))
		
		#TEXTE
		self.smallfront = pygame.font.SysFont('Corbel',25,)
		self.mediumfont = pygame.font.SysFont('Corbel',35)
		self.bigfont = pygame.font.SysFont('Corbel',55,bold=True)
		#titre
		self.titre = self.bigfont.render('Interface de commande' , True , (0,0,0))
		self.screen.blit(self.titre , (self.width-1200,self.height-640))
		#instructions
		self.instructions1 = self.smallfront.render("Clignez deux fois des yeux lorsque la fleche correspondant" , True , (0,0,0))
		self.screen.blit(self.instructions1 , (self.width-1225,self.height-300))
		self.instructions2 = self.smallfront.render(" a la direction desiree et selectionnee, vous pourez" , True , (0,0,0))		
		self.screen.blit(self.instructions2 , (self.width-1225,self.height-250))
		self.instructions3 = self.smallfront.render(" constater la direction choisie grace a la fleche ci-dessus." , True , (0,0,0))
		self.screen.blit(self.instructions3 , (self.width-1225,self.height-200))
		self.instructions4 = self.smallfront.render(" Choisir deux fois la même direction pour s'arrêter." , True , (0,0,0))
		self.screen.blit(self.instructions4 , (self.width-1225,self.height-150))		
		#creation du boutton et du texte
		self.couleur_quitter_d=(100,100,100)
		self.couleur_quitter_l = (170,170,170) 
		pygame.draw.rect(self.screen,self.couleur_quitter_d,[self.width-190,self.height-90,140,40]) 
		self.text = self.mediumfont.render('Quitter' , True , (255,255,255) )
		self.screen.blit(self.text , (self.width-190+20,self.height-90+3))
		
		#element pour rotation toutes les 2 sec
		self.dif=90
		self.avancer=(self.width-400+self.dif,self.height-575+self.dif)
		self.reculer=(self.width-400+self.dif,self.height-325+self.dif)
		self.droite=(self.width-250+self.dif,self.height-450+self.dif)
		self.gauche=(self.width-550+self.dif,self.height-450+self.dif)
		
		
		
		self.clock = pygame.time.Clock()
		self.positions = [self.avancer, self.droite, self.reculer, self.gauche]
		self.position_index = 0
		self.temps_total=0
		self.temps_changement_position=2000
		self.x,self.y=self.avancer
		self.x_pre,self.y_pre=self.gauche

		self.pivo=0
		self.pivo_avant=0
		self.pivo_gauche=90
		self.pivo_arriere=180
		self.pivo_droite=270  
		
		self.valeur_deplacment=2

	def updateTk(self):
		#print("update")
		try :
			self.mouse = pygame.mouse.get_pos()
		except :
			return
		# fermeture de la fenetre en cas de clique sur la croix
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			
			#if the mouse is clicked on the button quitter the game is terminated
			if self.width-190 <= self.mouse[0] <= self.width-190+140 and self.height-90 <= self.mouse[1] <= self.height-90+40:
				pygame.draw.rect(self.screen,self.couleur_quitter_l,[self.width-190,self.height-90,140,40]) 
				self.screen.blit(self.text , (self.width-190+20,self.height-90+3))
				if event.type == pygame.MOUSEBUTTONDOWN: 
					print("quitter")
					pygame.quit()
					sys.exit()
			else:
					pygame.draw.rect(self.screen,self.couleur_quitter_d,[self.width-190,self.height-90,140,40])
					self.screen.blit(self.text , (self.width-190+20,self.height-90+3))


			#ajout du control de la fleche de deplacement par clique de sourie
			if event.type == pygame.MOUSEBUTTONDOWN: 
					#fleche avant
				if self.width-400 <= self.mouse[0] <= self.width-400+150 and self.height-575 <= self.mouse[1] <= self.height-575+150:
					self.pivo=self.pivo_avant
					#fleche arriere
				if self.width-400 <= self.mouse[0] <= self.width-400+150 and self.height-325 <= self.mouse[1] <= self.height-325+150:
					self.pivo=self.pivo_arriere
					#fleche droite
				if self.width-250 <= self.mouse[0] <= self.width-250+150 and self.height-450 <= self.mouse[1] <= self.height-450+150:
					self.pivo=self.pivo_droite
					#fleche gauche
				if self.width-550 <= self.mouse[0] <= self.width-550+150 and self.height-450 <= self.mouse[1] <= self.height-450+150:
					self.pivo=self.pivo_gauche
		
		
		#cercle de couleur qui change de position toutes les 1,5 sec
		pygame.draw.ellipse(self.screen,'light salmon', (self.x-105, self.y-105,90 * 2, 90 * 2),15) 
		pygame.draw.ellipse(self.screen,self.fond, (self.x_pre-105, self.y_pre-105,90 * 2, 90 * 2),15)
		self.temps_total += self.clock.get_time()
		if self.temps_total >= self.temps_changement_position+200:
			self.position_index = (self.position_index + 1) % len(self.positions)
			self.x, self.y = self.positions[self.position_index]
			self.x_pre, self.y_pre=self.positions[self.position_index-1]
			self.temps_total = 200
			
		
		
		# if self.valeur_deplacment==1:
		#	 self.pivo=self.pivo_avant
		# if self.valeur_deplacment==2: 
		#	 self.pivo=self.pivo_droite
		# if self.valeur_deplacment==3:
		#	 self.pivo=self.pivo_arriere
		# if self.valeur_deplacment==4: 
		#	 self.pivo=self.pivo_gauche
			
		#affichage de la fleche qui indique la direction choisi dans la bonne orientation
		pygame.draw.circle(self.screen,'peach puff', (self.width-1025+75,self.height-520+75), 100)
		self.image_deplacement_pivo=pygame. transform. rotate (self.image_deplacement, self.pivo)
		self.screen.blit(self.image_deplacement_pivo, (self.width-1025,self.height-520))
		#pygame.draw.ellipse(self.screen,'light salmon', (self.x-105, self.y-105,90 * 2, 90 * 2),15) 
		#pygame.draw.ellipse(self.screen,self.fond, (self.x_pre-105, self.y_pre-105,90 * 2, 90 * 2),15) 
	   


		pygame.display.flip()
		self.clock.tick(60)
		#pygame.display.flip()  # Mettez à jour l'affichage
		 
		#pygame.display.update()

	def get_mouvement(self):
		# recuperation de la valeur actuelle de la page
		return self.position_index
box = MyOVBox()
