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
		self.isAI = False
		
		# Valeurs par défaut
		self.image = image_dot
		self.couleur = (205, 247, 226)
		self.couleur2 = (33, 45, 72)
		self.image_curseur = image_curseur

	def initialiser(self, symb):
		self.symb = symb
		self.isAI = False
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
		elif symb == "tri":
			self.image = image_tri
			self.couleur = (180, 32, 42)
			self.couleur2 = (59, 23, 37)
			print(symb)
			self.image_curseur = image_curseur_tri
		elif symb == "sq":
			self.image = image_sq
			self.couleur = (180, 32, 42)
			self.couleur2 = (59, 23, 37)
			print(symb)
			self.image_curseur = image_curseur_sq
		else: 
			# Valeurs par défaut
			self.image = image_dot
			self.couleur = (205, 247, 226)
			self.couleur2 = (33, 45, 72)
			self.image_curseur = image_curseur

	def __str__(self):
		return f"nom: {self.nom} \n symbole: {self.symb}"

states = 0
######## AI OPPONENT ##########
class IA_Joueur(Joueur):
	def __init__(self, nom, symb, difficulte=0):
		super().__init__(nom, symb)
		self.difficulte = difficulte
		self.isAI = True

	def symb_oppose(self, nom):
		if nom == "j1":
			return "j2"
		return "j1"

	def jouer(self, grille, tour):
		choix_possibles = grille.cases_vides()
		if len(choix_possibles) == 0:
			return None
		return random.choice(choix_possibles)
		
		self.choice = None
		self.minimax(grille, self.symb, tour)
		return self.choice

	def minimax(self, grille, symb, couche=0):
		# Algorithme minimax récursif
		moves = grille.cases_vides()
		score = grille.score(symb)
		if len(moves) == 0 or score != 0:
			return grille.score(symb)
		if couche >= 9:
			return 0

		scores = []

		# On génère le score de toutes les possibilités possibles
		for move in moves:
			# TODO: c'est giga pas opti niveau mémoire
			grille_possible = Grille(grille.n)
			grille_possible.table = [i[:] for i in grille.table]
			grille_possible.changer_val(move, symb)

			for i in grille_possible.table:
				pass
				#print(i)
			#print("--------")
			# TODO: adaptable à n nombre de joueurs
			symb = self.symb_oppose(symb)
			scores.append(self.minimax(grille_possible, symb, couche+1))

		if couche < 5:
			return 0

		if symb == self.symb:
			# Joueur maximisant
			# On trouve l'index du score maximisant
			max_i = 0
			for i in range(1, len(scores)):
				if scores[i] > scores[max_i]:
					max_i = i
			self.choice = moves[max_i]
			return scores[max_i]
		else:
			# On sélectionne le meilleur score pour le joueur minimisant
			min_i = 0
			for i in range(1, len(scores)):
				if scores[i] > scores[min_i]:
					min_i = i
			return scores[min_i]
		

######## BOUTON ########
class Bouton:
	def __init__(self, index, pos, size):
		self.index = index
		self.pos = pos
		self.size = size
		self.offset = (0, 0)
		self.survole = False
		self.bounce = False

	def est_survole(self):
		souris_x, souris_y = pygame.mouse.get_pos()
		w = espace_entre_cases / 2
		contact_x = self.pos[0] - w <= souris_x < self.pos[0] + self.size[0] + w
		contact_y = self.pos[1] - w <= souris_y < self.pos[1] + self.size[1] + w
		contact = contact_x and contact_y
		self.survole = contact
		return contact

	def est_clique(self, clic_gauche):
		if self.est_survole():
			if clic_gauche:
				return True
		return False

###################### CASE ######################
class Case:
	def __init__(self, pos, val):
		self.pos = pos
		self.val = val

	def __str__(self):
		return f"position : {self.pos}\nvaleur : {self.val}"


################## GRILLE #####################
class Grille:
	def __init__(self, largeur=3):
		self.n = largeur
		self.table = [[0]* largeur for i in range(largeur)]
		self.initialiser_boutons()
		self.selection = None
		self.cursor = Cursor([-84, -84])
		self.n_animation= 0
	
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

	def est_vide(self, index):
		return self.table[index[0]][index[1]] == 0

	def changer_val(self, i, j, symbole=None):
		if symbole == None:
			self.table[i[0]][i[1]] = j
		else:
			self.table[i][j] = symbole
	
	def valeur(self, index, j=None):
		if j == None:
			return self.table[index[0]][index[1]]
		return self.table[index][j]

	def lire_bouton(self, index, j=None):
		if j == None:
			return self.boutons[index[0]][index[1]]
		return self.boutons[index][j]
	
	def score(self, symb):
		victoire = self.victoire()
		if not victoire or victoire == "match nul":
			return 0 
		elif victoire == symb:
			return 1
		else:
			return -1 
	
	def victoire(self, tour=0):
		table = self.table
		n = self.n
		combinaisons = []
		# TODO: opti en stockant plutot que générer à chaque fois 
		# On génère toutes les combinaisons
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
				# En cas de victoire
				for pos in comb:
					self.lire_bouton(pos).bounce = True 
				return last_char

		if tour >= n*n:
			return "match nul"
		return False
	
	def cases_vides(self):
		mouvs = []
		for i in range(self.n):
			for j in range(self.n):
				if self.table[i][j] == 0:
					mouvs.append((i,j))
		return mouvs
	
	def interaction_boutons(self, clic_gauche):
		for ligne in self.boutons:
			for bouton in ligne:
				if bouton.est_survole():
					self.selection = bouton
				if bouton.est_clique(clic_gauche) and self.est_vide(bouton.index): 
					self.cursor.width = -8
					self.cursor.anim_timer = 0
					return bouton.index
		return None

	def animer_curseur(self, dt):
		self.cursor.animate(dt)
		if self.selection:
			self.cursor.pos[0] += ((self.selection.pos[0]) - self.cursor.pos[0]) * dt * 20
			self.cursor.pos[1] += ((self.selection.pos[1]) - self.cursor.pos[1]) * dt * 20
		

	def afficher_grille(self, joueur):
		# Grille
		for ligne in self.boutons:
			for bouton in ligne:
				case = self.valeur(bouton.index)
				image = image_dot
				for i in range(len(liste_symbolestr)):
					if case == liste_symbolestr[i]:
						image = liste_symbole[i]
				
				x, y = bouton.pos
				x += bouton.offset[0]
				y += bouton.offset[1]
				if bouton.bounce:
					for i in range(len(liste_symbolestr)):
						if case == liste_symbolestr[i]:
							index_animation = i
       
					offset = bouton.index[0] + 1.65 * bouton.index[1]
					y += math.sin(pygame.time.get_ticks()/100 + offset) * 20

					#print(str(case))
					image = liste_symbole_animation[index_animation][int((round(pygame.time.get_ticks()/67))%len(liste_symbole_animation[index_animation]))]
				screen.blit(pygame.transform.scale(image, image_res), (x, y))
		# Afficher curseur
		# TODO: sélparer curseur dans sa classe
		self.cursor.draw(joueur)

###################### CURSOR ######################
class Cursor:
	def __init__(self, pos):
		self.pos = list(pos)
		self.width = 0
		self.visible = True
		self.anim_timer = 0

	def animate(self, dt):
		self.anim_timer += dt * 1000
		self.width *= 0.9

	def draw(self, joueur):
		if self.visible:
			w = image_size / 2
			corners = ((0,0,w,w),(0,w,w,w),(w,0,w,w),(w,w,w,w))
			offset = ((-1,-1),(-1,1),(1,-1),(1,1))
			for i in range(4):
				crop = corners[i]
				ox, oy = offset[i]
				#dist = math.sin(pygame.time.get_ticks()/100) * 4 + 8 
				dist = math.sin(self.anim_timer/100) * 4 + 8 
				dist += self.width
				pos = (self.pos[0] + crop[0] + ox*dist, self.pos[1] + crop[1] + oy*dist)
				screen.blit(pygame.transform.scale(joueur.image_curseur, image_res), pos, crop)

###################### JEU ######################
class Jeu:
	def __init__(self, joueur1, joueur2):
		self.joueurs = [joueur1, joueur2]
		
		self.jactuel_index = 0
		self.jactuel = self.joueurs[0]
		self.tour = 1
  
		self.game_over = False

		self.game_over = False
		self.grille = Grille(3)
		self.actif = True
		self.menu = True
		self.fin_selection = 0
		self.ini = True
		self.symbole_pris = None

	def joueur_actuel(self):
		return self.jactuel

	def tour_suivant(self):
		self.tour += 1
		self.jactuel_index += 1
		self.jactuel_index %= len(self.joueurs)
		self.jactuel = self.joueurs[self.jactuel_index]
	
	def match_nul(self):
		return self.tour >= 9
		
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


			# Delta time
			clock.tick(60)
			now = time.time()
			dt = now - prev_time
			prev_time = now

            # On dessine la grille
			screen.fill(blanc)
			if not self.menu:
				if self.ini:

					self.test = True
					self.jactuel_index = random.randint(0,1)
					self.jactuel = self.joueurs[self.jactuel_index]
					self.grille.afficher_grille(self.jactuel)
					self.grille = Grille(3)
					self.tour = 0
					self.ini = False
					self.time = 0

				# Choix
				choix = None
				if self.jactuel.isAI:
					choix = self.jactuel.jouer(self.grille, self.tour)
				else:
					choix = self.grille.interaction_boutons(clic_gauche)
				self.grille.animer_curseur(dt) 

				if choix !=None:
					pass
					#print(choix)
				if choix != None:
					sfx_place.play()
					self.grille.changer_val(choix, self.jactuel.symb)
					victoire = self.grille.victoire(self.tour)
					self.tour_suivant()

			# Affichage du texte
			text = ""
			if victoire:
				self.grille.cursor.visible = False
				self.game_over = True
				text = f"{victoire} gagne!"

			# Affichage du texte
			text = 'J' + str(self.jactuel_index + 1)
			if victoire:
				text += " gagne!"
				
				if self.time == 0:
					sfx_win.play()

				self.time += 1
				#print(self.time//60)
				if self.time//60 == 5:
					jeu = Jeu(j1, j2)
					jeu.main()	

			textsurface = small_font.render(text, False, (0, 0, 0))
			screen.blit(textsurface,(0,0))

			#textsurface = small_font.render(text, False, (0, 0, 0))
			#screen.blit(textsurface,(0,0))

			# On dessine la grille
			self.grille.afficher_grille(self.jactuel)
			if victoire:
				pass
			
			# Menu
			if self.menu == True:
				screen.fill(blanc)
				text_selection = liste_joueur[self.jactuel_index]
				selection = small_font.render(text_selection, False, noir)
				selection_x = (l_ecran - small_font.size(text_selection )[0])/2
				screen.blit(selection,(selection_x,0))
				#affichage des symboles
				
				gap = (l_ecran - n_symbole*image_size)/(n_symbole+1)
				y_pos_symbole = (h_ecran-image_size)/2
				liste_bouton = []
				for n in range(n_symbole):
					x_pos_symbole = (n+1)*gap+image_size*n
					liste_bouton.append(Bouton(n,(x_pos_symbole,y_pos_symbole),image_res))
					
					new_res = (image_res[0]*1.2, image_res[1]*1.2)
					new_res = ( int(new_res[0]), int(new_res[1]) )

					if self.symbole_pris == n: #pin
						screen.blit(pygame.transform.scale(image_dot, new_res), (x_pos_symbole-(image_res[0]*0.2)/2, y_pos_symbole-(image_res[0]*0.2)/2))
					elif liste_bouton[n].est_survole() and self.symbole_pris != n:
						screen.blit(pygame.transform.scale(liste_symbole[n], new_res), (x_pos_symbole-(image_res[0]*0.2)/2, y_pos_symbole-(image_res[0]*0.2)/2))
					else:
						screen.blit(pygame.transform.scale(liste_symbole[n], image_res), (x_pos_symbole,y_pos_symbole))

					if liste_bouton[n].est_clique(clic_gauche) and self.symbole_pris != n:
						
						self.jactuel = self.joueurs[self.jactuel_index]
						self.jactuel.initialiser(liste_symbolestr[n])
						sfx_place.play()
						
						self.jactuel_index = (self.jactuel_index+1)%2
						self.fin_selection += 1	
						self.symbole_pris = n
				
						
				#condition enlever menu
				if self.fin_selection == len(liste_joueur):
					self.menu = False

			# On affiche tout sur l'écran 
			pygame.display.flip()


# Variables globales
taille_ecran = l_ecran, h_ecran = 640, 480
noir = (0, 0, 0)
blanc = (255, 255, 255)
vert = (50, 132, 100)
rouge = (180, 32, 42)

pygame.display.set_caption("Morpion par Léo et Guillaume")
screen = pygame.display.set_mode(taille_ecran)

# Importation des images
image_curseur = pygame.image.load("images/cursor.png")
image_curseur_o = pygame.image.load("images/cursor_o.png")
image_curseur_x = pygame.image.load("images/cursor_x.png")
image_curseur_tri = pygame.image.load("images/cursor_tri.png")
image_curseur_sq = pygame.image.load("images/cursor_sq.png")

image_o = pygame.image.load("images/o.png")
image_x = pygame.image.load("images/x.png")
image_tri = pygame.image.load("images/tri.png")
image_dot = pygame.image.load("images/dot.png")
image_sq = pygame.image.load("images/sq.png")
image_size = 64
image_res = (image_size, image_size)
espace_entre_cases = 10

#importation des images animations
animation_x = []
animation_x.append(pygame.image.load('images/x_animation/x1.png'))
animation_x.append(pygame.image.load('images/x_animation/x2.png'))
animation_x.append(pygame.image.load('images/x_animation/x3.png'))
animation_x.append(pygame.image.load('images/x_animation/x4.png'))
animation_x.append(pygame.image.load('images/x_animation/x5.png'))
animation_x.append(pygame.image.load('images/x_animation/x6.png'))
animation_x.append(pygame.image.load('images/x_animation/x7.png'))
animation_x.append(pygame.image.load('images/x_animation/x8.png'))

animation_o = []
animation_o.append(pygame.image.load('images/o_animation/o1.png'))
animation_o.append(pygame.image.load('images/o_animation/o2.png'))
animation_o.append(pygame.image.load('images/o_animation/o3.png'))
animation_o.append(pygame.image.load('images/o_animation/o4.png'))
animation_o.append(pygame.image.load('images/o_animation/o5.png'))
animation_o.append(pygame.image.load('images/o_animation/o6.png'))
animation_o.append(pygame.image.load('images/o_animation/o7.png'))
animation_o.append(pygame.image.load('images/o_animation/o8.png'))


animation_sq = []
animation_sq.append(pygame.image.load('images/sq_animation/sq1.png'))
animation_sq.append(pygame.image.load('images/sq_animation/sq2.png'))
animation_sq.append(pygame.image.load('images/sq_animation/sq3.png'))
animation_sq.append(pygame.image.load('images/sq_animation/sq4.png'))
animation_sq.append(pygame.image.load('images/sq_animation/sq5.png'))
animation_sq.append(pygame.image.load('images/sq_animation/sq6.png'))
animation_sq.append(pygame.image.load('images/sq_animation/sq7.png'))

# Sons
pygame.mixer.init()
sfx_place = pygame.mixer.Sound('sfx/place.mp3')
sfx_win = pygame.mixer.Sound('sfx/win.mp3')


animation_tri = animation_o 
frame_actuelle = 0
# Intéraction 
clic_gauche = False

# Initialisation du texte
pygame.font.init() 
small_font = pygame.font.Font('font/8-bit-hud.ttf', 30)

# Initialisation du jeu
j1_name = "j1"
j2_name = "j2"
j1 = Joueur("j1", "x")
j2 = Joueur("j2", "o")
#j2 = IA_Joueur("j2", "o")

liste_joueur = ["j1","j2"]
liste_symbole = [image_o,image_x,image_tri,image_sq]
liste_symbolestr = ['o','x','tri','sq']
liste_symbole_animation = [animation_o,animation_x,animation_tri,animation_sq]
n_symbole = len(liste_symbole)
grille = Grille(3)

pygame.font.init()
clock = pygame.time.Clock()

jeu = Jeu(j1, j2)
jeu.main()	
