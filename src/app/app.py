# the main application file
import streamlit as st

def main():
    """Interface principale."""
    st.set_page_config(
        page_title="Analyse des logs",
        layout="wide",
    )

    # hello world
    st.write("Hello, world!")


if __name__ == "__main__":
    main()
