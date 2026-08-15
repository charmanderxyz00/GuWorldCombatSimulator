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

max_cap_map = {1: 2, 2: 4, 3: 6, 4: 8, 5: 10}
rank_max_thoughts = {1: 1, 2: 2, 3: 4, 4: 5, 5: 6}
rank_max_hp = {1: 200, 2: 400, 3: 600, 4: 800, 5: 1000}

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
        
        c_cap = max_cap_map.get(c_rank, 2)
        st.markdown(f"**Gu Inventory (Cap: {c_cap})**")
        c_att = st.slider("Attack Gu", 0, c_cap, min(2, c_cap), key="c_att")
        c_def = st.slider("Defense Gu", 0, c_cap, min(1, c_cap), key="c_def")
        c_heal = st.slider("Healing Gu", 0, c_cap, min(1, c_cap), key="c_heal")
        c_agi = st.slider("Agility Gu", 0, c_cap, min(1, c_cap), key="c_agi")
        
        if (c_att + c_def + c_heal + c_agi) > c_cap:
            st.warning(f"Total Gu ({c_att + c_def + c_heal + c_agi}) exceeds Rank {c_rank} cap of {c_cap}!")
        
        if st.button("Host Match", type="primary"):
            if (c_att + c_def + c_heal + c_agi) > c_cap:
                st.error("Cannot host: Gu count exceeds your rank limit!")
            else:
                initial_state = {
                    "p1_name": c_name,
                    "p1_rank": c_rank,
                    "p1_apt": c_apt,
                    "p1_hp": rank_max_hp.get(c_rank, 200),
                    "p1_max_hp": rank_max_hp.get(c_rank, 200),
                    "p1_essence": 100.0,
                    "p1_thoughts": rank_max_thoughts.get(c_rank, 1),
                    "p1_max_thoughts": rank_max_thoughts.get(c_rank, 1),
                    "p1_gu": {"Attack Gu": c_att, "Defense Gu": c_def, "Healing Gu": c_heal, "Agility Gu": c_agi},
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
        
        j_cap = max_cap_map.get(j_rank, 2)
        st.markdown(f"**Gu Inventory (Cap: {j_cap})**")
        j_att = st.slider("Attack Gu", 0, j_cap, min(2, j_cap), key="j_att")
        j_def = st.slider("Defense Gu", 0, j_cap, min(1, j_cap), key="j_def")
        j_heal = st.slider("Healing Gu", 0, j_cap, min(1, j_cap), key="j_heal")
        j_agi = st.slider("Agility Gu", 0, j_cap, min(1, j_cap), key="j_agi")
        
        if (j_att + j_def + j_heal + j_agi) > j_cap:
            st.warning(f"Total Gu ({j_att + j_def + j_heal + j_agi}) exceeds Rank {j_rank} cap of {j_cap}!")
        
        if st.button("Join Match"):
            if (j_att + j_def + j_heal + j_agi) > j_cap:
                st.error("Cannot join: Gu count exceeds your rank limit!")
            else:
                room_data = get_room_data(j_room)
                if room_data:
                    update_data = {
                        "p2_name": j_name,
                        "p2_rank": j_rank,
                        "p2_apt": j_apt,
                        "p2_hp": rank_max_hp.get(j_rank, 200),
                        "p2_max_hp": rank_max_hp.get(j_rank, 200),
                        "p2_essence": 100.0,
                        "p2_thoughts": rank_max_thoughts.get(j_rank, 1),
                        "p2_max_thoughts": rank_max_thoughts.get(j_rank, 1),
                        "p2_gu": {"Attack Gu": j_att, "Defense Gu": j_def, "Healing Gu": j_heal, "Agility Gu": j_agi},
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
        
        b_cap = max_cap_map.get(b_rank, 2)
        st.markdown(f"**Gu Inventory (Cap: {b_cap})**")
        b_att = st.slider("Attack Gu", 0, b_cap, min(2, b_cap), key="b_att")
        b_def = st.slider("Defense Gu", 0, b_cap, min(1, b_cap), key="b_def")
        b_heal = st.slider("Healing Gu", 0, b_cap, min(1, b_cap), key="b_heal")
        b_agi = st.slider("Agility Gu", 0, b_cap, min(1, b_cap), key="b_agi")
        
        if (b_att + b_def + b_heal + b_agi) > b_cap:
            st.warning(f"Total Gu ({b_att + b_def + b_heal + b_agi}) exceeds Rank {b_rank} cap of {b_cap}!")
        
        if st.button("Battle AI Bot", type="primary"):
            if (b_att + b_def + b_heal + b_agi) > b_cap:
                st.error("Cannot start: Gu count exceeds your rank limit!")
            else:
                bot_rank = b_rank
                bot_cap = max_cap_map.get(bot_rank, 2)
                st.session_state.bot_room_data = {
                    "p1_name": b_name,
                    "p1_rank": b_rank,
                    "p1_apt": b_apt,
                    "p1_hp": rank_max_hp.get(b_rank, 200),
                    "p1_max_hp": rank_max_hp.get(b_rank, 200),
                    "p1_essence": 100.0,
                    "p1_thoughts": rank_max_thoughts.get(b_rank, 1),
                    "p1_max_thoughts": rank_max_thoughts.get(b_rank, 1),
                    "p1_gu": {"Attack Gu": b_att, "Defense Gu": b_def, "Healing Gu": b_heal, "Agility Gu": b_agi},
                    "p1_shield": 0,
                    "p1_actions": [],
                    "p2_name": "Shadow Sect AI",
                    "p2_rank": bot_rank,
                    "p2_apt": "A-Grade",
                    "p2_hp": rank_max_hp.get(bot_rank, 200),
                    "p2_max_hp": rank_max_hp.get(bot_rank, 200),
                    "p2_essence": 100.0,
                    "p2_thoughts": rank_max_thoughts.get(bot_rank, 1),
                    "p2_max_thoughts": rank_max_thoughts.get(bot_rank, 1),
                    "p2_gu": {"Attack Gu": bot_cap // 2, "Defense Gu": bot_cap - (bot_cap // 2), "Healing Gu": 0, "Agility Gu": 0},
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
        st.write(f"**HP:** {room.get(f'{my_prefix}_hp', 0)}/{room.get(f'{my_prefix}_max_hp', 100)}")
        current_avail_essence = room.get(f'{my_prefix}_essence', 0) - st.session_state.staged_essence_cost
        current_avail_thoughts = room.get(f'{my_prefix}_thoughts', 0) - st.session_state.staged_thoughts_used
        st.write(f"**Essence:** {current_avail_essence:.1f}% | **Thoughts:** {current_avail_thoughts}")
        if room.get(f'{my_prefix}_shield', 0) > 0:
            st.info(f"Shield: {room.get(f'{my_prefix}_shield')}")
            
    with col_ai:
        st.markdown(f"### {room.get(f'{opp_prefix}_name', 'Opponent')} (Opponent)")
        st.write(f"**HP:** {room.get(f'{opp_prefix}_hp', 0)}/{room.get(f'{opp_prefix}_max_hp', 100)}")
        st.write(f"**Essence:** {room.get(f'{opp_prefix}_essence', 0):.1f}% | **Thoughts:** {room.get(f'{opp_prefix}_thoughts', 0)}")
        if room.get(f'{opp_prefix}_shield', 0) > 0:
            st.info(f"Shield: {room.get(f'{opp_prefix}_shield')}")

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
            ('Attack Gu (10.0% Essence, 1 Thought, 20 DMG/rank)', 'attack'),
            ('Active Defense Gu (15.0% Essence, 1 Thought, 30 Shield/rank)', 'defense'),
            ('Healing Gu (7.5% Essence, 1 Thought, 10 HP/rank)', 'heal'),
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
        def resolve_turn(actor_pref, target_pref):
            actor_actions = room.get(f"{actor_pref}_actions", [])
            total_shield = 0
            total_heal = 0
            raw_damage = 0
            total_absorbed = 0
            net_damage = 0
            
            for action in actor_actions:
                if room[f"{actor_pref}_hp"] <= 0 or room[f"{target_pref}_hp"] <= 0:
                    break
                rank = room[f"{actor_pref}_rank"]
                if action == 'defense':
                    total_shield += 30 * rank
                elif action == 'heal':
                    max_hp = room[f"{actor_pref}_max_hp"]
                    total_heal += min(10 * rank, max_hp - room[f"{actor_pref}_hp"])
                elif action == 'attack':
                    raw_damage += 20 * rank

            if total_shield > 0:
                room[f"{actor_pref}_shield"] += total_shield
            if total_heal > 0:
                room[f"{actor_pref}_hp"] = min(room[f"{actor_pref}_max_hp"], room[f"{actor_pref}_hp"] + total_heal)

            if raw_damage > 0:
                target_shield = room[f"{target_pref}_shield"]
                if target_shield > 0:
                    total_absorbed = min(target_shield, raw_damage)
                    room[f"{target_pref}_shield"] -= total_absorbed
                    net_damage = raw_damage - total_absorbed
                    if net_damage > 0:
                        room[f"{target_pref}_hp"] -= net_damage
                else:
                    net_damage = raw_damage
                    room[f"{target_pref}_hp"] -= net_damage

            parts = []
            if total_shield > 0:
                parts.append(f"+{total_shield} Shield")
            if total_heal > 0:
                parts.append(f"+{total_heal} HP")
            if raw_damage > 0:
                parts.append(f"Dealt {net_damage} DMG")
            return ", ".join(parts) if parts else "Passed"

        p1_actions = room.get("p1_actions", [])
        p2_actions = room.get("p2_actions", [])
        p1_agi_count = p1_actions.count('agility')
        p2_agi_count = p2_actions.count('agility')
        
        p1_score = p1_agi_count * room["p1_rank"]
        p2_score = p2_agi_count * room["p2_rank"]
        
        if p1_score > p2_score:
            first, second = "p1", "p2"
        elif p2_score > p1_score:
            first, second = "p2", "p1"
        else:
            first, second = ("p1", "p2") if random.choice([True, False]) else ("p2", "p1")

        f_summary = resolve_turn(first, second)
        s_summary = resolve_turn(second, first)
        
        f_name = room[f"{first}_name"]
        s_name = room[f"{second}_name"]
        log_entry = f"Turn {room['turn']}: {f_name} went first [{f_summary}]. Then {s_name} went [{s_summary}]."
        
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
            regen_rate = aptitude_recovery_map.get(apt, 12.0)
            room[f"{p}_essence"] = min(100.0, room[f"{p}_essence"] + regen_rate)
            rank = room[f"{p}_rank"]
            thought_regen = rank_max_thoughts.get(rank, 1)
            max_t = room[f"{p}_max_thoughts"]
            room[f"{p}_thoughts"] = min(max_t, room[f"{p}_thoughts"] + thought_regen)
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