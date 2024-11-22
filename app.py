import itertools
import random
import streamlit as st
from time import sleep

# Função para configurar a página, incluindo o ícone e o fundo
def configurar_pagina():
    # URL das imagens no repositório GitHub
    BACKGROUND_URL = "BACKGROUND.png"
    NAVBAR_ICON_URL = "navbar icon.png"
    
    # Definir o ícone e o título da página
    st.set_page_config(
        page_title="Death Lucky Cassino",  # Título da página
        page_icon=NAVBAR_ICON_URL,  # URL do ícone da página
        layout="wide"
    )
    
    # Adicionar a imagem de fundo e a navbar
    st.markdown(
        f"""
        <style>
        body {{
            background-image: url("{BACKGROUND_URL}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #333;
            padding: 10px 20px;
        }}
        .navbar img {{
            height: 50px;  /* Ajuste o tamanho do logo conforme necessário */
        }}
        .navbar a {{
            color: white;
            text-decoration: none;
            font-size: 18px;
            margin-left: 20px;
        }}
        .navbar a:hover {{
            color: #ff0;
        }}
        </style>
        """, unsafe_allow_html=True)

    # Navbar com logo do "Cassa Niquel"
    st.markdown(
        f"""
        <div class="navbar">
            <img src="{NAVBAR_ICON_URL}" alt="Logo do Cassino">
        </div>
        """, unsafe_allow_html=True)

# Classe Player
class Player:
    def __init__(self, balance=0):
        self.balance = balance

# Classe CassaNiquel
class CassaNiquel:
    def __init__(self):
        self.SIMBOLOS = {
            'smirking face': '1F60F',
            'collision': '1F4A5',
            'smiling face with sunglasses': '1F60E',
            'smiling face with horns': '1F608',
            'alien': '1F47D'
        }
        self.levels = ['1', '2', '3', '4']
        self.balance = 0
        self.permutations = self._gen_permutations()

    # Matriz de 3 por 3 com os símbolos
    def _gen_permutations(self):
        permutations = list(itertools.product(self.SIMBOLOS.keys(), repeat=3))

        # Chance do usuário ganhar
        for i in self.SIMBOLOS.keys():
            permutations.append((i, i, i))
        return permutations
    
    # Figuras aleatórias para a matriz
    def _get_final_result(self, level):
        result = list(random.choice(self.permutations))

         # Chance de ganhar com base no nível
        if level in ['3', '4', '2'] and len(set(result)) == 3 and random.randint(0, 10) >= 2:
            result[1] = result[0]

        return result
        
    # Display com tempo tanto de rolagem das imagens como o tempo que elas vão acontecer
    def _display(self, amout_bet, result, time=0.5):
        seconds = 4
        for _ in range(int(seconds / time)):
            st.text(self._emojize(random.choice(self.permutations)))
            sleep(time)
        st.text(self._emojize(result))

        # Mensagem para o usuário
        if self._check_result_user(result):
            st.success(f'Você venceu e recebeu: R${amout_bet * 2}')
        else:
            st.warning('Essa foi por pouco! Na próxima você ganha, tente novamente.')

    # Emojis
    def _emojize(self, emojis):
        return ''.join(chr(int(self.SIMBOLOS[code], 16)) for code in emojis)
    
    # Resultados dos usuários, se a tupla for igual o usuário ganhou
    def _check_result_user(self, result):
        return result[0] == result[1] == result[2]
    
    # Atualizando o balance com os ganhos e as perdas
    def _update_balance(self, amout_bet, result, player: Player):
        if self._check_result_user(result):
            player.balance += amout_bet * 2  # Jogador ganha o dobro da aposta
            self.balance -= amout_bet * 2    # Máquina paga a aposta (reduz seu saldo)
        else:
            player.balance -= amout_bet            # Jogador perde a aposta
            self.balance += amout_bet * 2       # Máquina ganha a aposta (aumenta seu saldo)

    # Função play
    def play(self, amout_bet, player: Player):
        level = random.choice(self.levels)  # Seleciona um nível aleatório para cada jogada
        result = self._get_final_result(level)
        self._display(amout_bet, result)
        self._update_balance(amout_bet, result, player)

# Inicializa o saldo do jogador
if "player" not in st.session_state:
    st.session_state["player"] = None

if "jogo_ativo" not in st.session_state:
    st.session_state["jogo_ativo"] = True

if st.session_state["player"] is None:
    saldo_inicial = st.text_input("Insira seu saldo inicial (use '.' para centavos):", value="", key="saldo_inicial_input")
    saldo_ok = st.button("OK")

    if saldo_ok:
        try:
            saldo_inicial = float(saldo_inicial)
            if saldo_inicial > 0:
                st.session_state["player"] = Player(balance=saldo_inicial)
                st.write(f"Seu saldo inicial é: R${st.session_state['player'].balance:.2f}")
            else:
                st.warning("Por favor, insira um saldo inicial válido para começar a jogar.")
        except ValueError:
            st.error("Por favor, insira um número válido.")
