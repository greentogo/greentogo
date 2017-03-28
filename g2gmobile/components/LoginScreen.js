import React from "react";
import {Text, TextInput, View, StyleSheet} from "react-native";
import {
    Container,
    Header,
    Body,
    Title,
    Content,
    Form,
    Item,
    Input,
    Button,
} from "native-base";

import { connect } from 'react-redux';

import { saveAuthToken } from "../actions";
import stylesheet from "../styles";

class LoginScreen extends React.Component {
    static route = {
        navigationBar: {
            title: 'Login',
        }
    }

    constructor(props) {
        super(props)
        this.state = {
            username: null,
            password: null
        }
    }

    attemptLogin() {
        this.props.login(
            fetch('https://greentogo.ngrok.io/auth/login/', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: this.state.username,
                    password: this.state.password,
                })
            })
                .then((response) => response.json())
        )
    }

    render() {
        // Button component does not accept styles correctly
        const fullWidthButton = StyleSheet.flatten([stylesheet.fullWidthButton]);

        return (
            <Container>
                <Header>
                    <Body>
                    <Title>Login</Title>
                    </Body>
                </Header>
                <Content>
                    <Form>
                        <Item>
                            <Input placeholder="Username"
                                   autoCapitalize="none"
                                   autoCorrect={false}
                                   onChangeText={(text) => this.setState({ username: text })}
                            />
                        </Item>
                        <Item last>
                            <Input placeholder="Password"
                                   secureTextEntry={true}
                                   onChangeText={(text) => this.setState({ password: text })}
                            />
                        </Item>
                        <View style={stylesheet.buttonContainer}>
                            <Button light style={fullWidthButton}
                                    onPress={() => this.attemptLogin()}>
                                <Text style={stylesheet.boldText}>Login</Text>
                            </Button>
                        </View>
                    </Form>
                </Content>
            </Container>
        )
    }
}

const mapStateToProps = (state) => {
    return {}
}

const mapDispatchToProps = (dispatch) => {
    return {
        login: (promise) => {
            dispatch(saveAuthToken(promise))
        }
    }
}

const LoginContainer = connect(mapStateToProps, mapDispatchToProps)(LoginScreen);

export default LoginContainer;
