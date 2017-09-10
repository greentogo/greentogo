import React from "react";
import G2GTitleImage from "./G2GTitleImage";
import { Constants } from 'expo';
import axios from '../apiClient';
import { Button } from "native-base";
import { observer } from "mobx-react";
import styles from "../styles";
import {
    Text,
    TextInput,
    View,
    StyleSheet,
    TouchableHighlight
} from "react-native";

class LoginScreen extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            username: null,
            password: null,
            error: [],
            loading: false,
        }
    }

    attemptLogin() {
        this.setState({ error: [], loading: true });

        axios({
            method: 'post',
            url: this.props.store.makeUrl('/auth/login/'),
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            data: {
                username: this.state.username,
                password: this.state.password
            }
        })
            .then((json) => {
                console.log(json.data.auth_token);
                if (json.data.auth_token) {
                    this.setState({ loading: false });
                    return this.props.store.setAuthToken(json.data.auth_token);
                }
            })
            .catch((error) => {
                console.log(JSON.stringify(error.response.data.non_field_errors[0]))
                this.setState({ error: error.response.data.non_field_errors, loading: false });
                // console.log("State error: " + this.state.error)
            });

    }

    render() {
        let loadingSpinner = this.state.loading ?
            <Spinner color={styles.primaryColor} />
            : null;
        let errorMessages = this.state.error.map((error, index) => {
            return <Text key={index} style={{ color: 'red', textAlign: 'center' }}>{error}</Text>;
        });
        return (
            <Container style={styles.container}>
                <Header style={{ backgroundColor: styles.primaryColor, marginTop: Constants.statusBarHeight }}>
                    <G2GTitleImage />
                </Header>
                <Content style={{ alignContent: 'center' }}>
                    <Form>
                        <Item>
                            <Input placeholder="Email"
                                autoCapitalize="none"
                                autoCorrect={false}
                                onChangeText={(text) => this.setState({ username: text })}
                            />
                        </Item>
                        <Item last>
                            <Input placeholder="Password"
                                secureTextEntry={true}
                                onSubmitEditing={() => this.attemptLogin()}
                                onChangeText={(text) => this.setState({ password: text })}
                            />
                        </Item>
                        <Button style={{ backgroundColor: styles.primaryCream }} light full title="Login" onPress={() => { this.attemptLogin() }}>
                            <Text style={styles.boldText}>Login</Text>
                        </Button>
                    </Form>
                    {errorMessages}
                    {loadingSpinner}
                </Content>
            </Container>
        )
    }
}

export default LoginScreen;
