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
    
    # Add custom CSS styling for a darker, slot-machine style
    st.markdown("""
        <style>
            body {
                background-color: #222; /* Dark background */
                font-family: 'Georgia', serif;
                color: #f2f2f2;
            }
            .title {
                text-align: center;
                font-size: 3em;
                color: gold; /* Make the title stand out on dark bg */
                text-shadow: 1px 1px 2px #000;
                font-weight: bold;
                margin-top: 20px;
            }
            .spin-message {
                text-align: center;
                font-size: 1.5em;
                margin-bottom: 20px;
                color: gold;
            }
            .stButton>button {
                background-color: gold;
                color: #000;
                border: 2px solid #fff;
                border-radius: 5px;
                font-size: 1em;
                padding: 10px 20px;
                box-shadow: 2px 2px 5px rgba(255,255,255,0.3);
            }
            .reel {
                text-align: center;
                font-size: 60px;
                padding: 10px;
                border: 2px solid gold;
                border-radius: 10px;
                background-color: #444; /* Reel background */
                margin: 5px;
            }
            .slot-machine {
                width: 650px;
                margin: 30px auto;
                padding: 20px;
                background-color: #333; /* Cabinet background */
                border: 5px solid gold;
                border-radius: 15px;
                box-shadow: 0 0 15px gold; /* Neon glow */
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
        # Define symbols with "Bar" in black
        self.SYMBOLS = {
            'Lemon': '🍋',
            'Cherry': '🍒',
            'Seven': '7️⃣',
            'Orange': '🍊',
            'Bell': '🔔',
            'Bar': '<span style="color:black;">BAR</span>'
        }
        self.levels = ['1', '2', '3', '4']
        self.balance = 0
        self.permutations = self._gen_permutations()

    def _gen_permutations(self):
        permutations = list(itertools.product(self.SYMBOLS.keys(), repeat=3))
        for symbol in self.SYMBOLS.keys():
            permutations.append((symbol, symbol, symbol))
        return permutations

    def _get_final_result(self, level):
        result = list(random.choice(self.permutations))
        if level in ['2', '3', '4'] and len(set(result)) == 3 and random.randint(0, 10) >= 1:
            result[1] = result[0]
        return result

    def _display(self, amount_bet, result, time_interval=0.2):
        st.markdown("<h3 class='spin-message'>🎰 Spinning... 🎰</h3>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='slot-machine'>", unsafe_allow_html=True)
            
            reel_cols = st.columns(3)
            reel_placeholders = [col.empty() for col in reel_cols]
            
            spin_duration = 4
            iterations = int(spin_duration / time_interval)
            for _ in range(iterations):
                for i in range(3):
                    random_symbol = random.choice(list(self.SYMBOLS.keys()))
                    reel_placeholders[i].markdown(
                        f"<div class='reel'>{self.SYMBOLS[random_symbol]}</div>",
                        unsafe_allow_html=True
                    )
                sleep(time_interval)
            
            # Reveal final symbols
            for i in range(3):
                reel_placeholders[i].markdown(
                    f"<div class='reel' style='font-size:80px;'>{self.SYMBOLS[result[i]]}</div>",
                    unsafe_allow_html=True
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Win or lose message as a header
        if self._check_result_user(result):
            st.markdown(
                f"<h1 style='text-align: center; color: green;'>You won and received: R${amount_bet * 2:.2f}</h1>",
                unsafe_allow_html=True
            )
            st.balloons()
        else:
            st.markdown(
                "<h1 style='text-align: center; color: red;'>That was close! Try again next time.</h1>",
                unsafe_allow_html=True
            )

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
    if "player" not in st.session_state:
        st.session_state["player"] = None
    if "game_active" not in st.session_state:
        st.session_state["game_active"] = True
    # We'll store a flag for auto-spinning and how many remain
    if "auto_spins_active" not in st.session_state:
        st.session_state["auto_spins_active"] = False
    if "auto_spins_remaining" not in st.session_state:
        st.session_state["auto_spins_remaining"] = 0

    # STOP auto spin if the user clicks "Stop Auto Spin"
    if st.button("Stop Auto Spin", key="stop_auto"):
        st.session_state["auto_spins_active"] = False
        st.session_state["auto_spins_remaining"] = 0
        st.info("Auto spin stopped.")

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
                    st.info("Please enter a valid initial balance to start playing.")
            except ValueError:
                st.error("Please enter a valid number.")

    if st.session_state["game_active"] and st.session_state["player"] is not None:
        player = st.session_state["player"]
        if player.balance > 0:
            # Standard bet input
            bet = st.text_input(f"Enter your bet amount (Available balance: R${player.balance:.2f})", value="", key="bet_input")
            
            # Number of auto spins
            auto_spins = st.number_input("How many auto spins?", min_value=1, max_value=100, value=5, step=1, key="auto_spin_input")
            
            # Single spin button
            bet_ok = st.button("OK", key="bet_ok")
            
            # Auto spin button
            auto_spin_ok = st.button("Auto Spin", key="auto_spin_ok")

            if bet_ok:
                # Single spin
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
                            st.info("You ran out of balance. Game over!")
                            st.session_state["game_active"] = False
                except ValueError:
                    st.error("Please enter a valid numeric value.")

            elif auto_spin_ok:
                # Start auto spins
                try:
                    amount_bet = float(bet)
                    if amount_bet <= 0:
                        st.error("The bet must be greater than 0.")
                    elif amount_bet > player.balance:
                        st.error("You do not have enough balance for this bet.")
                    else:
                        st.session_state["auto_spins_active"] = True
                        st.session_state["auto_spins_remaining"] = auto_spins
                except ValueError:
                    st.error("Please enter a valid numeric value.")

            # If auto spins are active, run the spins automatically
            if st.session_state["auto_spins_active"] and st.session_state["auto_spins_remaining"] > 0:
                casino = SlotMachine()
                # Spin repeatedly up to the chosen number, or until balance is insufficient
                for i in range(int(st.session_state["auto_spins_remaining"])):
                    if player.balance < float(bet):
                        st.info("You do not have enough balance to continue auto spins.")
                        st.session_state["auto_spins_active"] = False
                        st.session_state["auto_spins_remaining"] = 0
                        break
                    # Perform one spin
                    casino.play(float(bet), player)
                    st.write(f"Spin {i+1}/{auto_spins}. Current balance: R${player.balance:.2f}")
                    sleep(1.5)  # Pause so the user can see the result before next spin
                    # If user pressed "Stop Auto Spin," break immediately
                    if not st.session_state["auto_spins_active"]:
                        break

                # Adjust any leftover spins if we didn't break
                if st.session_state["auto_spins_active"]:
                    st.session_state["auto_spins_remaining"] = 0
                    st.session_state["auto_spins_active"] = False
                    st.write(f"Auto spins complete. Final balance: R${player.balance:.2f}")

                if player.balance <= 0:
                    st.info("You ran out of balance. Game over!")
                    st.session_state["game_active"] = False

        else:
            st.info("You ran out of balance. Game over!")
            st.session_state["game_active"] = False

if __name__ == "__main__":
    configure_page()
    start_game()
