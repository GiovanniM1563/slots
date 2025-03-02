import itertools
import random
import streamlit as st
from time import sleep

def configure_page():
    ICON_URL = "assets/navbar icon.png"

    st.set_page_config(
        page_title="Death Lucky Casino",  
        page_icon="assets/navbar icon.png",  
        layout="centered"  
    )
  
    st.markdown(f"<h1>☠Death Lucky Casino☠</h1>", unsafe_allow_html=True)

# Player Class
class Player:
    def __init__(self, balance=0):
        self.balance = balance

# Slot Machine Class
class SlotMachine:
    def __init__(self):
        self.SYMBOLS = {
            'Lemon': '🍋',
            'Cherry': '🍒',
            'Seven': '7️⃣',
            'Orange': '🍊',
            'Bell': '🔔',
            'Bar': 'BAR'
        }
        self.levels = ['1', '2', '3', '4']
        self.balance = 0
        self.permutations = self._gen_permutations()

    def _gen_permutations(self):
        permutations = list(itertools.product(self.SYMBOLS.keys(), repeat=3))
        for symbol in self.SYMBOLS.keys():
            permutations.append((symbol, symbol, symbol))  # Ensuring jackpots are possible
        return permutations

    def _get_final_result(self, level):
        result = list(random.choice(self.permutations))
        if level in ['3', '4', '2'] and len(set(result)) == 3 and random.randint(0, 10) >= 1:
            result[1] = result[0]  # Adjusting for a higher chance of two matching symbols
        return result

    def _display(self, amount_bet, result, time=0.5):
        st.markdown("<h3 style='text-align:center;'>🎰 Spinning... 🎰</h3>", unsafe_allow_html=True)
        seconds = 4
        placeholder = st.empty()
        for _ in range(int(seconds / time)):
            placeholder.markdown(
                f"<div style='text-align:center; font-size:60px;'>{self._emojize(random.choice(self.permutations))}</div>",
                unsafe_allow_html=True
            )
            sleep(time)
        placeholder.markdown(
            f"<div style='text-align:center; font-size:80px;'>{self._emojize(result)}</div>",
            unsafe_allow_html=True
        )

        if self._check_result_user(result):
            st.success(f'You won and received: R${amount_bet * 2}')
        else:
            st.warning('That was close! Try again next time.')

    def _emojize(self, symbols):
        return ' | '.join(self.SYMBOLS[symbol] for symbol in symbols)

    def _check_result_user(self, result):
        return result[0] == result[1] == result[2]

    def _update_balance(self, amount_bet, result, player: Player):
        if self._check_result_user(result):
            player.balance += amount_bet * 2
            self.balance -= amount_bet * 2
        else:
            player.balance -= amount_bet
            self.balance += amount_bet * 2

    def play(self, amount_bet, player: Player):
        level = random.choice(self.levels)
        result = self._get_final_result(level)
        self._display(amount_bet, result)
        self._update_balance(amount_bet, result, player)

# User Interaction Function
def start_game():
    # Initialize player balance
    if "player" not in st.session_state:
        st.session_state["player"] = None

    if "game_active" not in st.session_state:
        st.session_state["game_active"] = True

    if st.session_state["player"] is None:
        initial_balance = st.text_input("Enter your initial balance (use '.' for cents):", value="", key="initial_balance_input")
        balance_ok = st.button("OK", key="balance_ok")

        if balance_ok:
            try:
                initial_balance = float(initial_balance)
                if initial_balance > 0:
                    st.session_state["player"] = Player(balance=initial_balance)
                    st.success(f"Your initial balance is: R${st.session_state['player'].balance:.2f}")
                else:
                    st.warning("Please enter a valid initial balance to start playing.")
            except ValueError:
                st.error("Please enter a valid number.")

    if st.session_state["game_active"] and st.session_state["player"] is not None:
        player = st.session_state["player"]

        if player.balance > 0:
            bet = st.text_input(f"Enter your bet amount (Available balance: R${player.balance:.2f})", value="", key="bet_input")
            bet_ok = st.button("OK", key="bet_ok")

            if bet_ok:
                try:
                    amount_bet = float(bet)
                    if amount_bet <= 0:
                        st.error("The bet must be greater than 0.")
                    elif amount_bet > player.balance:
                        st.error("You do not have enough balance for this bet.")
                    else:
                        casino = SlotMachine()
                        casino.play(amount_bet, player)
                        st.write(f"Your current balance is: R${player.balance:.2f}")

                        col1, col2 = st.columns(2)
                        with col1:
                            continue_yes = st.button("Play again", key="continue_yes")
                        with col2:
                            continue_no = st.button("Exit game", key="continue_no")

                        if continue_yes:
                            st.session_state["game_active"] = True
                        elif continue_no:
                            st.success("Thank you for playing! See you next time!")
                            st.session_state["game_active"] = False

                        if player.balance <= 0:
                            st.warning("You ran out of balance. Game over!")
                            st.session_state["game_active"] = False
                except ValueError:
                    st.error("Please enter a valid numeric value.")

        else:
            st.warning("You ran out of balance. Game over!")
            st.session_state["game_active"] = False

if __name__ == "__main__":
    configure_page()
    start_game()

