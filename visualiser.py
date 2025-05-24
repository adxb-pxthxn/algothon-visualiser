import pandas as pd
import streamlit as st
import plotly.graph_objs as go
import json
import os

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            asset_names_raw = data.get("asset_names", {})
            asset_names = {int(k): v for k, v in asset_names_raw.items()}
            return {
                "asset_names": asset_names,
                "groups": data.get("groups", {})
            }
    return {"asset_names": {}, "groups": {}}


def save_state(asset_names, groups):
    with open(STATE_FILE, "w") as f:
        json.dump({"asset_names": asset_names, "groups": groups}, f, indent=4)

def load_data(filename):
    return pd.read_csv(filename, sep="\s+", header=None)


def main():
    df = load_data("prices.txt")
    num_assets = df.shape[1]

    if "asset_names" not in st.session_state or "groups" not in st.session_state:
        saved = load_state()
        st.session_state.asset_names = saved.get("asset_names", {})
        for i in range(num_assets):
            if i not in st.session_state.asset_names:
                st.session_state.asset_names[i] = f"Asset {i + 1}"

        st.session_state.groups = saved.get("groups", {})

    # ------------------------
    # INIT STATE
    # ------------------------
    if "asset_names" not in st.session_state or "groups" not in st.session_state:
        saved = load_state()
        st.session_state.asset_names = saved.get("asset_names", {i: f"Asset {i + 1}" for i in range(num_assets)})
        st.session_state.groups = saved.get("groups", {})
    if "groups" not in st.session_state:
        st.session_state.groups = {}
    if "graph_count" not in st.session_state:
        st.session_state.graph_count = 1

    # ------------------------------
    # Asset Renaming
    # ------------------------------
    st.sidebar.header("📝 Rename Assets")

    selected_rename_index = st.sidebar.slider(
        "Select Asset to Rename",
        min_value=0,
        max_value=num_assets - 1,
        format="Asset %d"
    )

    new_name = st.sidebar.text_input(
        label=f"Rename Asset {selected_rename_index + 1}",
        value=st.session_state.asset_names[selected_rename_index],
        key=f"rename_input_{selected_rename_index}"
    )

    st.session_state.asset_names[selected_rename_index] = new_name.strip() or f"Asset {selected_rename_index + 1}"
    save_state(st.session_state.asset_names, st.session_state.groups)

    # ------------------------------
    # Group Creation
    # ------------------------------
    st.sidebar.markdown("---")
    st.sidebar.header("Manage Groups")

    new_group_name = st.sidebar.text_input("New group name")

    if st.sidebar.button("➕ Create Group"):
        if new_group_name and new_group_name not in st.session_state.groups:
            st.session_state.groups[new_group_name] = []
            save_state(st.session_state.asset_names, st.session_state.groups)
            st.sidebar.success(f"Group '{new_group_name}' created.")
        else:
            st.sidebar.warning("Enter a unique group name.")

    # ------------------------
    # Initialize flexible graph panel state
    # ------------------------
    if "graph_ids" not in st.session_state:
        st.session_state.graph_ids = [0]

    # Track the next unique graph ID
    if "next_graph_id" not in st.session_state:
        st.session_state.next_graph_id = 1

    # ------------------------
    # Graph Panels Loop
    # ------------------------
    for graph_id in st.session_state.graph_ids:
        graph_label = f"Graph {st.session_state.graph_ids.index(graph_id) + 1}"
        with st.expander(f"📈 {graph_label}", expanded=True):
            selected_names = st.multiselect(
                f"Select assets for {graph_label}",
                options=list(st.session_state.asset_names.values()),
                key=f"select_assets_{graph_id}"
            )
            selected_indices = [
                i for i, name in st.session_state.asset_names.items()
                if name in selected_names
            ]

            # Remove graph button
            if st.button(f"❌ Remove {graph_label}", key=f"remove_graph_btn_{graph_id}"):
                st.session_state.graph_ids.remove(graph_id)
                st.rerun()

            # Toggle group controls visibility
            if f"show_groups_{graph_id}" not in st.session_state:
                st.session_state[f"show_groups_{graph_id}"] = True

            toggle = st.checkbox("Show group controls", value=st.session_state[f"show_groups_{graph_id}"],
                                 key=f"group_toggle_{graph_id}")
            st.session_state[f"show_groups_{graph_id}"] = toggle

            if toggle:
                # New group creation UI
                st.markdown("### ➕ Create New Group from Selection")
                new_group_name = st.text_input(
                    f"New group name ({graph_label})",
                    key=f"new_group_name_{graph_id}"
                )
                if st.button("✅ Create Group", key=f"create_group_btn_{graph_id}"):
                    if new_group_name:
                        if new_group_name in st.session_state.groups:
                            st.warning(f"Group '{new_group_name}' already exists.")
                        else:
                            st.session_state.groups[new_group_name] = selected_indices.copy()
                            save_state(st.session_state.asset_names, st.session_state.groups)
                            st.success(f"Group '{new_group_name}' created.")
                    else:
                        st.warning("Please enter a group name.")

                # Add to existing group
                st.markdown("### 📂 Add Selected to Existing Group")
                group_options = list(st.session_state.groups.keys())
                if group_options:
                    group_to_add = st.selectbox(
                        f"Choose existing group (Graph {graph_id})",
                        options=["(None)"] + group_options,
                        key=f"group_select_{graph_id}"
                    )

                    if group_to_add != "(None)":
                        if st.button(f"➕ Add to '{group_to_add}'", key=f"add_to_group_btn_{graph_id}"):
                            for idx in selected_indices:
                                if idx not in st.session_state.groups[group_to_add]:
                                    st.session_state.groups[group_to_add].append(idx)
                            save_state(st.session_state.asset_names, st.session_state.groups)
                            st.success(f"Assets added to group '{group_to_add}'.")

            # Plotting
            if selected_indices:
                fig = go.Figure()
                for i in selected_indices:
                    fig.add_trace(go.Scatter(
                        y=df[i],
                        mode="lines",
                        name=st.session_state.asset_names[i]
                    ))
                st.plotly_chart(fig, use_container_width=True, key=f"plot_{graph_id}")
            else:
                st.info("Select assets to plot.")

    # ------------------------
    # Button: Add New Graph Panel
    # ------------------------
    if st.button("➕ Add Another Graph Panel"):
        st.session_state.graph_ids.append(st.session_state.next_graph_id)
        st.session_state.next_graph_id += 1

    # ------------------------
    # Group Preview/Plot
    # ------------------------
    st.markdown("## 📂 View a Saved Group")
    selected_group = st.selectbox("Choose a group", list(st.session_state.groups.keys()) or ["(No groups)"])
    if selected_group and selected_group != "(No groups)":
        fig = go.Figure()
        for idx in st.session_state.groups[selected_group]:
            fig.add_trace(go.Scatter(
                y=df[idx],
                mode="lines",
                name=st.session_state.asset_names[idx]
            ))
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
