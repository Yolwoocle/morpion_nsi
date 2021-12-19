	# By Yolwoocle and Notgoyome
# Léo BERNARD et Guillaume TRAN TG04

# Importations

import pygame
import sys
import math
import random
import time

# Fonctions 
def coloriser(image, col1, col2):
	#pixels = pygame.PixelArray(image)
	#pixels.replace(col1, col2)
	pass #pygame.transform.threshold(destsurface, surface, yellow, thresh, blue, 1, None, True)

# Classes
class Joueur:
	def __init__(self, nom, symb):
		self.nom = nom
		self.symb = symb
		if symb == "x":
			self.image = image_x
			self.couleur = (50, 132, 100)
			self.couleur2 = (18, 32, 32)
		elif symb == "o":
			self.image = image_o
			self.couleur = (180, 32, 42)
			self.couleur2 = (59, 23, 37)
		else: 
			# Valeurs par défaut
			self.image = image_dot
			self.couleur = (205, 247, 226)
			self.couleur2 = (33, 45, 72)

	
	def __str__(self):
		f"nom: {self.nom} \n symbole: {self.symb}"


class Case:
	def __init__(self, pos, val):
		self.pos = pos
		self.val = val

	def __str__(self):
		return f"position : {self.pos}\nvaleur : {self.val}"


class Grille:
	def __init__(self, largeur):
		self.n = largeur
		self.table = [[0]* largeur for i in range(largeur)]
		self.initialiser_boutons()
		self.selection = None
		self.pos_cursor = [0, 0]
	
	def est_vide(self, index):
		return self.table[index[0]][index[1]] == 0

	def changer_val(self, i, j, symbole):
		# todo chagner nom
		self.table[i][j] = symbole
	
	def valeur(self, index, j=None):
		if j == None:
			return self.table[index[0]][index[1]]
		return self.table[index][j]
	
	def victoire(self):
		table = self.table
		n = self.n
			
		# On vérifie les lignes - - - -
		for ligne in range(n):
			aligne = True
			if table[ligne][0] == 0:
				aligne = False
			for case in range(n-1):
				if table[ligne][case] != table[ligne][case + 1]:
					aligne = False
					break
			if aligne:
				return table[ligne][0] #pin
				
		# On vérifie les colonnes | | | |
		for colonne in range(n):
			aligne = True
			if table[0][colonne] == 0:
				aligne = False
			for case in range(n-1):
				if table[case][colonne] != table[case + 1][colonne]:
					aligne = False
					break
			if aligne:
				return table[0][colonne] #pin
		
		# On vérifie les diagonales \ \ \ 
		aligne = True
		if table[0][0] == 0:
			aligne = False
		for case in range(n-1):
			if table[case][case] != table[case+1][case+1]:
				aligne = False
		if aligne:
			return table[0][0]

		# On vérifie les diagonales / / /
		aligne = True
		if table[0][n-1] == 0:
			aligne = False
		for case in range(n-1):
			if table[case][n-1-case] != table[case+1][n-1-case-1]:
				aligne = False
		if aligne:
			return table[0][n-1]
			
		return False
	
	def initialiser_boutons(self):
		n = self.n
		l_grille = n * image_size + (n-1) * espace_entre_cases
		x = (l_ecran - l_grille) / 2
		y = (h_ecran - l_grille) / 2
		w = image_size + espace_entre_cases

		self.boutons = []
		for i in range(n):
			self.boutons.append([])
			for j in range(n):
				self.boutons[i].append({ "index": (i, j), "pos": (x + j*w, y + i*w) })
	
	def interaction_boutons(self, clic_gauche):
		souris_x, souris_y = pygame.mouse.get_pos()
		for ligne in self.boutons:
			for bouton in ligne:
				bouton_x = bouton["pos"][0]
				bouton_y = bouton["pos"][1]
				w = espace_entre_cases / 2
				contact_x = bouton_x - w <= souris_x < bouton_x + image_size + w
				contact_y = bouton_y - w <= souris_y < bouton_y + image_size + w
				if contact_x and contact_y:
					self.selection = bouton
					if clic_gauche and self.est_vide(bouton["index"]):
						return bouton["index"]
		return None

	def animer_curseur(self, dt):
		if self.selection:
			self.pos_cursor[0] += ((self.selection["pos"][0]) - self.pos_cursor[0]) * dt * 40
			self.pos_cursor[1] += ((self.selection["pos"][1]) - self.pos_cursor[1]) * dt * 40

	def afficher_grille(self, joueur):
		# Grille
		for ligne in self.boutons:
			for bouton in ligne:
				case = self.table[bouton["index"][0]][bouton["index"][1]]
				image = image_dot
				if case == "x":
					image = image_x
				elif case == "o":
					image = image_o
				screen.blit(pygame.transform.scale(image, image_res), bouton["pos"])
		# Afficher curseur
		# TODO: 4 sprites curseur
		coloriser(image_curseur, (205, 247, 226), joueur.couleur)
		screen.blit(pygame.transform.scale(image_curseur, image_res), self.pos_cursor)
  

		


class Jeu:
	def __init__(self, joueur1, joueur2):
		self.joueurs = [joueur1, joueur2]
		self.jactuel = self.joueurs[0]
		self.jactuel_index = 0
		self.tour = 0

		self.grille = Grille(3)
		self.actif = True
	
	def joueur_actuel(self):
		return self.jactuel

	def tour_suivant(self):
		self.tour += 1
		self.jactuel_index += 1
		self.jactuel_index %= len(self.joueurs)
		self.jactuel = self.joueurs[self.jactuel_index]
	
	def match_nul(self):
		if self.tour == 8:
			return True
		return False
		
	def main(self):
		prev_time = time.time()

		while self.actif:
			# Événements
			clic_gauche = False
			for event in pygame.event.get():
				if event.type == pygame.QUIT: 
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					clic_gauche = True

			# Limiter les FPS
			clock.tick(60)
			now = time.time()
			dt = now - prev_time
			prev_time = now

			choix = self.grille.interaction_boutons(clic_gauche)
			victoire = False 
			init = None
			self.grille.animer_curseur(dt) 

			if choix:
				self.grille.changer_val(choix[0], choix[1], self.jactuel.symb)
				victoire = self.grille.victoire()
				print(self.tour)
				
				self.tour_suivant()
			
			menu = True
			screen.fill(blanc)
   
			text_selection = 'yolwoocle est un pd'
			selection = small_font.render(text_selection, False, (0, 0, 0))
			selection_x = (644 - font.size(text_selection )[0])/2
			print(selection_x)
			screen.blit(selection,(selection_x,0))


			# On dessine la grille
			if menu != True:
				self.grille.afficher_grille(self.jactuel)
				if victoire:
					pass

				# Affichage du texte
				textsurface = small_font.render('Score : 5', False, (0, 0, 0))
				screen.blit(textsurface,(0,0))
			
   
			
			# On affiche tout sur l'écran 
			pygame.display.flip()

			if victoire:
				print("victoire pour", victoire)
				init = input("voulez vous recommencer ? o/n")
			elif jeu.match_nul():
				print("MATCH NUL BANDE DE NUL")
				init = input("voulez vous recommencer ? o/n")
			else: 
				init = False
			# Recommencer la partie ?
			if init == "o" :
				self.tour = 0
				self.grille = Grille(3)


# Variables globales
taille_ecran = l_ecran, h_ecran = 640, 480
noir = (0, 0, 0)
blanc = (255, 255, 255)
pygame.display.set_caption("Morpion par Léo et Guillaume")
screen = pygame.display.set_mode(taille_ecran)

# Importation des images
image_curseur = pygame.image.load("images/cursor.png")
images_curseur = [pygame.image.load(f"images/cu_{i}.png") for i in range(1, 5)]
image_o = pygame.image.load("images/o.png")
image_x = pygame.image.load("images/x.png")
image_tri = pygame.image.load("images/tri.png")
image_dot = pygame.image.load("images/dot.png")

image_size = 64
image_res = (image_size, image_size)
espace_entre_cases = 10

# Intéraction 
clic_gauche = False

# Initialisation du texte
pygame.font.init() 
small_font = pygame.font.Font('font/ReadexPro.ttf', 30)
font = pygame.font.Font("font/ReadexPro.ttf", 32)

# Initialisation du jeu
j1 = Joueur("Léo", "x")
j2 = Joueur("Guigui", "o")
grille = Grille(3)
jeu = Jeu(j1, j2)
pygame.font.init()
clock = pygame.time.Clock()


jeu.main()

