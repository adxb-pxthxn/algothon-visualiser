import pandas as pd
import streamlit as st
import plotly.graph_objs as go

def load_data(filename):
    return pd.read_csv(filename, sep="\s+", header=None)

def main():
    st.title("SIG Algothon 2025 - Price Visualizer")

    df = load_data("prices.txt")
    num_assets = df.shape[1]

    if "asset_names" not in st.session_state:
        st.session_state.asset_names = {i: f"Asset {i+1}" for i in range(num_assets)}

    st.sidebar.header("💡 Rename Assets")
    for i in range(num_assets):
        new_name = st.sidebar.text_input(
            label=f"Name for Asset {i + 1}",
            value=st.session_state.asset_names[i],
            key=f"name_input_{i}"
        )
        st.session_state.asset_names[i] = new_name.strip() or f"Asset {i+1}"

    selected_names = st.multiselect(
        "Select Assets to Visualize",
        options=list(st.session_state.asset_names.values()),
        default=[list(st.session_state.asset_names.values())[0]]
    )

    selected_indices = [
        i for i, name in st.session_state.asset_names.items()
        if name in selected_names
    ]

    if selected_indices:
        fig = go.Figure()
        for i in selected_indices:
            fig.add_trace(go.Scatter(
                y=df[i],
                mode="lines",
                name=st.session_state.asset_names[i]
            ))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least one asset to display.")

if __name__ == "__main__":
    main()
