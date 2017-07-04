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
} from "native-base";

import styles from "../styles";

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
        this.props.store.attemptLogin(this.state.username, this.state.password);
    }

    render() {
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
                </Content>
            </Container>
        )
    }
}

export default LoginScreen;
