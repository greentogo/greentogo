import React from "react";

import {
    Text,
    TextInput,
    View,
    StyleSheet,
} from "react-native";

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
    Spinner,
} from "native-base";

import {inject, observer} from "mobx-react";

import styles from "../styles";

@inject("appStore")
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
            password: null,
            error: null,
            loading: false,
        }
    }

    attemptLogin() {
        this.setState({error: null, loading: true});

        return fetch(this.props.appStore.makeUrl('/auth/login/'), {
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
        .then((json) => {
            if (json.auth_token) {
                this.setState({loading: false});
                return this.props.store.setAuthToken(json.auth_token);
            }
        })
        .catch((error) => {
            this.setState({error: error, loading: false});
        });
    }

    render() {
        var loadingSpinner = this.state.loading ?
            <Spinner color={styles.primaryColor} />
            : null;

        return (
            <Container style={styles.container}>
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
                        <Button light full title="Login" onPress={() => {this.attemptLogin()}}>
                            <Text style={styles.boldText}>Login</Text>
                        </Button>
                    </Form>
                    {loadingSpinner}
                </Content>
            </Container>
        )
    }
}

export default LoginScreen;
