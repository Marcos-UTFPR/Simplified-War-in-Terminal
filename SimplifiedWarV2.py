# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Bibliotecas -----------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

import time
import sys
import os
import random

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Constantes e Variáveis Globais ---------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

# Cores
PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLACK = '\x1b[30m'
BRIGHTBLACK   = '\033[30m'
WHITE   = '\033[37m'
MAGENTA = '\033[35m'
RED = '\033[91m'
# Estilos de texto
BLINK = "\033[5m"
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m' # Reseta toda a formatação
# Vetor completo
COLORS = [PURPLE, CYAN, DARKCYAN, BLUE, GREEN, YELLOW, RED, MAGENTA, BLACK, BRIGHTBLACK, WHITE, BLINK, BOLD, UNDERLINE, END]

STARTING_ARMIES = 3 # Número de tropas que cada player inicia

ARMIES_PER_ROUND = 2 # Número mínimo de tropas ganhas por cada round
card_bonus = 1 # Número de tropas ganhas a cada troca de 3 cartas (OBS: Mínimo de 1 no início por default, aumenta com cada troca)

SPADES = '♠'
GOLD = '♦'
HEARTS = '♥'
WOOD = '♣' # Unused
SUITS = [SPADES, GOLD, HEARTS, WOOD]

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Exceções -------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

class PathException(Exception): # Exceção customizada
    def __init__(self, message=("Não há caminho entre os territórios escolhidos!")):
        # Call the base class constructor with the parameters it needs
        super(PathException, self).__init__(message) 

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Funções --------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

def doNothing():
    time.sleep(9223372036.854775-9223372036.854775)
    pass

# -------

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Classes --------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

# -------

class card:
    # Atributos: player_owner, suit
    def __init__(self, player_owner):
        self.player_owner = player_owner  # Player que tem posse da carta (Nenhum por default)
        #self.territory_owner = territory_owner # Player recebe uma carta cada vez que captura um território
        self.suit = SUITS[random.randint(0, 2)] # Número aleatório entre 0 e 2 (♠, ♦ ou ♥)

    def __iter__(self):
        return self
    
# -------

class territory:
    #Atributos: owner, armies, neighbors, name
    def __init__(self, name, map, neighbors=None):
        self.owner = None  # Player atual no controle (vazio por default)
        self.armies = [] # Quantos armies estão no território atualmente, array de army
        self.neighbors = neighbors if neighbors is not None else [] # neighbors é um array de territórios
        self.name = name # Nome do território
        self.map = map # Mapa que representa o território

    def __iter__(self):
        return self

    # ---------------------------------------
    
    def colored_name(self):
        if self.owner == None:
            return self.name
        else:
            return self.owner.color+f"{self.name}"+END
        
    # ---------------------------------------

    def update_map_color(self):
        self.map.update_color(self.owner.color)

    # ---------------------------------------
    
    def set_neighbor(self, neighbor):
        print(f"Adicionando o vizinho {neighbor.colored_name()} para o território {self.colored_name()} e vice-versa...")
        self.neighbors.append(neighbor)
        neighbor.neighbors.append(self)
        
    # ---------------------------------------
    
    def set_owner(self, new_owner): # Set o dono do território
        self.owner = new_owner
        self.owner.get_territory(self)

    # ---------------------------------------
    
    def add_army(self, army):
        self.armies.append(army)

    # ---------------------------------------
    
    def remove_army(self, army):
        self.armies.remove(army)

    # ---------------------------------------
                 
    def print(self):
        string = (f"{self.colored_name()}:{len(self.armies)} -> | ")
        if self.neighbors != [] and self.neighbors != None: # Só entra no loop se tiver vizinhos
            for neighbor in self.neighbors:
                string += f"{neighbor.colored_name()} | "
        return (string)
    
    # ---------------------------------------
    
    def check_path(self, destination_territory):
        return True if destination_territory in self.neighbors else False
    
    # ---------------------------------------
    
    def attack(self, defender):
        while len(defender.armies) > 0 and len(self.armies) > 1: # Mínimo que fica de exército atacante é 1
            if self.armies[0].clash() < defender.armies[0].clash(): # Destroí o atacante
                lost_army = self.armies[0]
                self.armies.remove(lost_army)
                self.owner.armies.remove(lost_army)
                del lost_army
                print(f"Atacante: {len(self.armies)}")
            elif self.armies[0].clash() > defender.armies[0].clash(): # Destroí o defensor
                lost_army = defender.armies[0]
                defender.armies.remove(lost_army)
                defender.owner.armies.remove(lost_army)
                del lost_army 
                print(f"Defensor: {len(defender.armies)}")
        # Resultado
        if len(defender.armies) == 0: # Caí direto nesta condição se o território estava vazio
            print(f"Território {defender.colored_name()} tomado por {self.owner.print_name()}!")
            defender.lost_battle(self.owner)
            return True
        else:
            print("Ataque falhou!")
            return False
    
    # ---------------------------------------
    
    def lost_battle(self, new_owner):
        if self.owner is not None:
            self.owner.lose_territory(self)
            gameMain.check_death(self.owner, new_owner) # Checa se o antigo dono morreu ou não
        new_owner.get_territory(self)
        self.owner = new_owner
        self.update_map_color()
        new_owner.get_card() # Ganha uma carta por capturar um território

    # ---------------------------------------
    
    def movement(self, destination):
        while True:
            try:
                transfer = int(input(f"\tInforme o número de tropas que você pretende transferir do seu território para o novo (OBS: Minímo de 1 por território - Território de origem: {len(self.armies)} tropas): "))
                if (len(self.armies)-1 >= transfer) and (transfer > 0) and (len(self.armies)-1 > 0): # Quantidade que fica tem que ser pelo menos 1 e quantidade tem que ser maior que zero
                    for i in range (0,transfer):
                        destination.add_army(self.armies[0])
                        self.remove_army(self.armies[0])
                    break
                else:
                    raise ValueError
            except ValueError:
                print(f"\tNúmero de tropas informado inválido! Disponível para transferência: {len(self.armies)-1}")

# -------

class player:
    #Atributos: color, territories, game e armies
    def __init__(self, color):
        assert color in COLORS
        self.color = color
        self.territories = [] # Lista de territórios dominados
        self.armies = [] # Lista de tropas
        self.cards = [] # Lista de cartas
        print(color+"Jogador criado!"+END)

    def print(self):
        print(self.color+"\t-=Jogador=- ", end="")
        for card in self.cards:
            print(f"| {card.suit} |",end="")
        print(END)
        print(f"Quantidade de territórios dominados: {len(self.territories)}")
        print(f"Quantidade de tropas: {len(self.armies)}")

    def print_name(self): # Usada para retorna só o nome na hora de exibir a mensagem de vitória
        return str(self.color+"Jogador"+END)

    def death(self):
        return False if len(self.territories) > 0 else True
    
    def add_army(self, army):
        self.armies.append(army)

    def get_territory(self, territory):
        self.territories.append(territory)

    def lose_territory(self, territory):
        self.territories.remove(territory)

    def get_card(self, possible_card = None):
        if len(self.cards) < 5:
            new_card = card(self) if possible_card is None else possible_card
            self.cards.append(new_card)

    def lose_card(self, card):
        self.cards.remove(card)

    def deck(self):
        deck = []
        for i in range(0,5): # Retorna um deck de cinco cartas
            try:
                deck.append(self.cards[i])
            except IndexError:
                deck.append(None)
        return deck
    
    # ---------------------------------------

    def card_bonus(self): # Checa o bônus # WIP!!!!!!!!!!
        global card_bonus
        deck = self.deck() 
        heart_suit = 0 # (♠)
        spades_suit = 0 # (♥)
        gold_suit = 0 # (♦)
        for card in deck:
            if card is not None:
                card_suit = card.suit
                if card_suit == '♠':
                    spades_suit += 1
                elif card_suit == '♥':
                    heart_suit += 1
                elif card_suit == '♦':
                    gold_suit += 1
        string = None
        if (heart_suit >= 1 and spades_suit >= 1 and gold_suit >= 1):
            string = "(♠,♥,♦)"
        elif (heart_suit >= 3):
            string = "(♥,♥,♥)"
        elif (spades_suit >= 3):
            string = "(♠,♠,♠)"
        elif (gold_suit >= 3):
            string = "(♦,♦,♦)"
        if string is not None:
            print(f"\t---= Bônus de Cartas {string}! =---")
            print(f"Você tem cartas disponíveis para trocar por trocas - Bônus atual: {card_bonus} tropas")
            if sum(1 for card in deck if card is not None) >= 5:
                print(BOLD+"Troca Obrigatória!!!"+END)
                flag = True
            else:
                flag = str(input("Deseja trocar? (Sim ou derivados caso desejar)\n"))
                if flag.lower() in ("s","sim","yes","y","sí"):
                    flag = True
                else:
                    flag = False
            if flag:
                self.get_card_armies()
                self.consume_cards(string) # Consome três cartas usadas pelo bônus

    def get_card_armies(self):
        global card_bonus
        print(f"Recebido {card_bonus} tropas! Distribua elas entre seus territórios")
        for i in range(0,card_bonus): # Ganha duas tropas por round (por default)
            while True:
                try:
                    destination = int(input("\tPor favor, informe o número de um dos seus territórios: "))-1
                    if gameMain.territories[destination] not in self.territories:
                        raise IndexError
                except (IndexError, ValueError):
                    print("\tTerritório inválido! Informe um território aliado válido!")
                else:
                    break
            army(self, gameMain.territories[destination]) # OBS: Aqui está criando novas tropas
            print(f"Tropa enviada para o território {gameMain.territories[destination].colored_name()}")
        gameMain.exchanges += 1
        gameMain.increase_card_bonus()

    def consume_cards(self, kind_of_exchange):
        deck = self.deck()
        all_suits = ['♠', '♥', '♦']
        i = 0 # Contador de quantas cartas foram excluídas
        if kind_of_exchange == "(♠,♥,♦)":
            for card in deck:
                if i >= 3:
                    break
                if card is not None:
                    card_suit = card.suit
                    if card_suit in all_suits:
                        self.lose_card(card)
                        all_suits.remove(card_suit) # Consome um de cada naipe de carta
                        i += 1
        elif kind_of_exchange == "(♥,♥,♥)":
            for card in deck:
                if i >= 3:
                    break
                if card is not None:
                    card_suit = card.suit
                    if card_suit == '♥':
                        self.lose_card(card)
                        i += 1
        elif kind_of_exchange == "(♠,♠,♠)":
            for card in deck:
                if i >= 3:
                    break
                if card is not None:
                    card_suit = card.suit
                    if card_suit == '♠':
                        self.lose_card(card)
                        i += 1
        elif kind_of_exchange == "(♦,♦,♦)":
            for card in deck:
                if i >= 3:
                    break
                if card is not None:
                    card_suit = card.suit
                    if card_suit == '♦':
                        self.lose_card(card)
                        i += 1

    # ---------------------------------------

    def preparation(self): # Alocar novos armies
        global gameMain # Usa gameMain para ter acesso ao escopo total de territórios
        new_armies = int(ARMIES_PER_ROUND + len(self.territories)/3) # A cada 3 território ganha 1 extra além do básico
        print(f"Recebido {new_armies} tropas! Distribua elas entre seus territórios")
        for i in range(0,new_armies): # Ganha duas tropas por round (por default)
            while True:
                try:
                    destination = int(input("\tPor favor, informe o número de um dos seus territórios: "))-1
                    if gameMain.territories[destination] not in self.territories:
                        raise IndexError
                except (IndexError, ValueError):
                    print("\tTerritório inválido! Informe um território aliado válido!")
                else:
                    break
            army(self, gameMain.territories[destination]) # OBS: Aqui está criando novas tropas
            print(f"Tropa enviada para o território {gameMain.territories[destination].colored_name()}")

    # ---------------------------------------
    
    def attack(self):
        global gameMain # Usa gameMain para ter acesso ao escopo total de territórios
        while True:
            try:
                print("OBS: Digite o número 0 para cancelar a Etapa de Ataque!")
                origin = int(input("\tPor favor, informe o número de um dos seus territórios: "))-1
                if origin+1 == 0:
                    break
                destination = int(input("\tPor favor, informe o número de um território inimigo: "))-1
                if destination+1 == 0:
                    break
                elif (gameMain.territories[origin] not in self.territories) or (gameMain.territories[destination] in self.territories):
                    raise IndexError
                elif gameMain.territories[origin].check_path(gameMain.territories[destination]) == False:
                    raise PathException
            except (IndexError, ValueError):
                print("\tTerritórios inválidos! informe um território aliado e um território inimigo válidos!")
            except PathException as e:
                print(e)
                print("\n\tTerritórios inválidos! informe um território aliado e um território inimigo válidos!")
            else:
                if gameMain.territories[origin].attack(gameMain.territories[destination]):
                    #self.get_territory(gameMain.territories[destination]) # Toma o território
                    gameMain.territories[origin].movement(gameMain.territories[destination]) # Transfere um certo número de tropas

    # ---------------------------------------
    
    def movement(self): # Mudar a posição de tropas
        global gameMain # Usa gameMain para ter acesso ao escopo total de territórios
        while True:
            try:
                print("OBS: Digite o número 0 para cancelar a Etapa de Deslocamento!")
                origin = int(input("\tPor favor, informe o número de um dos seus territórios: "))-1
                if origin+1 == 0:
                    break
                destination = int(input("\tPor favor, informe o número de outro território aliado: "))-1
                if destination+1 == 0:
                    break
                elif (gameMain.territories[origin] not in self.territories) or (gameMain.territories[destination] not in self.territories):
                    raise IndexError
                elif (len(gameMain.territories[origin].armies)-1 == 0):
                    print("Quantidade de tropas insuficiente!!")
                    raise IndexError
                elif gameMain.territories[origin].check_path(gameMain.territories[destination]) == False:
                    raise PathException
            except (IndexError, ValueError):
                print("\tTerritórios inválidos! informe dois territórios aliados válidos!")
            except PathException as e:
                print(e+"\n\tTerritórios inválidos! informe dois territórios aliados válidos!")
            else:
                gameMain.territories[origin].movement(gameMain.territories[destination]) # Transfere um certo número de tropas

# -------

class army:
    #Atributos:
    def __init__(self, owner, territory):
        self.owner = owner
        self.territory = territory
        self.owner.add_army(self)
        self.territory.add_army(self)

    # ---------------------------------------
    
    def clash(self): # Método usado durante o ataque
        return (random.randint(1, 7)) # Número aleatório entre 1 e 6

    # ---------------------------------------
    
    def movement(self, new_territory):
        self.territory.remove_army(self)
        self.territory = new_territory
        new_territory.add_army(self)
        
# -------

class world:
    #Atributos: game e territories
    def __init__(self, game, territories):
        self.game = game
        self.territories = territories # territories é um array de territórios

    # ---------------------------------------

    def start(self):
        temp_list = self.territories.copy()
        random.shuffle(temp_list)
        i = 0
        for player in self.game.players: # Colocando os territórios e tropas iniciais
            temp_list[i].set_owner(player)
            temp_list[i].update_map_color()
            for j in range(0, STARTING_ARMIES): # Cinco armies por player (default)
                army(player, temp_list[i])
            i += 1

    # ---------------------------------------
    
    def print(self):
        i=1
        for territory in self.territories:
            print(f"{i}. {territory.print()}")
            i += 1

# -------

class game:
    #Atributos: current_round, current_player, territories, player e world
    def __init__(self, list_of_players, territories, map):
        self.current_round = 1
        self.current_player_number = 0
        self.current_player = list_of_players[self.current_player_number] # Array de players
        self.territories = territories # territories é um array de territórios
        self.players = list_of_players
        self.world = world(self, self.territories) # Game cria o mundo, mundo contêm os territórios, que contêm as conexões
        self.exchanges = 0 # Número de trocas já realizadas até o momento atual
        self.map = map # Mapa do mundo completo

    # ---------------------------------------

    def start(self):
        self.world.start()
        #self.world.print()
        #for i in range(0,10):
        while True:
            self.round()
            winner = self.check_victory()
            if winner is not None:
                self.victory(winner)

    # ---------------------------------------           

    def check_victory(self):
        return None if len(self.players) != 1 else self.players[0]
    
    # ---------------------------------------
    
    def victory(self,winner):
        typewriterPrint(f"{winner.print_name()}"+GREEN+" venceu!!!"+END) # Printando em verde
        self.world.print()
        winner.print()
        exit()

    # ---------------------------------------

    def round(self):
        print(f"--------- Round {self.current_round} ---------")
        self.map.print()
        self.world.print()
        self.current_player = self.players[self.current_player_number]
        self.current_player.print()
        self.current_player.card_bonus()
        print(BOLD+"-Etapa de Preparação-"+END)
        self.current_player.preparation()
        print(BOLD+"-Etapa de Ataque-"+END)
        self.current_player.attack()
        print(BOLD+"-Etapa de Deslocamento-"+END)
        self.current_player.movement()

        for player in self.players:
            player.death()

        self.current_round += 1
        self.current_player_number = (self.current_player_number+1) if self.current_player_number+1 < len(self.players) else 0

    # ---------------------------------------

    def check_death(self, player, killer):
        if player.death():
            typewriterPrint(f"{player.print_name()}"+RED+" foi morto por "+END+f"{killer.print_name()}"+RED+"!!!"+END)
            self.players.remove(player)
            for card in player.cards:
                player.lose_card(card)
                if len(killer.cards) == 5: # Limite de 5 cartas por jogador
                    break
                killer.get_card(card) # Killer recebe as cartas do jogador morto
            del player

    # ---------------------------------------

    def increase_card_bonus(self): # Por enquanto tá usando a Sequência de Fibonacci
        global card_bonus
        previousOne = 1
        fibonacci = 1
        #prime_numbers = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 
        # 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 
        # 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 
        # 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 
        # 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 
        # 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 
        # 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 
        # 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]
        for i in range(0,self.exchanges):
            #print(f"{fibonacci} - ", end="")
            previousTwo = previousOne
            previousOne = fibonacci
            fibonacci = previousOne + previousTwo 
        card_bonus = previousOne

    # ---------------------------------------

# -------

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Funções auxiliares ---------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

def typewriterPrint(message): # Um print lento com efeito de "máquina de escrever"
    for x in message:
        print(x, end='')
        sys.stdout.flush()
        time.sleep(0.1)
    print('\n', end='') # Pulando linha

# -------

def doNothing():
    time.sleep(9223372036.854775-9223372036.854775)
    pass

# -------

def clear(): # Limpa o terminal
    os.system('cls' if os.name == 'nt' else 'clear')

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Variáveis Globais do Mapa --------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

# ╚╔║╝╗═
# ♣ ♥ ♦ ♠

complete_art =  "\n" \
"                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣄⣠⣀⡀⣀⣠⣤⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⢠⣠⣼⣿⣿⣿⣟⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⢠5⣦⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⢦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣟⣾⣿⣽⣿⣿⣅⠈⠉⠻⣿⣿4⣿⣿⡿⠇⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⢀⡶⠒⢉⡀⢠⣤⣶⣶⣿⣷⣆⣀⡀⠀⢲⣖⠒⠀⠀⠀⠀⠀⠀⠀\n" \
"⢀⣤⣾⣶⣦⣤⣤⣶⣿⣿⣿⣿⣿⣿⣽⡿⠻⣷⣀⠀⢻⣿⣿⣿⡿⠟⠀⠀⠀⠀⠀⠀⣤⣶⣶⣤⣀⣀⣬⣷⣦⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⣤⣦⣼⣀⠀\n" \
"⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠓⣿⣿⠟⠁⠘⣿⡟⠁⠀⠘⠛⠁⠀⠀⢠⣾⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿7⣿⣿⣿⣿⣿⣿⣿⡿⠏⠙⠁\n" \
"⠀⠸⠟⠋⠀⠈⠙⣿⣿⣿⣿⣿⣿⣷⣦⡄⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⣼⣆⢘⣿⣯⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡉⠉⢱⡿⠀⠀⠀⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⡿⠦⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿6⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⡗⠀⠈⠀⠀⠀⠀⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿3⣿⣿⣿⣿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣉⣿⡿⢿⢷⣾⣾⣿⣞⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⣠⠟⠀⠀⠀⠀⠀⠀⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⠿⠿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣾⣿⣿⣷⣦⣶⣦⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠈⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⣿⣤⡖⠛2⠤⡀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿10⣿⣿⣿⣿⣿⣿⡿⠁⠙⣿⣿⠿8⣿⣿⡿⠋⢩⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠧⣤⣦⣤⣄⡀⠀⠀⠀⠀⠀⠘⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠘⣧⠀⠈⣹⡻⠇⢀⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣤⣀⡀⠀⠀⠀⠀⠀⠀⠈⢽⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⣴⣿⣷⢲⣦⣤⡀⢀⡀⠀⠀⠀⠀⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿1⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⢸⣿11⣿⣷⢀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠂⠛⣆⣤⡜⣟⠋⠙⠂⠀⠀⠀⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⠉⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣾⣿⣿⣿⣿⣆⠀⠰⠄⠀⠉⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⠿⠿9⣿⣿⠇⠀⠀⢀⠀⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡿⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⡇⠀⠀⢀⣼⠗⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠃⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠁⠀⠀⠀\n" \
"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"

south_america_art = [ "⠀⠀⢠⣿⣿⣿⣿⣿⣤⣀⡀",
                      "⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿1⣿⣿⣿⠟⠀⠀",
                      "⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⠟⠀",
                      "⠀⠀⠀⠀⠀⠀⣸⣿⣿⡿⠃⠀⠀",
                      "⠀⠀⠀⠀⠀⠀⢀⣿⡿⠛⠀⠀",
                      "⠀⠀⠀⠀⠀⠀⢸⣿⠃⣀⠀⠀⠀",
                      "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠒⠀"]

central_america_art = [ "⣤⡖⠛2⠤⡀⠀⠀⠀⠀",
                "⠀⠀⠀⠀⠈⠙⠧⣤⣦⣤⣄⡀⠀⠀"]

north_america_art = ["⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⢠⣠⣼⣿⣿⣿⣟⣿",
                     "⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣟⣾⣿⣽⣿⣿⣅",
                     "⢀⣤⣾⣶⣦⣤⣤⣶⣿⣿⣿⣿⣿⣿⣽⡿⠻⣷⣀⠀",
                     "⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠓⣿⣿⠟⠁",
                     "⠀⠸⠟⠋⠀⠈⠙⣿⣿⣿⣿⣿⣿⣷⣦⡄⣿⣿⣿⣆",
                     "⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⡿⠦",
                     "⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿3⣿⣿⣿⣿⠋⠁",
                     "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⠿⠿⣿⠁⠀",
                     "⠀⠀⠀⠀⠉⠻⣿" ]

oceania_art =       ["⠀⣤⣾⣿⣿⣿⣿⣆⠀⠰⠄⠀⠉",
                     "⠀⢻⣿⠿⠿9⣿⣿⠇⠀⠀⢀⠀⠀⠀",
                     "⠀⠈⢻⡇⠀⠀⢀⣼⠗⠀",
                     "⠀⠀⠀⠙⠁⠀⠀⠀"]

sahara_art = ["⠀⠀⠀⠀⣀⣾⣿⣿⣷⣦⣶⣦⣼⣿⣿⣿⣿",
              "⠀⠀⠀⢰⣿⣿⣿⣿10⣿⣿⣿⣿⣿⣿⡿⠁",
              "⠀⠘⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀" ]

lower_africa_arts = ["⠀⠈⢽⣿⣿⣿⣿⣿⠋⠀",
                     "⠀⠀⢸⣿11⣿⣷⢀⡄⠀⠀",
                     "⠀⠘⣿⣿⣿⣿⠉⣿⠃",
                     "⠀⠀⠀⢹⣿⡿⠃⠀⠀⠀⠀⠀" ]

greenland_arts = ["⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀",
                     "⠈⠉⠻⣿⣿4⣿⣿⡿⠇⠀⠀",
                     "⢻⣿⣿⣿⡿⠟⠀",
                     "⠘⣿⡟⠁⠀⠘⠛⠁⠀" ]

europe_arts = ["⠀⠀⠀⠀⠀⢀⡶⠒",
                     "⠀⠀⠀⣤⣶⣶⣤⣀⣀⣬⣷",
                     "⠀⢠⣾⣿⢿⣿⣿⣿⣿⣿⣿",
                     "⠀⣼⣆⢘⣿⣯⣼⣿⣿⣿⣿⣿⣿",
                     "⠀⠙⣿⣿6⣿⣿⣿⣿⣿⣿⣿⣿",
                     "⠀⢿⣿⣉⣿⡿⢿⢷⣾⣾⣿⣞⣿" ]

upper_asia_arts = ["⠀⠰⢦⣄⠀⠀⠀⠀⠀⠀",
                     "⢉⡀⢠⣤⣶⣶⣿⣷⣆⣀⡀⠀⢲⣖⠒⠀⠀⠀⠀⠀⠀⠀",
                     "⣦⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⣤⣦⣼⣀⠀",
                     "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿7⣿⣿⣿⣿⣿⣿⣿⡿⠏⠙⠁",
                     "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡉⠉⢱⡿⠀⠀⠀",
                     "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⡗⠀⠈⠀⠀",
                     "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⣠⠟⠀",
                     "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠈⠛⠁⠀⠀⠀" ]

lower_asia_arts = ["⠙⣿⣿⠿8⣿⣿⡿⠋⢩⠀⠀⠀",
                     "⠀⠘⣧⠀⠈⣹⡻⠇⢀⣿⡆⠀⠀",
                     "⠀⠀⠀⠀⠹⣷⣴⣿⣷⢲⣦⣤⡀⢀⡀⠀⠀",
                     "⠀⠈⠉⠂⠛⣆⣤⡜⣟⠋⠙⠂⠀⠀⠀⠀" ]

artic_island_arts = ["⢀⣀⣄⣠⣀⡀⣀⣠⣤⣤⣤⣀⠀⠀",
                     "⢠5⣦⡄",
                     "⠀⠉⠀⠀⠀⠀⠀⢀⡶⠒" ]

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Classes do Mapa ------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

class fragment:
    def __init__(self, color, arts=None):
        self.color = color
        self.original_arts = arts if arts is not None else []
        self.modified_arts = []
        for i in self.original_arts:
            self.modified_arts.append(i.replace(i,color+i+END))

    def alter(self,art):
        assert (str(type(art)).lower() == "<class 'str'>")
        for i in self.original_arts:
            art = art.replace(i, self.modified_arts[self.original_arts.index(i)])
        return art
    
    def update_color(self, new_color):
        assert (str(type(new_color)).lower() == "<class 'str'>")
        previous_color = self.color
        self.color = new_color
        for i in range(0,len(self.modified_arts)):
            self.modified_arts[i] = self.modified_arts[i].replace(previous_color,self.color)

    def __iter__(self):
        return self

# ----------------------------------------------------------------------------------------------------

class complete_artpiece:
    def __init__(self, art, fragments=None):
        self.art = art
        self.fragments = fragments if fragments is not None else []

    def original_print(self):
        print(self.art)

    def print(self):
        final_art = self.art
        for i in self.fragments:
            #print(i.color+"Teste"+END) # Mostra a cor de cada fragmento
            final_art = i.alter(final_art)
        print(final_art)

    def __iter__(self):
        return self

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Função Main ----------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

def main():
    clear() # Limpa o terminal
    print("------------------ War Game in Console Terminal ------------------")

    # --------------------------------------- Preparando o mapa ---------------------------------------

    # Em resumo, complete_artpiece armazena a arte completa enquanto que fragments armazenam os trechos que devem ter a cor alterada
    south_america_fragment = fragment(BOLD, south_america_art) # Funciona
    central_america_fragment = fragment(BOLD, central_america_art) # Funciona
    north_america_fragment = fragment(BOLD, north_america_art) # Funciona
    oceania_fragment = fragment(BOLD, oceania_art) # Funciona
    sahara_fragment = fragment(BOLD, sahara_art) # Funciona
    lower_africa_fragment = fragment(BOLD, lower_africa_arts) # Funciona
    greenland_fragment = fragment(BOLD, greenland_arts)
    europe_fragment = fragment(BOLD, europe_arts)
    upper_asia_fragment = fragment(BOLD, upper_asia_arts)
    lower_asia_fragment = fragment(BOLD, lower_asia_arts)
    artic_island_fragment = fragment(BOLD, artic_island_arts)
    fragments = [south_america_fragment,central_america_fragment,north_america_fragment,oceania_fragment,sahara_fragment,lower_africa_fragment, greenland_fragment, artic_island_fragment, europe_fragment, lower_asia_fragment, upper_asia_fragment]

    world_map = complete_artpiece(complete_art, fragments)
    #world_map.original_print()
    world_map.print()

    # --------------------------------------- Definindo jogadores e territórios do mapa ---------------------------------------
    playerGreen = player(color = GREEN)
    playerBlue = player(color = BLUE)
    playerRed = player(color = RED)
    playerYellow = player(color = YELLOW)
    #playerCyan = player(color = CYAN)
    #playerPurple = player(color = PURPLE)
    #playerBlack = player(color = BLACK)

    players=[playerGreen,playerBlue,playerRed,playerYellow] # Lista e ordem dos jogadores
    #players=[playerGreen,playerBlue,playerRed,playerYellow, playerCyan, playerPurple, playerBlack]

    # Criando os territórios
    south_america = territory("América do Sul", south_america_fragment)
    central_america = territory("América Central", central_america_fragment)
    north_america = territory("América do Norte", north_america_fragment)
    greenland = territory("Groenlândia", greenland_fragment)
    artic_islands = territory("Ilhas do Ártico", artic_island_fragment)
    europe = territory("Europa", europe_fragment)
    upper_asia = territory("Ásia", upper_asia_fragment)
    lower_asia = territory("Ásia Central", lower_asia_fragment)
    oceania = territory("Oceania", oceania_fragment)
    sahara = territory("Deserto do Saara", sahara_fragment)
    lower_africa = territory("África Subsaariana", lower_africa_fragment)

    # Criando as conexões
    south_america.set_neighbor(central_america)
    central_america.set_neighbor(north_america)
    north_america.set_neighbor(greenland)
    greenland.set_neighbor(artic_islands)
    greenland.set_neighbor(europe)
    artic_islands.set_neighbor(europe)
    europe.set_neighbor(upper_asia)
    europe.set_neighbor(sahara)
    upper_asia.set_neighbor(lower_asia)
    upper_asia.set_neighbor(sahara)
    lower_asia.set_neighbor(sahara)
    lower_asia.set_neighbor(oceania)
    sahara.set_neighbor(lower_africa)
    
    territories = [south_america, central_america, north_america, greenland, artic_islands, europe, upper_asia, lower_asia, oceania, sahara, lower_africa]

    assert len(territories) >= len(players)

    # ---------------------------------------
    global gameMain
    gameMain = game(players, territories, world_map) # OBS: Cada jogador começa com um território e cinco armies (por default)
    gameMain.start() # OBS: Selecione o número do território
    # ---------------------------------------

# ----------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(YELLOW+"\nPrograma encerrado via terminal..."+END)

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Fim do código --------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------  