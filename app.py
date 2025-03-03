import itertools
import random
import streamlit as st
from time import sleep

def configure_page():
    ICON_URL = "assets/navbar icon.png"
    st.set_page_config(
        page_title="El Dorado Slots",  
        page_icon=ICON_URL,  
        layout="centered"  
    )
    
    # Add custom CSS styling for a vintage look
    st.markdown("""
        <style>
            body {
                background-color: #f5f5dc; /* Beige vintage background */
                font-family: 'Georgia', serif;
                color: #3e3e3e;
            }
            .title {
                text-align: center;
                font-size: 3em;
                color: #8b4513; /* SaddleBrown */
                text-shadow: 1px 1px 2px #fff;
                font-weight: bold;
                margin-top: 20px;
            }
            .spin-message {
                text-align: center;
                font-size: 1.5em;
                margin-bottom: 20px;
                color: #8b4513;
            }
            .stButton>button {
                background-color: #8b4513;
                color: #f5f5dc;
                border: 2px solid #f5f5dc;
                border-radius: 5px;
                font-size: 1em;
                padding: 10px 20px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
            }
            .reel {
                text-align: center;
                font-size: 60px;
                padding: 10px;
                border: 2px solid #8b4513;
                border-radius: 10px;
                background-color: #f8f0e3;
                margin: 5px;
            }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("<h1 class='title'>El Dorado Slots</h1>", unsafe_allow_html=True)

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
        # Create all possible combinations of 3 symbols
        permutations = list(itertools.product(self.SYMBOLS.keys(), repeat=3))
        # Add guaranteed jackpot combinations (all symbols matching) for extra excitement
        for symbol in self.SYMBOLS.keys():
            permutations.append((symbol, symbol, symbol))
        return permutations

    def _get_final_result(self, level):
        result = list(random.choice(self.permutations))
        # For certain levels, increase the chance for two matching symbols (building suspense)
        if level in ['2', '3', '4'] and len(set(result)) == 3 and random.randint(0, 10) >= 1:
            result[1] = result[0]
        return result

    def _display(self, amount_bet, result, time_interval=0.2):
        st.markdown("<h3 class='spin-message'>🎰 Spinning... 🎰</h3>", unsafe_allow_html=True)
        
        # Create three columns for the reels and use placeholders to update in place
        reel_cols = st.columns(3)
        reel_placeholders = [col.empty() for col in reel_cols]
        
        # Animate each reel sequentially
        for i in range(3):
            spin_duration = 2  # Spin duration per reel in seconds
            iterations = int(spin_duration / time_interval)
            for _ in range(iterations):
                random_symbol = random.choice(list(self.SYMBOLS.keys()))
                reel_placeholders[i].markdown(
                    f"<div class='reel'>{self.SYMBOLS[random_symbol]}</div>",
                    unsafe_allow_html=True
                )
                sleep(time_interval)
            # Reveal final symbol for the reel
            reel_placeholders[i].markdown(
                f"<div class='reel' style='font-size:80px;'>{self.SYMBOLS[result[i]]}</div>",
                unsafe_allow_html=True
            )
            # Pause briefly between reels for extra suspense
            sleep(0.5)
        
        # Check result and show appropriate message
        if self._check_result_user(result):
            st.success(f'You won and received: R${amount_bet * 2:.2f}')
            st.balloons()  # Celebrate a win!
        else:
            st.warning('That was close! Try again next time.')

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
    # Initialize player balance and game state
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
