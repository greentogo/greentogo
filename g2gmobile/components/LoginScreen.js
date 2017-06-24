import React from "react";
import {
    Text,
    TextInput,
    View,
    StyleSheet,
    Alert,
} from "react-native";
import {
    Header,
    Body,
    Title,
    Content,
    Form,
    Item,
    Input,
    Button,
} from "native-base";

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
        this.props.store.attemptLogin(this.state.username, this.state.password);
    }

    render() {
        return (
            <View style={stylesheet.container}>
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
                            <Button light style={stylesheet.fullWidthButton} title="Login" onPress={() => {this.attemptLogin()}}>
                                <Text style={stylesheet.boldText}>Login</Text>
                            </Button>
                        </View>
                    </Form>
                </Content>
            </View>
        )
    }
}

export default LoginScreen;
