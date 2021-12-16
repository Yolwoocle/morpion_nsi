	# By Yolwoocle and Notgoyome
# Léo BERNARD et Guillaume TRAN TG04

# Importations

import pygame
import sys
import math
import random
import time

# Classes
class Joueur:
	def __init__(self, nom, symb):
		self.nom = nom
		self.symb = symb
		if symb == "x":
			self.image = image_x
			self.couleur = (50, 132, 100)
			self.couleur2 = (18, 32, 32)
			self.image_curseur = image_curseur_x
		elif symb == "o":
			self.image = image_o
			self.couleur = (180, 32, 42)
			self.couleur2 = (59, 23, 37)
			self.image_curseur = image_curseur_o
		else: 
			# Valeurs par défaut
			self.image = image_dot
			self.couleur = (205, 247, 226)
			self.couleur2 = (33, 45, 72)
			self.image_curseur = image_curseur

	def __str__(self):
		f"nom: {self.nom} \n symbole: {self.symb}"

class Bouton:
	def __init__(self, index, pos, size):
		self.index = index
		self.pos = pos
		self.size = size
		self.offset = (0, 0)

	def est_survole(self):
		souris_x, souris_y = pygame.mouse.get_pos()
		w = espace_entre_cases / 2
		contact_x = self.pos[0] - w <= souris_x < self.pos[0] + self.size[0] + w
		contact_y = self.pos[1] - w <= souris_y < self.pos[1] + self.size[1] + w
		contact = contact_x and contact_y
		self.survole = contact
		return contact

	def est_clique(self, clic_gauche):
		bouton_x, bouton_y = self.pos[0], self.pos[1]
		if self.survole:
			if clic_gauche:
				return True
		return False



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
		self.pos_cursor = [-64, -64]
	
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
		combinaisons = []
		# TODO: opti en stockant plutot que générer à chaque fois 
		for ligne in range(n):
			combinaisons.append([(ligne, case) for case in range(n)])
		for colonne in range(n):
			combinaisons.append([(case, colonne) for case in range(n)])
		combinaisons.append([(case, case) for case in range(n)])
		combinaisons.append([(case, n-1 - case) for case in range(n)])

		# On vérifie les combinaisons
		for comb in combinaisons:
			aligne = True
			last_char = self.valeur(comb[0])
			for pos in comb:
				if self.valeur(pos) != last_char:
					aligne = False
			if aligne and last_char != 0:
				return last_char
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
				self.boutons[i].append(Bouton((i, j), (x + j*w, y + i*w), image_res))
	
	def interaction_boutons(self, clic_gauche):
		for ligne in self.boutons:
			for bouton in ligne:
				if bouton.est_survole():
					self.selection = bouton
				if bouton.est_clique(clic_gauche) and self.est_vide(bouton.index): 
					return bouton.index
		return None

	def animer_curseur(self, dt):
		if self.selection:
			self.pos_cursor[0] += ((self.selection.pos[0]) - self.pos_cursor[0]) * dt * 20
			self.pos_cursor[1] += ((self.selection.pos[1]) - self.pos_cursor[1]) * dt * 20

	def afficher_grille(self, joueur):
		# Grille
		for ligne in self.boutons:
			for bouton in ligne:
				case = self.table[bouton.index[0]][bouton.index[1]]
				image = image_dot
				if case == "x":
					image = image_x
				elif case == "o":
					image = image_o
				screen.blit(pygame.transform.scale(image, image_res), bouton.pos)
		# Afficher curseur
		# TODO: 4 sprites curseur
		w = image_size / 2
		corners = ((0,0,w,w),(0,w,w,w),(w,0,w,w),(w,w,w,w))
		offset = ((-1,-1),(-1,1),(1,-1),(1,1))
		for i in range(4):
			crop = corners[i]
			ox, oy = offset[i]
			dist = math.sin(pygame.time.get_ticks()/100) * 4 + 8
			pos = (self.pos_cursor[0] + crop[0] + ox*dist, self.pos_cursor[1] + crop[1] + oy*dist)
			screen.blit(pygame.transform.scale(joueur.image_curseur, image_res), pos, crop)


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
		if self.tour >= 9:
			return True
		return False
		
	def main(self):
		prev_time = time.time()
		victoire = None

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
			self.grille.animer_curseur(dt) 

			if choix:
				self.grille.changer_val(choix[0], choix[1], self.jactuel.symb)
				victoire = self.grille.victoire()
				print(self.tour)
				
				self.tour_suivant()
						
			# On dessine la grille
			screen.fill(blanc)
			self.grille.afficher_grille(self.jactuel)

			# Affichage du texte
			text = ""
			if victoire:
				text = f"{victoire} a gagné!"
				print(f"{victoire} a gagné!")
			textsurface = small_font.render(text, False, (0, 0, 0))
			screen.blit(textsurface,(0,0))

			# On affiche tout sur l'écran 
			pygame.display.flip()


# Variables globales
taille_ecran = l_ecran, h_ecran = 640, 480
noir = (0, 0, 0)
blanc = (255, 255, 255)
pygame.display.set_caption("Morpion par Léo et Guillaume")
screen = pygame.display.set_mode(taille_ecran)

# Importation des images
image_curseur = pygame.image.load("images/cursor.png")
image_curseur_o = pygame.image.load("images/cursor_o.png")
image_curseur_x = pygame.image.load("images/cursor_x.png")
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