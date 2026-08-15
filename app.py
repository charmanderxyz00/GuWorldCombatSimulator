import streamlit as st
import random
import requests

# --- CONFIGURATION ---
FIREBASE_URL = "https://gu-world-combat-default-rtdb.firebaseio.com/"

st.title("Gu Master Async PvP & Bot Battle")

if FIREBASE_URL == "YOUR_FIREBASE_URL_HERE":
    st.error("Please set your Firebase Realtime Database URL in the code to enable PvP rooms!")
    st.stop()

# Session State Initialization
if 'room_id' not in st.session_state:
    st.session_state.room_id = ""
if 'player_role' not in st.session_state:
    st.session_state.player_role = "" 
if 'in_room' not in st.session_state:
    st.session_state.in_room = False
if 'is_bot_match' not in st.session_state:
    st.session_state.is_bot_match = False
if 'staged_actions' not in st.session_state:
    st.session_state.staged_actions = []
if 'staged_essence_cost' not in st.session_state:
    st.session_state.staged_essence_cost = 0.0
if 'staged_thoughts_used' not in st.session_state:
    st.session_state.staged_thoughts_used = 0

rank_max_single = {1: 20, 2: 40, 3: 60, 4: 80, 5: 100}
rank_total_pool = {1: 50, 2: 100, 3: 150, 4: 200, 5: 250}
max_cap_map = {1: 2, 2: 4, 3: 6, 4: 8, 5: 10}

def get_room_data(room_id):
    if st.session_state.is_bot_match:
        return st.session_state.bot_room_data
    try:
        res = requests.get(f"{FIREBASE_URL}/rooms/{room_id}.json")
        return res.json() if res.status_code == 200 else None
    except:
        return None

def update_room_data(room_id, data):
    if st.session_state.is_bot_match:
        st.session_state.bot_room_data.update(data)
        return
    try:
        requests.patch(f"{FIREBASE_URL}/rooms/{room_id}.json", json=data)
    except:
        pass

# Global Escape Hatch in Sidebar
with st.sidebar:
    st.subheader("Controls")
    if st.session_state.in_room:
        if st.button("🚪 Leave / Delete Room", type="primary"):
            if not st.session_state.is_bot_match and st.session_state.room_id:
                try:
                    requests.delete(f"{FIREBASE_URL}/rooms/{st.session_state.room_id}.json")
                except:
                    pass
            st.session_state.in_room = False
            st.session_state.is_bot_match = False
            st.session_state.room_id = ""
            st.session_state.player_role = ""
            st.session_state.staged_actions = []
            st.session_state.staged_essence_cost = 0.0
            st.session_state.staged_thoughts_used = 0
            st.rerun()

# --- LOBBY SCREEN ---
if not st.session_state.in_room:
    st.subheader("Multiplayer & Bot Lobby")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Create Room")
        c_room = st.text_input("New Room Code", "room123")
        c_name = st.text_input("Your Name", "Gu Master A")
        c_rank = st.slider("Your Rank", 1, 5, 3, key="c_rank")
        c_apt = st.selectbox("Aptitude", ["Ten Extreme", "A-Grade", "B-Grade", "C-Grade", "D-Grade"], key="c_apt")
        
        c_max_stat = rank_max_single.get(c_rank, 20)
        c_max_pool = rank_total_pool.get(c_rank, 50)
        st.markdown(f"**Stat Allocation (Max Pool: {c_max_pool}, Max Single: {c_max_stat})**")
        c_pwr = st.slider("PWR (Power)", 0, c_max_stat, 10, key="c_pwr")
        c_agi = st.slider("AGI (Agility)", 0, c_max_stat, 10, key="c_agi")
        c_int = st.slider("INT (Wisdom)", 0, c_max_stat, 10, key="c_int")
        c_def = st.slider("DEF (Defense)", 0, c_max_stat, 10, key="c_def")
        
        c_total_stats = c_pwr + c_agi + c_int + c_def
        if c_total_stats > c_max_pool:
            st.warning(f"Total Stats ({c_total_stats}) exceeds Rank {c_rank} pool limit of {c_max_pool}!")

        c_cap = max_cap_map.get(c_rank, 2)
        st.markdown(f"**Gu Inventory (Cap: {c_cap})**")
        c_att = st.slider("Attack Gu", 0, c_cap, min(2, c_cap), key="c_att")
        c_def_gu = st.slider("Defense Gu", 0, c_cap, min(1, c_cap), key="c_def_gu")
        c_heal = st.slider("Healing Gu", 0, c_cap, min(1, c_cap), key="c_heal")
        c_agi_gu = st.slider("Agility Gu", 0, c_cap, min(1, c_cap), key="c_agi_gu")
        
        if (c_att + c_def_gu + c_heal + c_agi_gu) > c_cap:
            st.warning(f"Total Gu ({c_att + c_def_gu + c_heal + c_agi_gu}) exceeds Rank {c_rank} cap of {c_cap}!")
        
        if st.button("Host Match", type="primary"):
            if c_total_stats > c_max_pool:
                st.error("Cannot host: Stat allocation exceeds rank pool limit!")
            elif (c_att + c_def_gu + c_heal + c_agi_gu) > c_cap:
                st.error("Cannot host: Gu count exceeds your rank limit!")
            else:
                max_hp = c_def * 10.0
                max_thoughts = 1 + (c_int // 20)
                initial_state = {
                    "p1_name": c_name,
                    "p1_rank": c_rank,
                    "p1_apt": c_apt,
                    "p1_pwr": c_pwr,
                    "p1_agi": c_agi,
                    "p1_int": c_int,
                    "p1_def": c_def,
                    "p1_hp": max_hp,
                    "p1_max_hp": max_hp,
                    "p1_essence": 100.0,
                    "p1_thoughts": max_thoughts,
                    "p1_max_thoughts": max_thoughts,
                    "p1_gu": {"Attack Gu": c_att, "Defense Gu": c_def_gu, "Healing Gu": c_heal, "Agility Gu": c_agi_gu},
                    "p1_shield": 0,
                    "p1_actions": [],
                    "p2_name": "",
                    "turn": 1,
                    "game_status": "waiting",
                    "log": ["=== BATTLE COMMENCES ==="]
                }
                requests.put(f"{FIREBASE_URL}/rooms/{c_room}.json", json=initial_state)
                st.session_state.room_id = c_room
                st.session_state.player_role = "p1"
                st.session_state.in_room = True
                st.session_state.is_bot_match = False
                st.session_state.staged_actions = []
                st.session_state.staged_essence_cost = 0.0
                st.session_state.staged_thoughts_used = 0
                st.rerun()

    with col2:
        st.markdown("### Join Room")
        j_room = st.text_input("Enter Room Code", "room123", key="j_room")
        j_name = st.text_input("Your Name", "Gu Master B", key="j_name")
        j_rank = st.slider("Your Rank", 1, 5, 3, key="j_rank")
        j_apt = st.selectbox("Aptitude", ["Ten Extreme", "A-Grade", "B-Grade", "C-Grade", "D-Grade"], key="j_apt")
        
        j_max_stat = rank_max_single.get(j_rank, 20)
        j_max_pool = rank_total_pool.get(j_rank, 50)
        st.markdown(f"**Stat Allocation (Max Pool: {j_max_pool}, Max Single: {j_max_stat})**")
        j_pwr = st.slider("PWR (Power)", 0, j_max_stat, 10, key="j_pwr")
        j_agi = st.slider("AGI (Agility)", 0, j_max_stat, 10, key="j_agi")
        j_int = st.slider("INT (Wisdom)", 0, j_max_stat, 10, key="j_int")
        j_def = st.slider("DEF (Defense)", 0, j_max_stat, 10, key="j_def")
        
        j_total_stats = j_pwr + j_agi + j_int + j_def
        if j_total_stats > j_max_pool:
            st.warning(f"Total Stats ({j_total_stats}) exceeds Rank {j_rank} pool limit of {j_max_pool}!")

        j_cap = max_cap_map.get(j_rank, 2)
        st.markdown(f"**Gu Inventory (Cap: {j_cap})**")
        j_att = st.slider("Attack Gu", 0, j_cap, min(2, j_cap), key="j_att")
        j_def_gu = st.slider("Defense Gu", 0, j_cap, min(1, j_cap), key="j_def_gu")
        j_heal = st.slider("Healing Gu", 0, j_cap, min(1, j_cap), key="j_heal")
        j_agi_gu = st.slider("Agility Gu", 0, j_cap, min(1, j_cap), key="j_agi_gu")
        
        if (j_att + j_def_gu + j_heal + j_agi_gu) > j_cap:
            st.warning(f"Total Gu ({j_att + j_def_gu + j_heal + j_agi_gu}) exceeds Rank {j_rank} cap of {j_cap}!")
        
        if st.button("Join Match"):
            if j_total_stats > j_max_pool:
                st.error("Cannot join: Stat allocation exceeds rank pool limit!")
            elif (j_att + j_def_gu + j_heal + j_agi_gu) > j_cap:
                st.error("Cannot join: Gu count exceeds your rank limit!")
            else:
                room_data = get_room_data(j_room)
                if room_data:
                    max_hp = j_def * 10.0
                    max_thoughts = 1 + (j_int // 20)
                    update_data = {
                        "p2_name": j_name,
                        "p2_rank": j_rank,
                        "p2_apt": j_apt,
                        "p2_pwr": j_pwr,
                        "p2_agi": j_agi,
                        "p2_int": j_int,
                        "p2_def": j_def,
                        "p2_hp": max_hp,
                        "p2_max_hp": max_hp,
                        "p2_essence": 100.0,
                        "p2_thoughts": max_thoughts,
                        "p2_max_thoughts": max_thoughts,
                        "p2_gu": {"Attack Gu": j_att, "Defense Gu": j_def_gu, "Healing Gu": j_heal, "Agility Gu": j_agi_gu},
                        "p2_shield": 0,
                        "p2_actions": [],
                        "game_status": "battling"
                    }
                    update_room_data(j_room, update_data)
                    st.session_state.room_id = j_room
                    st.session_state.player_role = "p2"
                    st.session_state.in_room = True
                    st.session_state.is_bot_match = False
                    st.session_state.staged_actions = []
                    st.session_state.staged_essence_cost = 0.0
                    st.session_state.staged_thoughts_used = 0
                    st.rerun()
                else:
                    st.error("Room not found!")

    with col3:
        st.markdown("### Fight Bot")
        b_name = st.text_input("Your Name", "Gu Master", key="b_name")
        b_rank = st.slider("Your Rank", 1, 5, 3, key="b_rank")
        b_apt = st.selectbox("Aptitude", ["Ten Extreme", "A-Grade", "B-Grade", "C-Grade", "D-Grade"], key="b_apt")
        
        b_max_stat = rank_max_single.get(b_rank, 20)
        b_max_pool = rank_total_pool.get(b_rank, 50)
        st.markdown(f"**Your Stat Allocation (Max Pool: {b_max_pool}, Max Single: {b_max_stat})**")
        b_pwr = st.slider("PWR (Power)", 0, b_max_stat, 10, key="b_pwr")
        b_agi = st.slider("AGI (Agility)", 0, b_max_stat, 10, key="b_agi")
        b_int = st.slider("INT (Wisdom)", 0, b_max_stat, 10, key="b_int")
        b_def = st.slider("DEF (Defense)", 0, b_max_stat, 10, key="b_def")
        
        b_total_stats = b_pwr + b_agi + b_int + b_def
        if b_total_stats > b_max_pool:
            st.warning(f"Total Stats ({b_total_stats}) exceeds Rank {b_rank} pool limit of {b_max_pool}!")

        b_cap = max_cap_map.get(b_rank, 2)
        st.markdown(f"**Your Gu Inventory (Cap: {b_cap})**")
        b_att = st.slider("Attack Gu", 0, b_cap, min(2, b_cap), key="b_att")
        b_def_gu = st.slider("Defense Gu", 0, b_cap, min(1, b_cap), key="b_def_gu")
        b_heal = st.slider("Healing Gu", 0, b_cap, min(1, b_cap), key="b_heal")
        b_agi_gu = st.slider("Agility Gu", 0, b_cap, min(1, b_cap), key="b_agi_gu")
        
        if (b_att + b_def_gu + b_heal + b_agi_gu) > b_cap:
            st.warning(f"Total Gu ({b_att + b_def_gu + b_heal + b_agi_gu}) exceeds Rank {b_rank} cap of {b_cap}!")

        st.markdown("---")
        st.markdown("### Bot Configuration")
        bot_name = st.text_input("Bot Name", "Shadow Sect AI", key="bot_name")
        bot_rank = st.slider("Bot Rank", 1, 5, 3, key="bot_rank")
        bot_max_stat = rank_max_single.get(bot_rank, 20)
        bot_max_pool = rank_total_pool.get(bot_rank, 50)
        
        st.markdown(f"**Bot Stat Allocation (Max Pool: {bot_max_pool}, Max Single: {bot_max_stat})**")
        bot_pwr = st.slider("Bot PWR (Power)", 0, bot_max_stat, 10, key="bot_pwr")
        bot_agi = st.slider("Bot AGI (Agility)", 0, bot_max_stat, 10, key="bot_agi")
        bot_int = st.slider("Bot INT (Wisdom)", 0, bot_max_stat, 10, key="bot_int")
        bot_def = st.slider("Bot DEF (Defense)", 0, bot_max_stat, 10, key="bot_def")
        
        bot_total_stats = bot_pwr + bot_agi + bot_int + bot_def
        if bot_total_stats > bot_max_pool:
            st.warning(f"Bot Total Stats ({bot_total_stats}) exceeds Rank {bot_rank} pool limit of {bot_max_pool}!")

        bot_cap = max_cap_map.get(bot_rank, 2)
        st.markdown(f"**Bot Gu Inventory (Cap: {bot_cap})**")
        bot_att = st.slider("Bot Attack Gu", 0, bot_cap, min(2, bot_cap), key="bot_att")
        bot_def_gu_b = st.slider("Bot Defense Gu", 0, bot_cap, min(1, bot_cap), key="bot_def_gu_b")
        bot_heal_b = st.slider("Bot Healing Gu", 0, bot_cap, 0, key="bot_heal_b")
        bot_agi_gu_b = st.slider("Bot Agility Gu", 0, bot_cap, 0, key="bot_agi_gu_b")

        if (bot_att + bot_def_gu_b + bot_heal_b + bot_agi_gu_b) > bot_cap:
            st.warning(f"Bot Total Gu ({bot_att + bot_def_gu_b + bot_heal_b + bot_agi_gu_b}) exceeds Bot Rank limit of {bot_cap}!")
        
        if st.button("Battle AI Bot", type="primary"):
            if b_total_stats > b_max_pool:
                st.error("Cannot start: Your stat allocation exceeds rank pool limit!")
            elif (b_att + b_def_gu + b_heal + b_agi_gu) > b_cap:
                st.error("Cannot start: Your Gu count exceeds your rank limit!")
            elif bot_total_stats > bot_max_pool:
                st.error("Cannot start: Bot stat allocation exceeds rank pool limit!")
            elif (bot_att + bot_def_gu_b + bot_heal_b + bot_agi_gu_b) > bot_cap:
                st.error("Cannot start: Bot Gu count exceeds bot rank limit!")
            else:
                p1_max_hp = b_def * 10.0
                p1_max_thoughts = 1 + (b_int // 20)
                
                bot_max_hp = bot_def * 10.0
                bot_max_thoughts = 1 + (bot_int // 20)

                st.session_state.bot_room_data = {
                    "p1_name": b_name,
                    "p1_rank": b_rank,
                    "p1_apt": b_apt,
                    "p1_pwr": b_pwr,
                    "p1_agi": b_agi,
                    "p1_int": b_int,
                    "p1_def": b_def,
                    "p1_hp": p1_max_hp,
                    "p1_max_hp": p1_max_hp,
                    "p1_essence": 100.0,
                    "p1_thoughts": p1_max_thoughts,
                    "p1_max_thoughts": p1_max_thoughts,
                    "p1_gu": {"Attack Gu": b_att, "Defense Gu": b_def_gu, "Healing Gu": b_heal, "Agility Gu": b_agi_gu},
                    "p1_shield": 0,
                    "p1_actions": [],
                    "p2_name": bot_name,
                    "p2_rank": bot_rank,
                    "p2_apt": "A-Grade",
                    "p2_pwr": bot_pwr,
                    "p2_agi": bot_agi,
                    "p2_int": bot_int,
                    "p2_def": bot_def,
                    "p2_hp": bot_max_hp,
                    "p2_max_hp": bot_max_hp,
                    "p2_essence": 100.0,
                    "p2_thoughts": bot_max_thoughts,
                    "p2_max_thoughts": bot_max_thoughts,
                    "p2_gu": {"Attack Gu": bot_att, "Defense Gu": bot_def_gu_b, "Healing Gu": bot_heal_b, "Agility Gu": bot_agi_gu_b},
                    "p2_shield": 0,
                    "p2_actions": [],
                    "turn": 1,
                    "game_status": "battling",
                    "log": ["=== BATTLE COMMENCES VS AI ==="]
                }
                st.session_state.room_id = "bot_room"
                st.session_state.player_role = "p1"
                st.session_state.in_room = True
                st.session_state.is_bot_match = True
                st.session_state.staged_actions = []
                st.session_state.staged_essence_cost = 0.0
                st.session_state.staged_thoughts_used = 0
                st.rerun()

# --- BATTLE SCREEN ---
else:
    room = get_room_data(st.session_state.room_id)
    if not room:
        st.warning("Room was closed or disconnected.")
        if st.button("Return to Lobby"):
            st.session_state.in_room = False
            st.session_state.is_bot_match = False
            st.session_state.room_id = ""
            st.session_state.player_role = ""
            st.session_state.staged_actions = []
            st.rerun()
        st.stop()

    is_p1 = st.session_state.player_role == "p1"
    my_prefix = "p1" if is_p1 else "p2"
    opp_prefix = "p2" if is_p1 else "p1"

    if room["game_status"] == "waiting":
        st.info(f"Room: {st.session_state.room_id} | Waiting for opponent to join...")
        if st.button("🔄 Check for Opponent"):
            st.rerun()
        st.stop()

    # Top Bar with Sync Button
    c_head1, c_head2 = st.columns([3, 1])
    with c_head1:
        st.subheader(f"Room: {st.session_state.room_id} | Turn {room['turn']}")
    with c_head2:
        if not st.session_state.is_bot_match and st.button("🔄 Sync Game"):
            st.rerun()
    
    col_p, col_ai = st.columns(2)
    with col_p:
        st.markdown(f"### {room.get(f'{my_prefix}_name', 'You')} (You)")
        st.write(f"**HP:** {room.get(f'{my_prefix}_hp', 0):.1f}/{room.get(f'{my_prefix}_max_hp', 100)}")
        current_avail_essence = room.get(f'{my_prefix}_essence', 0) - st.session_state.staged_essence_cost
        current_avail_thoughts = room.get(f'{my_prefix}_thoughts', 0) - st.session_state.staged_thoughts_used
        st.write(f"**Essence:** {current_avail_essence:.1f}% | **Thoughts:** {current_avail_thoughts}")
        if room.get(f'{my_prefix}_shield', 0) > 0:
            st.info(f"Shield: {room.get(f'{my_prefix}_shield'):.1f}")
            
    with col_ai:
        st.markdown(f"### {room.get(f'{opp_prefix}_name', 'Opponent')} (Opponent)")
        st.write(f"**HP:** {room.get(f'{opp_prefix}_hp', 0):.1f}/{room.get(f'{opp_prefix}_max_hp', 100)}")
        st.write(f"**Essence:** {room.get(f'{opp_prefix}_essence', 0):.1f}% | **Thoughts:** {room.get(f'{opp_prefix}_thoughts', 0)}")
        if room.get(f'{opp_prefix}_shield', 0) > 0:
            st.info(f"Shield: {room.get(f'{opp_prefix}_shield'):.1f}")

    st.markdown("---")

    my_submitted_actions = room.get(f"{my_prefix}_actions", [])
    opp_submitted_actions = room.get(f"{opp_prefix}_actions", [])

    if st.session_state.is_bot_match and len(my_submitted_actions) == 0 and room.get(f'{my_prefix}_hp', 0) > 0:
        # Generate bot actions automatically if fighting AI
        bot_thoughts = room.get(f"{opp_prefix}_thoughts", 1)
        bot_essence = room.get(f"{opp_prefix}_essence", 100.0)
        bot_gu = room.get(f"{opp_prefix}_gu", {})
        bot_actions = []
        cost_map = {'attack': 10.0, 'defense': 15.0, 'heal': 7.5, 'agility': 5.0}
        
        available_moves = []
        if bot_gu.get('Attack Gu', 0) > 0: available_moves.append('attack')
        if bot_gu.get('Defense Gu', 0) > 0: available_moves.append('defense')
        if bot_gu.get('Healing Gu', 0) > 0 and room.get(f"{opp_prefix}_hp", 100) < room.get(f"{opp_prefix}_max_hp", 100): available_moves.append('heal')
        if not available_moves: available_moves = ['attack']

        while bot_thoughts > 0:
            move = random.choice(available_moves)
            cost = cost_map[move]
            if bot_essence >= cost:
                bot_actions.append(move)
                bot_essence -= cost
                bot_thoughts -= 1
            else:
                break
        if not bot_actions:
            bot_actions = ['attack']
        room[f"{opp_prefix}_actions"] = bot_actions
        room[f"{opp_prefix}_essence"] = bot_essence
        room[f"{opp_prefix}_thoughts"] = 0

    if len(my_submitted_actions) > 0 and len(opp_submitted_actions) == 0:
        st.info("Turn submitted! Waiting for opponent to lock in their actions...")
        if st.button("🔄 Refresh Status"):
            st.rerun()
    elif len(my_submitted_actions) == 0 and room.get(f'{my_prefix}_hp', 0) > 0:
        st.subheader("Action Queueing")
        
        if st.session_state.staged_actions:
            st.markdown(f"**Staged Actions (Not Locked In Yet):** {', '.join(st.session_state.staged_actions)}")

        action_choice = st.selectbox("Choose Action to Queue:", [
            ('Attack Gu (10.0% Essence, 1 Thought, Physical Strike)', 'attack'),
            ('Active Defense Gu (15.0% Essence, 1 Thought, Scales with DEF)', 'defense'),
            ('Healing Gu (7.5% Essence, 1 Thought, Heals HP)', 'heal'),
            ('Agility Gu (5.0% Essence, 1 Thought, Speed Priority)', 'agility'),
        ], format_func=lambda x: x[0])
        
        cost_map = {'attack': 10.0, 'defense': 15.0, 'heal': 7.5, 'agility': 5.0}
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if st.button("Queue Action"):
                choice_key = action_choice[1]
                choice_cost = cost_map[choice_key]
                avail_e = room.get(f'{my_prefix}_essence', 0) - st.session_state.staged_essence_cost
                avail_t = room.get(f'{my_prefix}_thoughts', 0) - st.session_state.staged_thoughts_used
                
                gu_inventory = room.get(f'{my_prefix}_gu', {})
                action_gu_name_map = {
                    'attack': 'Attack Gu',
                    'defense': 'Defense Gu',
                    'heal': 'Healing Gu',
                    'agility': 'Agility Gu'
                }
                gu_type_name = action_gu_name_map.get(choice_key)
                max_gu_available = gu_inventory.get(gu_type_name, 0)
                current_staged_count = st.session_state.staged_actions.count(choice_key)

                if avail_t <= 0:
                    st.warning("No thoughts remaining to queue another action!")
                elif avail_e < choice_cost:
                    st.warning("Not enough remaining essence!")
                elif current_staged_count >= max_gu_available:
                    st.warning(f"You only own {max_gu_available} {gu_type_name}(s) in your inventory!")
                else:
                    st.session_state.staged_thoughts_used += 1
                    st.session_state.staged_essence_cost += choice_cost
                    st.session_state.staged_actions.append(choice_key)
                    st.rerun()
                    
        with col_q2:
            if st.button("Clear Staged Actions", type="secondary"):
                st.session_state.staged_actions = []
                st.session_state.staged_essence_cost = 0.0
                st.session_state.staged_thoughts_used = 0
                st.rerun()

        if st.button("Submit Turn (Lock In)", type="primary"):
            if not st.session_state.staged_actions:
                st.warning("You must queue at least one action before submitting!")
            else:
                new_thoughts = room.get(f'{my_prefix}_thoughts', 0) - st.session_state.staged_thoughts_used
                new_essence = room.get(f'{my_prefix}_essence', 0) - st.session_state.staged_essence_cost
                
                update_room_data(st.session_state.room_id, {
                    f"{my_prefix}_thoughts": new_thoughts,
                    f"{my_prefix}_essence": new_essence,
                    f"{my_prefix}_actions": st.session_state.staged_actions
                })
                st.session_state.staged_actions = []
                st.session_state.staged_essence_cost = 0.0
                st.session_state.staged_thoughts_used = 0
                st.rerun()

    # If both submitted, process turn
    room = get_room_data(st.session_state.room_id)
    if room and len(room.get("p1_actions", [])) > 0 and len(room.get("p2_actions", [])) > 0:
        
        # Calculate speeds and initiative ordering for each action item
        p1_actions = room.get("p1_actions", [])
        p2_actions = room.get("p2_actions", [])
        
        p1_agi_stat = room.get("p1_agi", 0)
        p2_agi_stat = room.get("p2_agi", 0)
        
        # Build action queue tuples: (speed_value, actor_prefix, action_type, original_index)
        all_action_queue = []
        for idx, act in enumerate(p1_actions):
            act_speed = p1_agi_stat + (5 if act == 'agility' else 0)
            all_action_queue.append({
                'actor': 'p1',
                'target': 'p2',
                'action': act,
                'speed': act_speed,
                'index': idx
            })
            
        for idx, act in enumerate(p2_actions):
            act_speed = p2_agi_stat + (5 if act == 'agility' else 0)
            all_action_queue.append({
                'actor': 'p2',
                'target': 'p1',
                'action': act,
                'speed': act_speed,
                'index': idx
            })
            
        # Sort by speed descending; tie-break randomly
        all_action_queue.sort(key=lambda x: (x['speed'], random.random()), reverse=True)
        
        # Track summary logs per player
        p1_summaries = []
        p2_summaries = []
        
        for item in all_action_queue:
            actor = item['actor']
            target = item['target']
            action = item['action']
            
            if room[f"{actor}_hp"] <= 0 or room[f"{target}_hp"] <= 0:
                continue
                
            rank = room[f"{actor}_rank"]
            pwr = room.get(f"{actor}_pwr", 0)
            agi = room.get(f"{actor}_agi", 0)
            target_agi = room.get(f"{target}_agi", 0)
            def_stat = room.get(f"{actor}_def", 0)
            
            if action == 'defense':
                base_shield = 30.0 * rank
                shield_val = base_shield + (def_stat * 1.5) * (1.0 + (def_stat * 0.01))
                room[f"{actor}_shield"] += shield_val
                msg = f"+{shield_val:.1f} Shield"
                if actor == 'p1': p1_summaries.append(msg)
                else: p2_summaries.append(msg)
                
            elif action == 'heal':
                max_hp = room[f"{actor}_max_hp"]
                heal_val = min(10.0 * rank, max_hp - room[f"{actor}_hp"])
                room[f"{actor}_hp"] = min(max_hp, room[f"{actor}_hp"] + heal_val)
                msg = f"+{heal_val:.1f} HP"
                if actor == 'p1': p1_summaries.append(msg)
                else: p2_summaries.append(msg)
                
            elif action == 'agility':
                msg = f"Agility Priority"
                if actor == 'p1': p1_summaries.append(msg)
                else: p2_summaries.append(msg)
                
            elif action == 'attack':
                evasion_chance = min(50.0, target_agi)
                hit_chance = max(50.0, 85.0 + agi - evasion_chance)
                
                if random.uniform(0, 100) > hit_chance:
                    msg = "Attack Missed!"
                    if actor == 'p1': p1_summaries.append(msg)
                    else: p2_summaries.append(msg)
                else:
                    base_dmg = (20.0 * rank) + pwr
                    dmg_mult = 1.0 + (pwr * 0.01)
                    final_raw_dmg = base_dmg * dmg_mult
                    
                    crit_chance = 10.0
                    is_crit = random.uniform(0, 100) < crit_chance
                    if is_crit:
                        crit_dmg_mult = 1.5 + (pwr * 0.01)
                        final_raw_dmg *= crit_dmg_mult
                        
                    target_shield = room[f"{target}_shield"]
                    net_dmg = 0
                    if target_shield > 0:
                        absorbed = min(target_shield, final_raw_dmg)
                        room[f"{target}_shield"] -= absorbed
                        net_dmg = final_raw_dmg - absorbed
                        if net_dmg > 0:
                            room[f"{target}_hp"] -= net_dmg
                    else:
                        net_dmg = final_raw_dmg
                        room[f"{target}_hp"] -= net_dmg
                        
                    crit_str = " (CRIT!)" if is_crit else ""
                    msg = f"Dealt {net_dmg:.1f} DMG{crit_str}"
                    if actor == 'p1': p1_summaries.append(msg)
                    else: p2_summaries.append(msg)

        f_name = room["p1_name"]
        s_name = room["p2_name"]
        p1_sum_str = ", ".join(p1_summaries) if p1_summaries else "Passed"
        p2_sum_str = ", ".join(p2_summaries) if p2_summaries else "Passed"
        
        log_entry = f"Turn {room['turn']}: {f_name} [{p1_sum_str}] | {s_name} [{p2_sum_str}]"
        
        room["log"].insert(1, log_entry)
        room["turn"] += 1
        
        aptitude_recovery_map = {
            "Ten Extreme": 25.0,
            "A-Grade": 12.0,
            "B-Grade": 8.0,
            "C-Grade": 5.0,
            "D-Grade": 3.0
        }

        for p in ["p1", "p2"]:
            apt = room[f"{p}_apt"]
            int_stat = room.get(f"{p}_int", 0)
            base_regen = aptitude_recovery_map.get(apt, 12.0)
            essence_regen = base_regen * (1.0 + (int_stat * 0.01))
            room[f"{p}_essence"] = min(100.0, room[f"{p}_essence"] + essence_regen)
            
            rank = room[f"{p}_rank"]
            base_thought_regen = rank_max_thoughts.get(rank, 1) if 'rank_max_thoughts' in globals() else 1
            bonus_thought_regen = int_stat // 50
            total_thought_regen = base_thought_regen + bonus_thought_regen
            
            max_t = room[f"{p}_max_thoughts"]
            room[f"{p}_thoughts"] = min(max_t, room[f"{p}_thoughts"] + total_thought_regen)
            room[f"{p}_shield"] = 0
            room[f"{p}_actions"] = []

        update_room_data(st.session_state.room_id, room)
        st.rerun()

    st.markdown("### Battle Log")
    for entry in room.get("log", []):
        st.text(entry)

    if room.get("p1_hp", 0) <= 0 or room.get("p2_hp", 0) <= 0:
        st.subheader("=== BATTLE OVER ===")
        if room.get(f"{my_prefix}_hp", 0) <= 0:
            st.error("Defeat!")
        else:
            st.success("Victory!")
        if st.button("Reset Room"):
            if not st.session_state.is_bot_match:
                try:
                    requests.delete(f"{FIREBASE_URL}/rooms/{st.session_state.room_id}.json")
                except:
                    pass
            st.session_state.in_room = False
            st.session_state.is_bot_match = False
            st.session_state.room_id = ""
            st.session_state.player_role = ""
            st.session_state.staged_actions = []
            st.rerun()