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

		self.signalHeader = None
	
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
			print("Double Clignotement")
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
box = MyOVBox()