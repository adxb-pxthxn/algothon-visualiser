import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


def load_data(filename):
    return pd.read_csv(filename, sep="\s+", header=None)

def main():
    st.title("SIG Algothon Price Visualizer")

    df = load_data("prices.txt")

    st.write("Shape of dataset:", df.shape)

    asset_index = st.slider("Select Asset Index", 0, df.shape[1] - 1, 0)

    st.line_chart(df[asset_index])

if __name__ == "__main__":
    main()
