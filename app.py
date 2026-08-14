import streamlit as st
import random
import requests

# --- CONFIGURATION ---
FIREBASE_URL = "https://gu-world-combat-default-rtdb.firebaseio.com/"

st.title("Gu Master Async PvP")

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

max_cap_map = {1: 2, 2: 4, 3: 6, 4: 8, 5: 10}

def get_room_data(room_id):
    try:
        res = requests.get(f"{FIREBASE_URL}/rooms/{room_id}.json")
        return res.json() if res.status_code == 200 else None
    except:
        return None

def update_room_data(room_id, data):
    try:
        requests.patch(f"{FIREBASE_URL}/rooms/{room_id}.json", json=data)
    except:
        pass

# Global Escape Hatch in Sidebar
with st.sidebar:
    st.subheader("Controls")
    if st.session_state.in_room:
        if st.button("🚪 Leave / Delete Room", type="primary"):
            if st.session_state.room_id:
                try:
                    requests.delete(f"{FIREBASE_URL}/rooms/{st.session_state.room_id}.json")
                except:
                    pass
            st.session_state.in_room = False
            st.session_state.room_id = ""
            st.session_state.player_role = ""
            st.rerun()

# --- LOBBY SCREEN ---
if not st.session_state.in_room:
    st.subheader("Multiplayer Lobby")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Create Room")
        c_room = st.text_input("New Room Code", "room123")
        c_name = st.text_input("Your Name", "Gu Master A")
        c_rank = st.slider("Your Rank", 1, 5, 3, key="c_rank")
        c_apt = st.selectbox("Aptitude", ["Extreme", "A-Grade", "B-Grade", "C-Grade", "D-Grade"], key="c_apt")
        
        c_cap = max_cap_map.get(c_rank, 2)
        st.markdown(f"**Gu Inventory (Cap: {c_cap})**")
        c_att = st.slider("Attack Gu", 0, 10, 2, key="c_att")
        c_def = st.slider("Defense Gu", 0, 10, 1, key="c_def")
        c_heal = st.slider("Healing Gu", 0, 10, 1, key="c_heal")
        c_agi = st.slider("Agility Gu", 0, 10, 2, key="c_agi")
        
        if st.button("Host Match", type="primary"):
            initial_state = {
                "p1_name": c_name,
                "p1_rank": c_rank,
                "p1_apt": c_apt,
                "p1_hp": {1: 200, 2: 400, 3: 600, 4: 800, 5: 1000}.get(c_rank, 200),
                "p1_max_hp": {1: 200, 2: 400, 3: 600, 4: 800, 5: 1000}.get(c_rank, 200),
                "p1_essence": 100.0,
                "p1_thoughts": {1: 1, 2: 2, 3: 4, 4: 5, 5: 6}.get(c_rank, 1),
                "p1_max_thoughts": {1: 1, 2: 2, 3: 4, 4: 5, 5: 6}.get(c_rank, 1),
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
            st.rerun()

    with col2:
        st.markdown("### Join Room")
        j_room = st.text_input("Enter Room Code", "room123", key="j_room")
        j_name = st.text_input("Your Name", "Gu Master B", key="j_name")
        j_rank = st.slider("Your Rank", 1, 5, 3, key="j_rank")
        j_apt = st.selectbox("Aptitude", ["Extreme", "A-Grade", "B-Grade", "C-Grade", "D-Grade"], key="j_apt")
        
        j_cap = max_cap_map.get(j_rank, 2)
        st.markdown(f"**Gu Inventory (Cap: {j_cap})**")
        j_att = st.slider("Attack Gu", 0, 10, 2, key="j_att")
        j_def = st.slider("Defense Gu", 0, 10, 1, key="j_def")
        j_heal = st.slider("Healing Gu", 0, 10, 1, key="j_heal")
        j_agi = st.slider("Agility Gu", 0, 10, 2, key="j_agi")
        
        if st.button("Join Match"):
            room_data = get_room_data(j_room)
            if room_data:
                update_data = {
                    "p2_name": j_name,
                    "p2_rank": j_rank,
                    "p2_apt": j_apt,
                    "p2_hp": {1: 200, 2: 400, 3: 600, 4: 800, 5: 1000}.get(j_rank, 200),
                    "p2_max_hp": {1: 200, 2: 400, 3: 600, 4: 800, 5: 1000}.get(j_rank, 200),
                    "p2_essence": 100.0,
                    "p2_thoughts": {1: 1, 2: 2, 3: 4, 4: 5, 5: 6}.get(j_rank, 1),
                    "p2_max_thoughts": {1: 1, 2: 2, 3: 4, 4: 5, 5: 6}.get(j_rank, 1),
                    "p2_gu": {"Attack Gu": j_att, "Defense Gu": j_def, "Healing Gu": j_heal, "Agility Gu": j_agi},
                    "p2_shield": 0,
                    "p2_actions": [],
                    "game_status": "battling"
                }
                update_room_data(j_room, update_data)
                st.session_state.room_id = j_room
                st.session_state.player_role = "p2"
                st.session_state.in_room = True
                st.rerun()
            else:
                st.error("Room not found!")

# --- BATTLE SCREEN ---
else:
    room = get_room_data(st.session_state.room_id)
    if not room:
        st.warning("Room was closed or disconnected.")
        if st.button("Return to Lobby"):
            st.session_state.in_room = False
            st.session_state.room_id = ""
            st.session_state.player_role = ""
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
        if st.button("🔄 Sync Game"):
            st.rerun()
    
    col_p, col_ai = st.columns(2)
    with col_p:
        st.markdown(f"### {room.get(f'{my_prefix}_name', 'You')} (You)")
        st.write(f"**HP:** {room.get(f'{my_prefix}_hp', 0)}/{room.get(f'{my_prefix}_max_hp', 100)}")
        st.write(f"**Essence:** {room.get(f'{my_prefix}_essence', 0):.1f}% | **Thoughts:** {room.get(f'{my_prefix}_thoughts', 0)}")
        if room.get(f'{my_prefix}_shield', 0) > 0:
            st.info(f"Shield: {room.get(f'{my_prefix}_shield')}")
            
    with col_ai:
        st.markdown(f"### {room.get(f'{opp_prefix}_name', 'Opponent')} (Opponent)")
        st.write(f"**HP:** {room.get(f'{opp_prefix}_hp', 0)}/{room.get(f'{opp_prefix}_max_hp', 100)}")
        st.write(f"**Essence:** {room.get(f'{opp_prefix}_essence', 0):.1f}% | **Thoughts:** {room.get(f'{opp_prefix}_thoughts', 0)}")
        if room.get(f'{opp_prefix}_shield', 0) > 0:
            st.info(f"Shield: {room.get(f'{opp_prefix}_shield')}")

    st.markdown("---")

    my_actions = room.get(f"{my_prefix}_actions", [])
    opp_actions = room.get(f"{opp_prefix}_actions", [])

    if len(my_actions) > 0 and len(opp_actions) == 0:
        st.info("Turn submitted! Waiting for opponent to lock in their actions...")
        if st.button("🔄 Refresh Status"):
            st.rerun()
    elif len(my_actions) == 0 and room.get(f'{my_prefix}_thoughts', 0) > 0 and room.get(f'{my_prefix}_hp', 0) > 0:
        st.subheader("Action Queueing")
        
        # Display currently queued actions for this turn
        if my_actions:
            st.markdown(f"**Queued Actions:** {', '.join(my_actions)}")
            if st.button("↩️ Reset/Undo Queued Actions"):
                # Refund stats based on actions queued (simplified full reset)
                room = get_room_data(st.session_state.room_id)
                # Recalculate or restore base values before queueing
                # For simplicity, we trigger a soft reset of thoughts/essence for the turn or just let them re-sync
                st.rerun()

        action_choice = st.selectbox("Choose Action to Queue:", [
            ('Attack Gu (10% Essence, 1 Thought, 20 DMG/rank)', 'attack'),
            ('Active Defense Gu (15% Essence, 1 Thought, 30 Shield/rank)', 'defense'),
            ('Healing Gu (15% Essence, 1 Thought, 20 HP/rank)', 'heal'),
            ('Agility Gu (5% Essence, 1 Thought, Speed Priority)', 'agility'),
        ], format_func=lambda x: x[0])
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if st.button("Queue Action"):
                choice_key = action_choice[1]
                cost_map = {'attack': 10.0, 'defense': 15.0, 'heal': 15.0, 'agility': 5.0}
                if room[f'{my_prefix}_essence'] < cost_map[choice_key]:
                    st.warning("Not enough essence!")
                else:
                    room[f'{my_prefix}_thoughts'] -= 1
                    room[f'{my_prefix}_essence'] -= cost_map[choice_key]
                    my_actions.append(choice_key)
                    update_room_data(st.session_state.room_id, {
                        f"{my_prefix}_thoughts": room[f'{my_prefix}_thoughts'],
                        f"{my_prefix}_essence": room[f'{my_prefix}_essence'],
                        f"{my_prefix}_actions": my_actions
                    })
                    st.rerun()
        with col_q2:
            if st.button("Clear Turn & Refund", type="secondary"):
                # Pull fresh room data to refund accurately
                fresh_room = get_room_data(st.session_state.room_id)
                rank = fresh_room[f'{my_prefix}_rank']
                max_t = fresh_room[f'{my_prefix}_max_thoughts']
                fresh_room[f'{my_prefix}_thoughts'] = max_t
                fresh_room[f'{my_prefix}_essence'] = min(100.0, fresh_room[f'{my_prefix}_essence'] + (len(my_actions) * 10.0))
                fresh_room[f'{my_prefix}_actions'] = []
                update_room_data(st.session_state.room_id, fresh_room)
                st.rerun()

        if st.button("Submit Turn (Lock In)", type="primary"):
            update_room_data(st.session_state.room_id, {f"{my_prefix}_actions": my_actions})
            st.rerun()

    # If both submitted, process turn
    room = get_room_data(st.session_state.room_id) # ensure latest
    if len(room.get("p1_actions", [])) > 0 and len(room.get("p2_actions", [])) > 0:
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
                    total_heal += min(20 * rank, max_hp - room[f"{actor_pref}_hp"])
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

        first, second = ("p1", "p2") if random.choice([True, False]) else ("p2", "p1")
        f_summary = resolve_turn(first, second)
        s_summary = resolve_turn(second, first)
        
        f_name = room[f"{first}_name"]
        s_name = room[f"{second}_name"]
        log_entry = f"Turn {room['turn']}: {f_name} went first [{f_summary}]. Then {s_name} went [{s_summary}]."
        
        room["log"].insert(1, log_entry)
        room["turn"] += 1
        
        for p in ["p1", "p2"]:
            apt = room[f"{p}_apt"]
            regen_rate = 25.0 if apt == "Extreme" else 12.0
            room[f"{p}_essence"] = min(100.0, room[f"{p}_essence"] + regen_rate)
            rank = room[f"{p}_rank"]
            thought_regen = {1: 1, 2: 2, 3: 2, 4: 2, 5: 3}.get(rank, 1)
            max_t = room[f"{p}_max_thoughts"]
            room[f"{p}_thoughts"] = min(max_t, room[f"{p}_thoughts"] + thought_regen)
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
            try:
                requests.delete(f"{FIREBASE_URL}/rooms/{st.session_state.room_id}.json")
            except:
                pass
            st.session_state.in_room = False
            st.session_state.room_id = ""
            st.session_state.player_role = ""
            st.rerun()