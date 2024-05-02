import streamlit as st
from streamlit import write
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

st.set_page_config(page_title="Home Page!!", page_icon=":house:")

def main():
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)


    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
    )

    st.session_state['authenticator'] = authenticator

    if not st.session_state.get("authentication_status"):
        option = st.sidebar.radio("Choose an option:", ("Login", "Sign Up"))
        if option == "Login":
            name, authentication_status, username = authenticator.login()
            st.session_state["authentication_status"] = authentication_status
        elif option == "Sign Up":
            try:
                email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)
                if email_of_registered_user:
                    st.success('User registered successfully')
                with open('./config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
            except Exception as e:
                st.error(e)
                
    # def logout_button():
    #     if st.sidebar.button("Logout"):
    #     authenticator.logout()

    if st.session_state["authentication_status"]:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')

        image = st.image('logo.jpeg', width=100)  # Adjust width as needed
        st.write("# Admin Dashboard")
        st.markdown("**Track key metrics and analyze app performance.**")

    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')

    # elif st.session_state["authentication_status"] is None:
    #     st.warning('Please enter your username and password')

    # disconnecting the databases
    # disconnect_mongodb(mongo_client)
    # disconnect_postgres(post_client)

if __name__ == '__main__':
    main()