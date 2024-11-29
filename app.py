import itertools
import random
import streamlit as st
from time import sleep

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

    def _gen_permutations(self):
        permutations = list(itertools.product(self.SIMBOLOS.keys(), repeat=3))
        for i in self.SIMBOLOS.keys():
            permutations.append((i, i, i))
        return permutations

    def _get_final_result(self, level):
        result = list(random.choice(self.permutations))
        if level in ['3', '4', '2'] and len(set(result)) == 3 and random.randint(0, 10) >= 2:
            result[1] = result[0]
        return result

    def _display(self, amout_bet, result):
        st.write("🎰 Girando... 🎰")
        sleep(1)
        st.write(self._emojize(result))

        if self._check_result_user(result):
            st.success(f'Você venceu e recebeu: R${amout_bet * 2}')
        else:
            st.warning('Essa foi por pouco! Na próxima você ganha, tente novamente.')

    def _emojize(self, emojis):
        return ''.join(chr(int(self.SIMBOLOS[code], 16)) for code in emojis)

    def _check_result_user(self, result):
        return result[0] == result[1] == result[2]

    def _update_balance(self, amout_bet, result, player: Player):
        if self._check_result_user(result):
            player.balance += amout_bet * 2
            self.balance -= amout_bet * 2
        else:
            player.balance -= amout_bet
            self.balance += amout_bet * 2

    def play(self, amout_bet, player: Player):
        level = random.choice(self.levels)
        result = self._get_final_result(level)
        self._display(amout_bet, result)
        self._update_balance(amout_bet, result, player)

# Função principal de interação com o usuário usando o Streamlit
def iniciar_jogo():
    st.title("💀Death Lucky Cassino💀")

    # Inicializa o saldo do jogador
    if "player" not in st.session_state:
        st.session_state["player"] = None

    if "jogo_ativo" not in st.session_state:
        st.session_state["jogo_ativo"] = True

    if st.session_state["player"] is None:
        saldo_inicial = st.text_input("Insira seu saldo inicial (use '.' para centavos):", value="")
        saldo_ok = st.button("OK")

        if saldo_ok:
            try:
                saldo_inicial = float(saldo_inicial)
                if saldo_inicial > 0:
                    st.session_state["player"] = Player(balance=saldo_inicial)
                    st.success(f"Seu saldo inicial é: R${st.session_state['player'].balance:.2f}")
                else:
                    st.warning("Por favor, insira um saldo inicial válido para começar a jogar.")
            except ValueError:
                st.error("Por favor, insira um número válido.")

    if st.session_state["jogo_ativo"] and st.session_state["player"] is not None:
        player = st.session_state["player"]

        if player.balance > 0:
            aposta = st.text_input(f"Digite o valor da sua aposta (Saldo disponível: R${player.balance:.2f})", value="")
            aposta_ok = st.button("OK")

            if aposta_ok:
                try:
                    amout_bet = float(aposta)
                    if amout_bet <= 0:
                        st.error("A aposta deve ser maior que 0.")
                    elif amout_bet > player.balance:
                        st.error("Você não tem saldo suficiente para essa aposta.")
                    else:
                        cassino = CassaNiquel()
                        cassino.play(amout_bet, player)
                        st.write(f"Seu saldo atual é: R${player.balance:.2f}")

                        continuar_sim = st.button("Jogar novamente")
                        continuar_nao = st.button("Sair do jogo")

                        if continuar_sim:
                            st.session_state["jogo_ativo"] = True
                        elif continuar_nao:
                            st.success("Obrigado por jogar! Até a próxima!")
                            st.session_state["jogo_ativo"] = False

                        if player.balance <= 0:
                            st.warning("Você ficou sem saldo. Fim de jogo!")
                            st.session_state["jogo_ativo"] = False
                except ValueError:
                    st.error("Por favor, insira um valor numérico válido.")

        else:
            st.warning("Você ficou sem saldo. Fim de jogo!")
            st.session_state["jogo_ativo"] = False

if __name__ == "__main__":
    iniciar_jogo()
