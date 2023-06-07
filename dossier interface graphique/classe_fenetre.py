# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 18:27:18 2023

@author: Anna Gondret
"""
import pygame
import sys
from pygame.locals import *
import time

class Fenetre(pygame.sprite.Sprite):
    def __init__(self):
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
        self.temps_changement_position=1500
        self.x,self.y=self.avancer
        self.x_pre,self.y_pre=self.gauche

        self.pivo=0
        self.pivo_avant=0
        self.pivo_gauche=90
        self.pivo_arriere=180
        self.pivo_droite=270  
        
        self.valeur_deplacment=2
        
        
    def update(self):
        #print("update")
        self.mouse = pygame.mouse.get_pos() 
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
        if self.temps_total >= self.temps_changement_position:
            self.position_index = (self.position_index + 1) % len(self.positions)
            self.x, self.y = self.positions[self.position_index]
            self.x_pre, self.y_pre=self.positions[self.position_index-1]
            self.temps_total = 0
            
        
        
        # if self.valeur_deplacment==1:
        #     self.pivo=self.pivo_avant
        # if self.valeur_deplacment==2: 
        #     self.pivo=self.pivo_droite
        # if self.valeur_deplacment==3:
        #     self.pivo=self.pivo_arriere
        # if self.valeur_deplacment==4: 
        #     self.pivo=self.pivo_gauche
            
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
        self.direction=self.position_index
        return self.direction
        #print (self.direction)
        #pass


fenetre = Fenetre()

while True:
    
    fenetre.update()
    fenetre.get_mouvement()
    dir=fenetre.get_mouvement()
    print(dir)
