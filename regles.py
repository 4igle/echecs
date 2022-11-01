from time import sleep
from copy import deepcopy
from random import shuffle


class Piece:
    def __init__(self, couleur):
        self.couleur = couleur
        self.c_adversaire = {'blanc': 'noir', 'noir': 'blanc'}

    @property
    def couleur(self):
        return self.__couleur

    @couleur.setter
    def couleur(self, c):
        if c not in {'noir', 'blanc'}:
            raise ValueError('La couleur de la pièce doit être "noir" ou "blanc".')
        self.__couleur = c

    def coup_met_pas_en_echec(self, passant_p, plateau_p, pieces_p, score_p, pos1, pos2):
        passant, plateau, pieces, score = (deepcopy(passant_p),
                                           deepcopy(plateau_p),
                                           deepcopy(pieces_p),
                                           deepcopy(score_p))
        couleur = self.couleur
        self.bouger(plateau, pieces, pos1, pos2)
        couleur_adverse = self.c_adversaire[couleur]
        case_roi = pieces[f'roi{couleur}']
        for case_piece in pieces[couleur_adverse]:
            # Si le déplacement est possible, et donc si il y a échec
            if deepcopy(plateau[case_piece]).deplacement_verif(case_piece, case_roi,
                                                               deepcopy(passant),
                                                               deepcopy(pieces),
                                                               deepcopy(plateau),
                                                               deepcopy(score),
                                                               True,
                                                               False):
                return False
        return True

    def bouger(self, plateau, pieces, pos1, pos2):
        tour_couleur = self.couleur
        couleur_adv = self.c_adversaire[tour_couleur]
        if plateau[pos1].nom == 'Roi':
            pieces[f'roi{tour_couleur}'] = pos2
        if pos1 != pos2:
            plateau[pos2] = plateau[pos1]
            plateau[pos1] = None
            pieces[tour_couleur].remove(pos1)
            pieces[tour_couleur].add(pos2)
        if pos2 in pieces[couleur_adv]:
            pieces[couleur_adv].remove(pos2)


class Pion(Piece):
    def __init__(self, couleur):
        super().__init__(couleur)
        self.__nom = 'Pion'
        self.__value = 1.0

    @property
    def value(self):
        return self.__value

    @property
    def nom(self):
        return self.__nom

    def deplacement_verif(self, pos1, pos2, passant, pieces, plateau, score, simulation, check_echec=True):
        def changer_piece():
            if simulation:
                plateau[pos1] = Dame(couleur)
                score[couleur] += 7.8
            else:
                piece = ""
                print()
                while piece not in {'dame', 'cavalier', 'tour', 'fou'}:
                    piece = input("Choisissez votre pièce (Tour/Cavalier/Fou/Dame) : ").lower()
                if piece == 'dame':
                    plateau[pos1] = Dame(couleur)
                    score[couleur] += 7.8
                if piece == 'cavalier':
                    plateau[pos1] = Cavalier(couleur)
                    score[couleur] += 2.2
                if piece == 'tour':
                    plateau[pos1] = Tour(couleur)
                    score[couleur] += 4.1
                if piece == 'fou':
                    plateau[pos1] = Fou(couleur)
                    score[couleur] += 2.33

        couleur = self.couleur
        sens = 1
        debut = '2'
        c_adversaire = 'noir'
        if couleur == 'noir':
            sens = -1
            debut = '7'
            c_adversaire = 'blanc'
        # Déplacement simple (vers l'avant)
        if pos1[0] == pos2[0] and plateau[pos2] is None:
            # avance de 1
            if int(pos2[1]) == int(pos1[1]) + sens:
                if not check_echec or self.coup_met_pas_en_echec(passant,
                                                                 plateau,
                                                                 pieces,
                                                                 score,
                                                                 pos1, pos2):
                    # si la pièce est au bout, elle est 6 lignes plus avancée que sa ligne de départ
                    if int(pos2[1]) == int(debut) + 6 * sens:
                        changer_piece()
                    return True
            # avance de 2
            elif (int(pos2[1]) == int(pos1[1]) + sens * 2 and
                  plateau[f"{pos1[0]}{int(pos1[1]) + sens}"] is None and
                  pos1[1] == debut):
                if not check_echec or self.coup_met_pas_en_echec(passant,
                                                                 plateau,
                                                                 pieces,
                                                                 score,
                                                                 pos1, pos2):
                    passant[couleur] = pos2
                    return True
        # Prise (diagonale)
        elif ((pos2[0] == chr(ord(pos1[0]) + 1) or pos2[0] == chr(ord(pos1[0]) - 1)) and
              int(pos2[1]) == int(pos1[1]) + sens * 1):
            # prendre directement
            if pos2 in pieces[c_adversaire]:
                if not check_echec or self.coup_met_pas_en_echec(passant,
                                                                 plateau,
                                                                 pieces,
                                                                 score,
                                                                 pos1, pos2):
                    # si la pièce est au bout, elle est 6 lignes plus avancée que sa ligne de départ
                    if int(pos2[1]) == int(debut) + 6 * sens:
                        changer_piece()
                    score[c_adversaire] -= plateau[pos2].value
                    return True
            # prise en passant
            elif f"{pos2[0]}{pos1[1]}" == passant[c_adversaire]:
                plateau_p, pieces_p = deepcopy(plateau), deepcopy(pieces)
                plateau_p[f"{pos2[0]}{pos1[1]}"] = None
                pieces_p[c_adversaire].remove(f"{pos2[0]}{pos1[1]}")
                if not check_echec or self.coup_met_pas_en_echec(passant,
                                                                 plateau,
                                                                 pieces,
                                                                 score,
                                                                 pos1, pos2):
                    score[c_adversaire] -= plateau[f"{pos2[0]}{pos1[1]}"].value
                    plateau[f"{pos2[0]}{pos1[1]}"] = None
                    pieces[c_adversaire].remove(f"{pos2[0]}{pos1[1]}")
                    return True
        return False


class Cavalier(Piece):
    def __init__(self, couleur):
        super().__init__(couleur)
        self.__nom = 'Cavalier'
        self.__value = 3.2

    @property
    def value(self):
        return self.__value

    @property
    def nom(self):
        return self.__nom

    def deplacement_verif(self, pos1, pos2, passant, pieces, plateau, score, simulation, check_echec=True):
        couleur = self.couleur
        c_adversaire = self.c_adversaire[couleur]
        # décale de 2 colonnes, 1 ligne
        if ((pos2[0] == chr(ord(pos1[0]) + 2) or pos2[0] == chr(ord(pos1[0]) - 2)) and
                (int(pos1[1]) == int(pos2[1]) + 1 or int(pos1[1]) == int(pos2[1]) - 1)):
            if not check_echec or self.coup_met_pas_en_echec(passant,
                                                             plateau,
                                                             pieces,
                                                             score,
                                                             pos1, pos2):
                if pos2 in pieces[c_adversaire]:
                    score[c_adversaire] -= plateau[pos2].value
                return True

        # décale de 2 lignes, 1 colonne
        elif ((pos2[0] == chr(ord(pos1[0]) + 1) or pos2[0] == chr(ord(pos1[0]) - 1)) and
              (int(pos1[1]) == int(pos2[1]) + 2 or int(pos1[1]) == int(pos2[1]) - 2)):
            if not check_echec or self.coup_met_pas_en_echec(passant,
                                                             plateau,
                                                             pieces,
                                                             score,
                                                             pos1, pos2):
                if pos2 in pieces[c_adversaire]:
                    score[c_adversaire] -= plateau[pos2].value
                return True
        return False


class Fou(Piece):
    def __init__(self, couleur):
        super().__init__(couleur)
        self.__nom = 'Fou'
        self.__value = 3.33

    @property
    def value(self):
        return self.__value

    @property
    def nom(self):
        return self.__nom

    def deplacement_verif(self, pos1, pos2, passant, pieces, plateau, score, simulation, check_echec=True):
        couleur = self.couleur
        c_adversaire = self.c_adversaire[couleur]
        if abs(ord(pos1[0]) - ord(pos2[0])) == abs(int(pos1[1]) - int(pos2[1])):
            nb_cases_milieu = abs(int(pos1[1]) - int(pos2[1])) - 1
            lettre, chiffre = [], []
            if ord(pos1[0]) < ord(pos2[0]):
                for i in range(nb_cases_milieu):
                    lettre.append(chr(ord(pos1[0]) + i + 1))
            else:
                for i in range(nb_cases_milieu):
                    lettre.append(chr(ord(pos1[0]) - i - 1))

            if int(pos1[1]) < int(pos2[1]):
                for i in range(nb_cases_milieu):
                    chiffre.append(f"{int(pos1[1]) + i + 1}")
            else:
                for i in range(nb_cases_milieu):
                    chiffre.append(f"{int(pos1[1]) - i - 1}")

            for i, j in zip(lettre, chiffre):
                if not plateau[f"{i}{j}"] is None:
                    return False
        else:
            return False
        if not check_echec or self.coup_met_pas_en_echec(passant,
                                                         plateau,
                                                         pieces,
                                                         score,
                                                         pos1, pos2):
            if pos2 in pieces[c_adversaire]:
                score[c_adversaire] -= plateau[pos2].value
            return True
        return False


class Tour(Piece):
    def __init__(self, couleur):
        super().__init__(couleur)
        self.__nom = 'Tour'
        self.deplace = False
        self.__value = 5.1

    @property
    def value(self):
        return self.__value

    @property
    def deplace(self):
        return self.__deplace

    @deplace.setter
    def deplace(self, d):
        if type(d) != bool:
            raise TypeError('Un booléen est attendu.')
        self.__deplace = d

    @property
    def nom(self):
        return self.__nom

    def deplacement_verif(self, pos1, pos2, passant, pieces, plateau, score, simulation, check_echec=True):
        couleur = self.couleur
        c_adversaire = self.c_adversaire[couleur]
        if pos1[0] == pos2[0]:
            nb_cases_milieu = abs(int(pos1[1]) - int(pos2[1])) - 1
            chiffre = []
            if int(pos1[1]) < int(pos2[1]):
                for i in range(nb_cases_milieu):
                    chiffre.append(f"{int(pos1[1]) + i + 1}")
            else:
                for i in range(nb_cases_milieu):
                    chiffre.append(f"{int(pos1[1]) - i - 1}")
            for j in chiffre:
                if not plateau[f"{pos1[0]}{j}"] is None:
                    return False

        elif pos1[1] == pos2[1]:
            nb_cases_milieu = abs(ord(pos1[0]) - ord(pos2[0])) - 1
            lettre = []
            if ord(pos1[0]) < ord(pos2[0]):
                for i in range(nb_cases_milieu):
                    lettre.append(chr(ord(pos1[0]) + i + 1))
            else:
                for i in range(nb_cases_milieu):
                    lettre.append(chr(ord(pos1[0]) - i - 1))
            for i in lettre:
                if not plateau[f"{i}{pos1[1]}"] is None:
                    return False
        else:
            return False
        if not check_echec or self.coup_met_pas_en_echec(passant,
                                                         plateau,
                                                         pieces,
                                                         score,
                                                         pos1, pos2):
            if pos2 in pieces[c_adversaire]:
                score[c_adversaire] -= plateau[pos2].value
            self.deplace = True
            return True
        return False


class Dame(Piece):
    def __init__(self, couleur):
        super().__init__(couleur)
        self.__nom = 'Dame'
        self.__value = 8.8

    @property
    def value(self):
        return self.__value

    @property
    def nom(self):
        return self.__nom

    def deplacement_verif(self, pos1, pos2, passant, pieces, plateau, score, simulation, check_echec=True):
        couleur = self.couleur
        c_adversaire = self.c_adversaire[couleur]

        def verif_tour(plateau):
            if pos1[0] == pos2[0]:
                nb_cases_milieu = abs(int(pos1[1]) - int(pos2[1])) - 1
                chiffre = []
                if int(pos1[1]) < int(pos2[1]):
                    for i in range(nb_cases_milieu):
                        chiffre.append(f"{int(pos1[1]) + i + 1}")
                else:
                    for i in range(nb_cases_milieu):
                        chiffre.append(f"{int(pos1[1]) - i - 1}")
                for j in chiffre:
                    if not plateau[f"{pos1[0]}{j}"] is None:
                        return False

            elif pos1[1] == pos2[1]:
                nb_cases_milieu = abs(ord(pos1[0]) - ord(pos2[0])) - 1
                lettre = []
                if ord(pos1[0]) < ord(pos2[0]):
                    for i in range(nb_cases_milieu):
                        lettre.append(chr(ord(pos1[0]) + i + 1))
                else:
                    for i in range(nb_cases_milieu):
                        lettre.append(chr(ord(pos1[0]) - i - 1))
                for i in lettre:
                    if not plateau[f"{i}{pos1[1]}"] is None:
                        return False
            else:
                return False
            return True

        def verif_fou(plateau):
            if abs(ord(pos1[0]) - ord(pos2[0])) == abs(int(pos1[1]) - int(pos2[1])):
                nb_cases_milieu = abs(int(pos1[1]) - int(pos2[1])) - 1
                lettre, chiffre = [], []
                if ord(pos1[0]) < ord(pos2[0]):
                    for i in range(nb_cases_milieu):
                        lettre.append(chr(ord(pos1[0]) + i + 1))
                else:
                    for i in range(nb_cases_milieu):
                        lettre.append(chr(ord(pos1[0]) - i - 1))

                if int(pos1[1]) < int(pos2[1]):
                    for i in range(nb_cases_milieu):
                        chiffre.append(f"{int(pos1[1]) + i + 1}")
                else:
                    for i in range(nb_cases_milieu):
                        chiffre.append(f"{int(pos1[1]) - i - 1}")

                for i, j in zip(lettre, chiffre):
                    if not plateau[f"{i}{j}"] is None:
                        return False
            else:
                return False
            return True

        if (verif_tour(plateau) or
                verif_fou(plateau)):
            if not check_echec or self.coup_met_pas_en_echec(passant,
                                                             plateau,
                                                             pieces,
                                                             score,
                                                             pos1, pos2):
                if pos2 in pieces[c_adversaire]:
                    score[c_adversaire] -= plateau[pos2].value
                return True
        return False


class Roi(Piece):
    def __init__(self, couleur):
        super().__init__(couleur)
        self.__nom = 'Roi'
        self.deplace = False
        self.__value = 0

    @property
    def value(self):
        return self.__value

    @property
    def deplace(self):
        return self.__deplace

    @deplace.setter
    def deplace(self, d):
        if type(d) != bool:
            raise TypeError('Un booléen est attendu.')
        self.__deplace = d

    @property
    def nom(self):
        return self.__nom

    def deplacement_verif(self, pos1, pos2, passant, pieces, plateau, score, simulation, check_echec=True):
        couleur = self.couleur
        cote = 1
        c_adversaire = 'noir'
        if couleur == 'noir':
            cote = 8
            c_adversaire = 'blanc'
        # petit roque
        # vérif position
        if pos1 == f"e{cote}" and pos2 == f"g{cote}":
            # vérif cases vides, présence tour, roi et tour immobiles
            if (plateau[f"f{cote}"] is None and
                    plateau[f"g{cote}"] is None and
                    plateau[f"h{cote}"] is not None and
                    plateau[f"h{cote}"].nom == 'Tour' and
                    not plateau[f"h{cote}"].deplace and
                    not self.deplace):
                # vérif roi non en échec et cases de passages non plus
                for lettre in ['e', 'f', 'g']:
                    if not self.coup_met_pas_en_echec(passant,
                                                      plateau,
                                                      pieces,
                                                      score,
                                                      pos1, f"{lettre}{cote}"):
                        return False
                self.deplace = True
                pieces[f'roi{couleur}'] = pos2
                self.bouger(plateau, pieces, f"h{cote}", f"f{cote}")
                return True
            else:
                return False

        # grand roque
        # vérif position
        if pos1 == f"e{cote}" and pos2 == f"c{cote}":
            # vérif cases vides, présence tour, roi et tour immobiles
            if (plateau[f"b{cote}"] is None and
                    plateau[f"c{cote}"] is None and
                    plateau[f"d{cote}"] is None and
                    plateau[f"a{cote}"] is not None and
                    plateau[f"a{cote}"].nom == 'Tour' and
                    not plateau[f"a{cote}"].deplace and
                    not self.deplace):
                # vérif roi non en échec et cases de passages non plus
                for lettre in ['c', 'd', 'e']:
                    if not self.coup_met_pas_en_echec(passant,
                                                      plateau,
                                                      pieces,
                                                      score,
                                                      pos1, f"{lettre}{cote}"):
                        return False
                self.deplace = True
                pieces[f'roi{couleur}'] = pos2
                self.bouger(plateau, pieces, f"a{cote}", f"d{cote}")
                return True
            else:
                return False

        if abs(int(pos1[1]) - int(pos2[1])) not in [0, 1]:
            return False
        elif abs(ord(pos1[0]) - ord(pos2[0])) not in [0, 1]:
            return False
        if not check_echec or self.coup_met_pas_en_echec(passant,
                                                         plateau,
                                                         pieces,
                                                         score,
                                                         pos1, pos2):
            if pos2 in pieces[c_adversaire]:
                score[c_adversaire] -= plateau[pos2].value
            self.deplace = True
            pieces[f'roi{couleur}'] = pos2
            return True
        return False


class Plateau:
    def __init__(self):
        self.pieces = dict()
        self.pieces_vulnerables = {'blanc': [], 'noir': []}
        self.passant = dict()
        self.plateau = dict()
        self.score = dict()
        self.pieces['blanc'] = {f"{i}1" for i in 'abcdefgh'}.union({f"{i}2" for i in 'abcdefgh'})
        self.pieces['noir'] = {f"{i}7" for i in 'abcdefgh'}.union({f"{i}8" for i in 'abcdefgh'})
        self.pieces['roiblanc'] = 'e1'
        self.pieces['roinoir'] = 'e8'
        self.passant['blanc'] = None
        self.passant['noir'] = None
        self.score['blanc'], self.score['noir'] = 40.06, 40.06
        for i in 'abcdefgh':
            for j in '3456':
                self.plateau[f"{i}{j}"] = None
            self.plateau[f"{i}2"] = Pion('blanc')
            self.plateau[f"{i}7"] = Pion('noir')

        self.plateau["a1"], self.plateau["h1"] = Tour('blanc'), Tour('blanc')
        self.plateau["b1"], self.plateau["g1"] = Cavalier('blanc'), Cavalier('blanc')
        self.plateau["c1"], self.plateau["f1"] = Fou('blanc'), Fou('blanc')
        self.plateau["d1"], self.plateau["e1"] = Dame('blanc'), Roi('blanc')

        self.plateau["a8"], self.plateau["h8"] = Tour('noir'), Tour('noir')
        self.plateau["b8"], self.plateau["g8"] = Cavalier('noir'), Cavalier('noir')
        self.plateau["c8"], self.plateau["f8"] = Fou('noir'), Fou('noir')
        self.plateau["d8"], self.plateau["e8"] = Dame('noir'), Roi('noir')

    def deplacement_possible(self, pos1, pos2, couleur, verif_echec=True):
        if pos2 in self.pieces[couleur]:
            return False
        return deepcopy(self.plateau[pos1]).deplacement_verif(pos1, pos2,
                                                              deepcopy(self.passant),
                                                              deepcopy(self.pieces),
                                                              deepcopy(self.plateau),
                                                              deepcopy(self.score),
                                                              True,
                                                              verif_echec)

    def deplacement(self, pos1, pos2, couleur, simulation=False):
        if pos2 in self.pieces[couleur] or pos1 not in self.pieces[couleur] or pos2 not in self.plateau.keys():
            print("\nLe déplacement est invalide.\n")
            return False
        if not self.plateau[pos1].deplacement_verif(pos1, pos2,
                                                    self.passant,
                                                    self.pieces,
                                                    self.plateau,
                                                    self.score,
                                                    simulation):
            print('\nLe déplacement est invalide.\n')
            return False
        couleur_adv = 'noir'
        if couleur == 'noir':
            couleur_adv = 'blanc'
        self.plateau[pos2] = self.plateau[pos1]
        self.plateau[pos1] = None
        self.pieces[couleur].remove(pos1)
        self.pieces[couleur].add(pos2)
        if pos2 in self.pieces[couleur_adv]:
            self.pieces[couleur_adv].remove(pos2)
        return True

    def show(self):
        print()
        print(f"{' ' :6}", end="")
        for i in 'abcdefgh':
            print(f"{i :6}", end="")
        print("\n")
        for j in '87654321':
            print(f"{j :6}", end="")
            for i in 'abcdefgh':
                if self.plateau[f'{i}{j}'] is None:
                    if (ord(i) % 2 == 0 and int(j) % 2 != 0) or ord(i) % 2 != 0 and int(j) % 2 == 0:
                        print(f"{'░░░' :6}", end="")  # ░▒▓▇
                    else:
                        print(f"{'__|' :6}", end="")
                else:
                    pos = f'{i}{j}'
                    print(f"{f'{self.plateau[pos].nom[0]}' f'{self.plateau[pos].couleur[0]}' :6}", end="")
            print(j)
        print()
        print(f"{' ' :6}", end="")
        for i in 'abcdefgh':
            print(f"{i :6}", end="")
        print("\n")

    def partie_bot_rapide(self, couleur_jouee, difficulte, nb_coups):
        couleur = 'blanc'
        coups_jouables = self.coups_jouables_prise(couleur)
        diff = difficulte
        nb_c = nb_coups
        while not coups_jouables[0] == []:
            if len(self.pieces['blanc']) + len(self.pieces['noir']) < 5:
                diff = difficulte + 2
                nb_c = nb_coups + 3
            elif len(self.pieces['blanc']) + len(self.pieces['noir']) < 10:
                diff = difficulte + 1
                nb_c = nb_coups + 2
            elif len(self.pieces['blanc']) + len(self.pieces['noir']) < 15:
                nb_c = nb_coups+1
            self.show()
            sleep(0.2)
            self.passant[couleur] = None
            if self.echec(couleur):
                print("Échec.\n")
            print(f"Les {couleur}s jouent.\n")
            if not couleur == couleur_jouee:
                pos1, pos2 = self.meilleur_coup_rapide(coups_jouables,
                                                       couleur,
                                                       couleur,
                                                       diff,
                                                       diff,
                                                       nb_c)
                self.deplacement(pos1, pos2, couleur)
            else:
                pos1 = input(f'{"Position départ" :17}{" : "}')
                pos2 = input(f'{"Position arrivée " :17}{" : "}')
                while not self.deplacement(pos1, pos2, couleur):
                    pos1 = input(f'{"Position départ" :17}{" : "}')
                    pos2 = input(f'{"Position arrivée " :17}{" : "}')
            print(f"{pos1} -> {pos2}")
            if couleur == 'blanc':
                couleur = 'noir'
            else:
                couleur = 'blanc'
            coups_jouables = self.coups_jouables_prise(couleur)
        self.show()
        if self.echec_et_mat(couleur):
            print("\nÉchec et mat.")
            gagnant = 'noir'
            if couleur == 'noir':
                gagnant = 'blanc'
            print(f"Les {gagnant}s gagnent.")
        else:
            print("Pat.")
            print('Égalité.')

    def echec(self, couleur):
        couleur_adverse = 'noir'
        if couleur == 'noir':
            couleur_adverse = 'blanc'
        case_roi = self.pieces[f'roi{couleur}']
        for case_piece in self.pieces[couleur_adverse]:
            if self.deplacement_possible(case_piece, case_roi, couleur_adverse, False):
                return True
        return False

    def echec_et_mat(self, couleur):
        return self.coups_jouables_prise(couleur)[0] == [] and self.echec(couleur)

    def pat(self, couleur):
        return self.coups_jouables_prise(couleur)[0] == [] and not self.echec(couleur)

    def coups_jouables_prise(self, couleur):
        coups_possibles = []
        fin_coups_prise = 0
        couleur_adverse = 'noir'
        if couleur == 'noir':
            couleur_adverse = 'blanc'
        for case_piece in self.pieces[couleur]:
            # coups possibles du pion
            if self.plateau[case_piece].nom == 'Pion':
                sens = 1
                if couleur == 'noir':
                    sens = -1
                # avancer et diagonales
                cases_probables = [f"{case_piece[0]}{int(case_piece[1]) + sens}",
                                   f"{chr(ord(case_piece[0]) + 1)}{int(case_piece[1]) + sens}",
                                   f"{chr(ord(case_piece[0]) - 1)}{int(case_piece[1]) + sens}"]
                # double coup probable si pion au début
                if (couleur == 'noir' and case_piece[1] == "7") or (couleur == 'blanc' and case_piece[1] == "2"):
                    cases_probables.append(f"{case_piece[0]}{int(case_piece[1]) + 2 * sens}")

                cases_probables = [case for case in cases_probables if len(case) == 2]
                for case_arrivee in cases_probables:
                    if ord('h') >= ord(case_arrivee[0]) >= ord('a') and 8 >= int(case_arrivee[1]) >= 1:
                        if self.deplacement_possible(case_piece, case_arrivee, couleur):
                            if case_arrivee in self.pieces[couleur_adverse]:
                                coups_possibles.insert(0, (case_piece, case_arrivee))
                                fin_coups_prise += 1
                            else:
                                coups_possibles.append((case_piece, case_arrivee))

            if self.plateau[case_piece].nom == 'Cavalier':
                # décale de 2 colonnes, 1 ligne
                cases_probables = [f"{chr(ord(case_piece[0]) + 2)}{int(case_piece[1]) + 1}",
                                   f"{chr(ord(case_piece[0]) + 2)}{int(case_piece[1]) - 1}",
                                   f"{chr(ord(case_piece[0]) - 2)}{int(case_piece[1]) + 1}",
                                   f"{chr(ord(case_piece[0]) - 2)}{int(case_piece[1]) - 1}"]
                # décale de 2 lignes, 1 colonne
                cases_probables += [f"{chr(ord(case_piece[0]) + 1)}{int(case_piece[1]) + 2}",
                                    f"{chr(ord(case_piece[0]) + 1)}{int(case_piece[1]) - 2}",
                                    f"{chr(ord(case_piece[0]) - 1)}{int(case_piece[1]) + 2}",
                                    f"{chr(ord(case_piece[0]) - 1)}{int(case_piece[1]) - 2}"]
                cases_probables = [case for case in cases_probables if len(case) == 2]
                for case_arrivee in cases_probables:
                    if ord('h') >= ord(case_arrivee[0]) >= ord('a') and 8 >= int(case_arrivee[1]) >= 1:
                        if self.deplacement_possible(case_piece, case_arrivee, couleur):
                            if case_arrivee in self.pieces[couleur_adverse]:
                                coups_possibles.insert(0, (case_piece, case_arrivee))
                                fin_coups_prise += 1
                            else:
                                coups_possibles.append((case_piece, case_arrivee))

            if self.plateau[case_piece].nom == 'Tour':
                # On prend d'abord les cases de chaque côté de la tour, en partant de la tour et non de "a" ou "1"
                # Faire comme ça et non pas juste check toute la ligne et colonne permet de vérifier moins de cases
                haut = [f"{case_piece[0]}{int(case_piece[1]) + j}"
                        for j in range(1, 8 - abs(int(case_piece[1]) - 1))]
                bas = [f"{case_piece[0]}{int(case_piece[1]) - j}"
                       for j in range(1, 8 - abs(int(case_piece[1]) - 8))]
                gauche = [f"{chr(ord(case_piece[0]) - i)}{case_piece[1]}"
                          for i in range(1, 8 - abs(ord(case_piece[0]) - ord('h')))]
                droite = [f"{chr(ord(case_piece[0]) + i)}{case_piece[1]}"
                          for i in range(1, 8 - abs(ord(case_piece[0]) - ord('a')))]
                cases_probables = [haut, bas, droite, gauche]
                # réduction du nombre de tests : si une case est invalides, celles plus loin le sont aussi
                for direction in cases_probables:
                    for case_arrivee in direction:
                        if self.deplacement_possible(case_piece, case_arrivee, couleur):
                            if case_arrivee in self.pieces[couleur_adverse]:
                                coups_possibles.insert(0, (case_piece, case_arrivee))
                                fin_coups_prise += 1
                            else:
                                coups_possibles.append((case_piece, case_arrivee))
                        else:
                            break

            if self.plateau[case_piece].nom == 'Fou':
                # même principe de réduction de tests qu'avec les tours mais dans les diagonales
                haut_gauche = [f"{chr(ord(case_piece[0]) - i)}{int(case_piece[1]) + i}"
                               for i in
                               range(1, 8 - max(abs(int(case_piece[1]) - 1), abs(ord(case_piece[0]) - ord('h'))))]
                haut_droite = [f"{chr(ord(case_piece[0]) + i)}{int(case_piece[1]) + i}"
                               for i in
                               range(1, 8 - max(abs(int(case_piece[1]) - 1), abs(ord(case_piece[0]) - ord('a'))))]
                bas_droite = [f"{chr(ord(case_piece[0]) + i)}{int(case_piece[1]) - i}"
                              for i in
                              range(1, 8 - max(abs(int(case_piece[1]) - 8), abs(ord(case_piece[0]) - ord('a'))))]
                bas_gauche = [f"{chr(ord(case_piece[0]) - i)}{int(case_piece[1]) - i}"
                              for i in
                              range(1, 8 - max(abs(int(case_piece[1]) - 8), abs(ord(case_piece[0]) - ord('h'))))]
                cases_probables = [haut_gauche, haut_droite, bas_droite, bas_gauche]
                for direction in cases_probables:
                    for case_arrivee in direction:
                        if self.deplacement_possible(case_piece, case_arrivee, couleur):
                            if case_arrivee in self.pieces[couleur_adverse]:
                                coups_possibles.insert(0, (case_piece, case_arrivee))
                                fin_coups_prise += 1
                            else:
                                coups_possibles.append((case_piece, case_arrivee))
                        else:
                            break

            if self.plateau[case_piece].nom == 'Dame':
                # même principe que fou et tour, mais les deux en même temps
                haut = [f"{case_piece[0]}{int(case_piece[1]) + j}"
                        for j in range(1, 8 - abs(int(case_piece[1]) - 1))]
                bas = [f"{case_piece[0]}{int(case_piece[1]) - j}"
                       for j in range(1, 8 - abs(int(case_piece[1]) - 8))]
                gauche = [f"{chr(ord(case_piece[0]) - i)}{case_piece[1]}"
                          for i in range(1, 8 - abs(ord(case_piece[0]) - ord('h')))]
                droite = [f"{chr(ord(case_piece[0]) + i)}{case_piece[1]}"
                          for i in range(1, 8 - abs(ord(case_piece[0]) - ord('a')))]
                haut_gauche = [f"{chr(ord(case_piece[0]) - i)}{int(case_piece[1]) + i}"
                               for i in
                               range(1, 8 - max(abs(int(case_piece[1]) - 1), abs(ord(case_piece[0]) - ord('h'))))]
                haut_droite = [f"{chr(ord(case_piece[0]) + i)}{int(case_piece[1]) + i}"
                               for i in
                               range(1, 8 - max(abs(int(case_piece[1]) - 1), abs(ord(case_piece[0]) - ord('a'))))]
                bas_droite = [f"{chr(ord(case_piece[0]) + i)}{int(case_piece[1]) - i}"
                              for i in
                              range(1, 8 - max(abs(int(case_piece[1]) - 8), abs(ord(case_piece[0]) - ord('a'))))]
                bas_gauche = [f"{chr(ord(case_piece[0]) - i)}{int(case_piece[1]) - i}"
                              for i in
                              range(1, 8 - max(abs(int(case_piece[1]) - 8), abs(ord(case_piece[0]) - ord('h'))))]
                cases_probables = [haut, haut_droite, droite, bas_droite, bas, bas_gauche, gauche, haut_gauche]
                for direction in cases_probables:
                    for case_arrivee in direction:
                        if self.deplacement_possible(case_piece, case_arrivee, couleur):
                            if case_arrivee in self.pieces[couleur_adverse]:
                                coups_possibles.insert(0, (case_piece, case_arrivee))
                                fin_coups_prise += 1
                            else:
                                coups_possibles.append((case_piece, case_arrivee))
                        else:
                            break

            if self.plateau[case_piece].nom == 'Roi':
                cote = 1
                if couleur == 'noir':
                    cote = 8
                # cases devant
                cases_probables = [f"{chr(ord(case_piece[0]) + i)}{int(case_piece[1]) + 1}" for i in [-1, 0, 1]]
                # cases derrière
                cases_probables += [f"{chr(ord(case_piece[0]) + i)}{int(case_piece[1]) - 1}" for i in [-1, 0, 1]]
                # cases sur le côté
                cases_probables += [f"{chr(ord(case_piece[0]) + 1)}{case_piece[1]}",
                                    f"{chr(ord(case_piece[0]) - 1)}{case_piece[1]}"]
                cases_probables = [case for case in cases_probables if len(case) == 2]
                if not self.plateau[case_piece].deplace:
                    cases_probables += [f"c{cote}", f"g{cote}"]
                for case_arrivee in cases_probables:
                    if ord('h') >= ord(case_arrivee[0]) >= ord('a') and 8 >= int(case_arrivee[1]) >= 1:
                        if self.deplacement_possible(case_piece, case_arrivee, couleur):
                            if case_arrivee in self.pieces[couleur_adverse]:
                                coups_possibles.insert(0, (case_piece, case_arrivee))
                                fin_coups_prise += 1
                            else:
                                coups_possibles.append((case_piece, case_arrivee))
        return coups_possibles, fin_coups_prise

    def update_vulnerable(self, couleur):
        """
            mettre la couleur de l'adversaire en paramètre
        """
        couleur_adverse = 'noir'
        if couleur == 'noir':
            couleur_adverse = 'blanc'

        self.pieces_vulnerables[couleur_adverse] = []

        for case_piece in self.pieces[couleur]:
            # coups possibles du pion
            if self.plateau[case_piece].nom == 'Pion':
                sens = 1
                if couleur == 'noir':
                    sens = -1
                # avancer et diagonales
                cases_probables = [f"{case_piece[0]}{int(case_piece[1]) + sens}",
                                   f"{chr(ord(case_piece[0]) + 1)}{int(case_piece[1]) + sens}",
                                   f"{chr(ord(case_piece[0]) - 1)}{int(case_piece[1]) + sens}"]
                # double coup probable si pion au début
                if (couleur == 'noir' and case_piece[1] == "7") or (couleur == 'blanc' and case_piece[1] == "2"):
                    cases_probables.append(f"{case_piece[0]}{int(case_piece[1]) + 2 * sens}")

                cases_probables = [case for case in cases_probables if len(case) == 2]
                for case_arrivee in cases_probables:
                    if ord('h') >= ord(case_arrivee[0]) >= ord('a') and 8 >= int(case_arrivee[1]) >= 1:
                        if case_arrivee in self.pieces[couleur_adverse]:
                            if self.deplacement_possible(case_piece, case_arrivee, couleur):
                                self.pieces_vulnerables[couleur_adverse].append(case_arrivee)

            if self.plateau[case_piece].nom == 'Cavalier':
                # décale de 2 colonnes, 1 ligne
                cases_probables = [f"{chr(ord(case_piece[0]) + 2)}{int(case_piece[1]) + 1}",
                                   f"{chr(ord(case_piece[0]) + 2)}{int(case_piece[1]) - 1}",
                                   f"{chr(ord(case_piece[0]) - 2)}{int(case_piece[1]) + 1}",
                                   f"{chr(ord(case_piece[0]) - 2)}{int(case_piece[1]) - 1}"]
                # décale de 2 lignes, 1 colonne
                cases_probables += [f"{chr(ord(case_piece[0]) + 1)}{int(case_piece[1]) + 2}",
                                    f"{chr(ord(case_piece[0]) + 1)}{int(case_piece[1]) - 2}",
                                    f"{chr(ord(case_piece[0]) - 1)}{int(case_piece[1]) + 2}",
                                    f"{chr(ord(case_piece[0]) - 1)}{int(case_piece[1]) - 2}"]
                cases_probables = [case for case in cases_probables if len(case) == 2]
                for case_arrivee in cases_probables:
                    if ord('h') >= ord(case_arrivee[0]) >= ord('a') and 8 >= int(case_arrivee[1]) >= 1:
                        if case_arrivee in self.pieces[couleur_adverse]:
                            if self.deplacement_possible(case_piece, case_arrivee, couleur):
                                self.pieces_vulnerables[couleur_adverse].append(case_arrivee)

            if self.plateau[case_piece].nom == 'Tour':
                # On prend d'abord les cases de chaque côté de la tour, en partant de la tour et non de "a" ou "1"
                # Faire comme ça et non pas juste check toute la ligne et colonne permet de vérifier moins de cases
                haut = [f"{case_piece[0]}{int(case_piece[1]) + j}"
                        for j in range(1, 8 - abs(int(case_piece[1]) - 1))]
                bas = [f"{case_piece[0]}{int(case_piece[1]) - j}"
                       for j in range(1, 8 - abs(int(case_piece[1]) - 8))]
                gauche = [f"{chr(ord(case_piece[0]) - i)}{case_piece[1]}"
                          for i in range(1, 8 - abs(ord(case_piece[0]) - ord('h')))]
                droite = [f"{chr(ord(case_piece[0]) + i)}{case_piece[1]}"
                          for i in range(1, 8 - abs(ord(case_piece[0]) - ord('a')))]
                cases_probables = [haut, bas, droite, gauche]
                # réduction du nombre de tests : si une case est invalides, celles plus loin le sont aussi
                for direction in cases_probables:
                    for case_arrivee in direction:
                        if case_arrivee in self.pieces[couleur_adverse]:
                            if self.deplacement_possible(case_piece, case_arrivee, couleur):
                                self.pieces_vulnerables[couleur_adverse].append(case_arrivee)
                            else:
                                break

            if self.plateau[case_piece].nom == 'Fou':
                # même principe de réduction de tests qu'avec les tours mais dans les diagonales
                haut_gauche = [f"{chr(ord(case_piece[0]) - i)}{int(case_piece[1]) + i}"
                               for i in
                               range(1, 8 - max(abs(int(case_piece[1]) - 1), abs(ord(case_piece[0]) - ord('h'))))]
                haut_droite = [f"{chr(ord(case_piece[0]) + i)}{int(case_piece[1]) + i}"
                               for i in
                               range(1, 8 - max(abs(int(case_piece[1]) - 1), abs(ord(case_piece[0]) - ord('a'))))]
                bas_droite = [f"{chr(ord(case_piece[0]) + i)}{int(case_piece[1]) - i}"
                              for i in
                              range(1, 8 - max(abs(int(case_piece[1]) - 8), abs(ord(case_piece[0]) - ord('a'))))]
                bas_gauche = [f"{chr(ord(case_piece[0]) - i)}{int(case_piece[1]) - i}"
                              for i in
                              range(1, 8 - max(abs(int(case_piece[1]) - 8), abs(ord(case_piece[0]) - ord('h'))))]
                cases_probables = [haut_gauche, haut_droite, bas_droite, bas_gauche]
                for direction in cases_probables:
                    for case_arrivee in direction:
                        if case_arrivee in self.pieces[couleur_adverse]:
                            if self.deplacement_possible(case_piece, case_arrivee, couleur):
                                self.pieces_vulnerables[couleur_adverse].append(case_arrivee)
                            else:
                                break

            if self.plateau[case_piece].nom == 'Dame':
                # même principe que fou et tour, mais les deux en même temps
                haut = [f"{case_piece[0]}{int(case_piece[1]) + j}"
                        for j in range(1, 8 - abs(int(case_piece[1]) - 1))]
                bas = [f"{case_piece[0]}{int(case_piece[1]) - j}"
                       for j in range(1, 8 - abs(int(case_piece[1]) - 8))]
                gauche = [f"{chr(ord(case_piece[0]) - i)}{case_piece[1]}"
                          for i in range(1, 8 - abs(ord(case_piece[0]) - ord('h')))]
                droite = [f"{chr(ord(case_piece[0]) + i)}{case_piece[1]}"
                          for i in range(1, 8 - abs(ord(case_piece[0]) - ord('a')))]
                haut_gauche = [f"{chr(ord(case_piece[0]) - i)}{int(case_piece[1]) + i}"
                               for i in
                               range(1, 8 - max(abs(int(case_piece[1]) - 1), abs(ord(case_piece[0]) - ord('h'))))]
                haut_droite = [f"{chr(ord(case_piece[0]) + i)}{int(case_piece[1]) + i}"
                               for i in
                               range(1, 8 - max(abs(int(case_piece[1]) - 1), abs(ord(case_piece[0]) - ord('a'))))]
                bas_droite = [f"{chr(ord(case_piece[0]) + i)}{int(case_piece[1]) - i}"
                              for i in
                              range(1, 8 - max(abs(int(case_piece[1]) - 8), abs(ord(case_piece[0]) - ord('a'))))]
                bas_gauche = [f"{chr(ord(case_piece[0]) - i)}{int(case_piece[1]) - i}"
                              for i in
                              range(1, 8 - max(abs(int(case_piece[1]) - 8), abs(ord(case_piece[0]) - ord('h'))))]
                cases_probables = [haut, haut_droite, droite, bas_droite, bas, bas_gauche, gauche, haut_gauche]
                for direction in cases_probables:
                    for case_arrivee in direction:
                        if case_arrivee in self.pieces[couleur_adverse]:
                            if self.deplacement_possible(case_piece, case_arrivee, couleur):
                                self.pieces_vulnerables[couleur_adverse].append(case_arrivee)
                            else:
                                break

            if self.plateau[case_piece].nom == 'Roi':
                cote = 1
                if couleur == 'noir':
                    cote = 8
                # cases devant
                cases_probables = [f"{chr(ord(case_piece[0]) + i)}{int(case_piece[1]) + 1}" for i in [-1, 0, 1]]
                # cases derrière
                cases_probables += [f"{chr(ord(case_piece[0]) + i)}{int(case_piece[1]) - 1}" for i in [-1, 0, 1]]
                # cases sur le côté
                cases_probables += [f"{chr(ord(case_piece[0]) + 1)}{case_piece[1]}",
                                    f"{chr(ord(case_piece[0]) - 1)}{case_piece[1]}"]
                cases_probables = [case for case in cases_probables if len(case) == 2]
                if not self.plateau[case_piece].deplace:
                    cases_probables += [f"c{cote}", f"g{cote}"]
                for case_arrivee in cases_probables:
                    if ord('h') >= ord(case_arrivee[0]) >= ord('a') and 8 >= int(case_arrivee[1]) >= 1:
                        if case_arrivee in self.pieces[couleur_adverse]:
                            if self.deplacement_possible(case_piece, case_arrivee, couleur):
                                self.pieces_vulnerables[couleur_adverse].append(case_arrivee)

    def meilleur_coup_rapide(self, coups_jouables, couleur, couleur_joueur, recursion_initiale, recursion, nb_coups):
        """
            Principe du meilleur coup : coup offrant le meilleur gain de score minimum assuré
            Si deux coups on le meilleure gain minimum assuré, on choisi celui avec le meilleur
            maximum probable.
        """

        self.passant[couleur] = None

        def cases_adjacentes(case):
            cases_adj = {case}
            cases_liste = [f"{case[0]}{int(case[1]) + 1}",
                           f"{chr(ord(case[0]) + 1)}{int(case[1]) + 1}",
                           f"{chr(ord(case[0]) + 1)}{case[1]}",
                           f"{chr(ord(case[0]) + 1)}{int(case[1]) - 1}",
                           f"{case[0]}{int(case[1]) - 1}",
                           f"{chr(ord(case[0]) - 1)}{int(case[1]) - 1}",
                           f"{chr(ord(case[0]) - 1)}{case[1]}",
                           f"{chr(ord(case[0]) - 1)}{int(case[1]) + 1}"]

            for c in cases_liste:
                if ord('h') >= ord(c[0]) >= ord('a') and 8 >= int(c[1]) >= 1:
                    cases_adj.add(c)

            return cases_adj

        couleur_adverse = 'noir'
        if couleur == 'noir':
            couleur_adverse = 'blanc'

        # récursion maximale, le coup le plus avancé
        if recursion == 0:

            # Plus de coups jouables
            if len(coups_jouables[0]) == 0:
                if self.echec(couleur):
                    if couleur == couleur_joueur:
                        # Joueur pour qui on prédit est en échec et mat
                        return -10000, -10000
                    else:
                        # Joueur contre qui on prédit est en échec et mat
                        return 10000, 10000
                else:
                    # Pat
                    return 0, 0

            # retour normal
            d_score = self.score[couleur] - self.score[couleur_adverse]
            if couleur_joueur != couleur:
                d_score = -d_score
            # print(f" Récusrion : {recursion} : {d_score}")

            # prendre en compte si échec
            if self.echec(couleur):
                if couleur == couleur:
                    return d_score-5, d_score
                else:
                    return d_score, d_score+20
            return d_score, d_score

        # récursion intermédiaire
        if recursion != recursion_initiale:

            # Plus de coups jouables
            if len(coups_jouables[0]) == 0:
                if self.echec(couleur):
                    if couleur == couleur_joueur:
                        # Joueur pour qui on prédit est en échec et mat
                        return -10000, -10000
                    else:
                        # Joueur contre qui on prédit est en échec et mat
                        return 10000, 10000
                else:
                    # Pat
                    return 0, 0

            stats_min, stats_max = 1000, -1000

            self.update_vulnerable(couleur_adverse)
            cases_attention = set()
            for case_vulnerable in self.pieces_vulnerables[couleur]:
                cases_attention = cases_attention.union(cases_adjacentes(case_vulnerable))

            coups_verif, np = coups_jouables[0], coups_jouables[1]

            coups_prise = coups_verif[:np]
            coups_non_prise = coups_verif[np:]

            shuffle(coups_prise)
            shuffle(coups_non_prise)

            interessant = 0
            for coup in coups_non_prise.copy():
                if coup[0] in cases_attention or coup[1] in cases_attention:
                    coups_non_prise.remove(coup)
                    coups_non_prise.insert(0, coup)
                    interessant += 1

            coups_verif = coups_prise + coups_non_prise
            interessant = interessant % nb_coups
            n = max(len(coups_prise) + max(interessant, 1), nb_coups)
            coups_verif = coups_verif[:n]
            # print(coups_verif)

            for coup in coups_verif:
                # print(len(coups_verif), len(coups_jouables[0]))
                # print(f"{coup}, niveau {recursion - 1}")
                simulation = deepcopy(self)
                simulation.deplacement(coup[0], coup[1], couleur, True)
                # mini est le score minimum assuré et maxi est le score maximum possible
                mini, maxi = simulation.meilleur_coup_rapide(simulation.coups_jouables_prise(couleur_adverse),
                                                             couleur_adverse,
                                                             couleur_joueur,
                                                             recursion_initiale,
                                                             recursion - 1,
                                                             nb_coups)

                # ne pas trop bouger son roi, faire bouger le roi adverse
                if coup[0] == self.pieces[f'roi{couleur}']:
                    if couleur == couleur_joueur:
                        mini -= 2
                    else:
                        mini += 2

                if mini < stats_min:
                    stats_min = mini
                if maxi > stats_max:
                    stats_max = maxi

            # print(f" Récusrion : {recursion} : {stats_min}, {stats_max}")
            # prendre en compte si échec
            if self.echec(couleur):
                if couleur == couleur:
                    return stats_min - 5, stats_max
                else:
                    return stats_min, stats_max + 20
            return stats_min, stats_max

        # récursion primaire
        stats_min, stats_max = -1000, -1000
        bon_coup = ('a1', 'a1')

        self.update_vulnerable(couleur_adverse)
        cases_attention = set()
        for case_vulnerable in self.pieces_vulnerables[couleur]:
            cases_attention = cases_attention.union(cases_adjacentes(case_vulnerable))

        coups_verif, np = coups_jouables[0], coups_jouables[1]
        coups_prise = coups_verif[:np]
        coups_non_prise = coups_verif[np:]

        shuffle(coups_prise)
        shuffle(coups_non_prise)

        interessant = 0
        for coup in coups_non_prise.copy():
            if coup[0] in cases_attention or coup[1] in cases_attention:
                coups_non_prise.remove(coup)
                coups_non_prise.insert(0, coup)
                interessant += 1

        coups_verif = coups_prise + coups_non_prise
        interessant = interessant % nb_coups
        n = max(len(coups_prise) + max(interessant, 1), nb_coups)
        coups_verif = coups_verif[:n]
        # print(coups_verif)

        # print(len(coups_verif), len(coups_jouables[0]))
        for coup in coups_verif:
            # print(f"{coup}, niveau {recursion - 1}")
            simulation = deepcopy(self)
            simulation.deplacement(coup[0], coup[1], couleur, True)
            # mini est le score minimum assuré et maxi est le score maximum possible
            mini, maxi = simulation.meilleur_coup_rapide(simulation.coups_jouables_prise(couleur_adverse),
                                                         couleur_adverse,
                                                         couleur_joueur,
                                                         recursion_initiale,
                                                         recursion - 1,
                                                         nb_coups)

            # Bouger le roi est évitable
            if coup[0] == self.pieces[f'roi{couleur}']:
                mini -= 2
            if mini >= stats_min:
                if mini > stats_min:
                    stats_min = mini
                    stats_max = maxi
                    bon_coup = coup
                if maxi > stats_max:
                    stats_max = maxi
                    bon_coup = coup
        return bon_coup
