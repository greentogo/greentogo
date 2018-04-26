import React from "react";
import G2GTitleImage from "./G2GTitleImage";
import { Constants } from 'expo';
import axios from '../apiClient';

import {
    Text,
    TextInput,
    View,
    StyleSheet,
    TouchableHighlight
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

import { observer } from "mobx-react";

import styles from "../styles";

class LoginScreen extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            username: null,
            password: null,
            passwordConfirmation: null,
            error: [],
            loading: false,
            type: 'login'
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
        }).then((json) => {
            if (json.data.auth_token) {
                this.setState({ loading: false });
                this.props.store.setAuthToken(json.data.auth_token);
            }

            // Get the user data after successful login
            axios.get('/me/', {
                headers: {
                    'Authorization': `Token ${json.data.auth_token}`
                }
            }).then((response) => {
                console.log(response.data)
                this.props.store.setUserData(response.data.data);
            }).catch((err) => {
                console.log(err)
            })
        }).catch((error) => {
            console.log(JSON.stringify(error.response.data.non_field_errors[0]))
            this.setState({ error: error.response.data.non_field_errors, loading: false });
            // console.log("State error: " + this.state.error)
        });
    }

    attemptSignUp() {
        this.setState({ error: [], loading: true });

        // axios({
        //     method: 'post',
        //     url: this.props.store.makeUrl('/auth/signup/'),
        //     headers: {
        //         'Accept': 'application/json',
        //         'Content-Type': 'application/json',
        //     },
        //     data: {
        //         username: this.state.username,
        //         password: this.state.password,
        //         passwordConfirmation: this.state.passwordConfirmation
        //     }
        // }).then((json) => {
        //     console.log(json.data.auth_token);
        //     if (json.data.auth_token) {
        //         this.setState({ loading: false });
        //         return this.props.store.setAuthToken(json.data.auth_token);
        //     }
        // }).catch((error) => {
        //     console.log(JSON.stringify(error.response.data.non_field_errors[0]))
        //     this.setState({ error: error.response.data.non_field_errors, loading: false });
        //     // console.log("State error: " + this.state.error)
        // });
    }

    attemptPasswordReset() {
        this.setState({ type: 'passwordResetSuccess' })
        // axios({
        //     method: 'post',
        //     url: this.props.store.makeUrl('/auth/passwordReset/'),
        //     headers: {
        //         'Accept': 'application/json',
        //         'Content-Type': 'application/json',
        //     },
        //     data: {
        //         username: this.state.username
        //     }
        // }).then((json) => {
        //     console.log(json.data.auth_token);
        //     if (json.data.auth_token) {
        //         this.setState({ loading: false });
        //         return this.props.store.setAuthToken(json.data.auth_token);
        //     }
        // }).catch((error) => {
        //     console.log(JSON.stringify(error.response.data.non_field_errors[0]))
        //     this.setState({ error: error.response.data.non_field_errors, loading: false });
        //     // console.log("State error: " + this.state.error)
        // });
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
                    {this.state.type === 'login' ?
                        // Login form
                        <Form>
                            <Item>
                                <Input placeholder="Username or Email"
                                    autoCapitalize="none"
                                    autoCorrect={false}
                                    keyboardType="email-address"
                                    onChangeText={(text) => this.setState({ username: text })}
                                    value={this.state.username}
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
                                <Text style={{ fontWeight: 'bold', color: styles.primaryColor }}>Login</Text>
                            </Button>
                            <Button style={{ backgroundColor: styles.primaryCream }} light full title="SignUp" onPress={() => { this.setState({ type: "signUp" }) }}>
                                <Text style={{ fontWeight: 'bold', color: styles.primaryColor }}>Sign Up!</Text>
                            </Button>
                            <Button style={{ backgroundColor: styles.primaryCream }} light full title="passwordReset" onPress={() => { this.setState({ type: 'passwordReset' }) }}>
                                <Text style={{ color: styles.primaryColor }}>Forgot Password?</Text>
                            </Button>
                        </Form>
                        : this.state.type === 'signUp' ?
                            // Sign up form below
                            <Form>
                                <Item>
                                    <Input placeholder="Email"
                                        autoCapitalize="none"
                                        autoCorrect={false}
                                        keyboardType="email-address"
                                        onChangeText={(text) => this.setState({ username: text })}
                                    />
                                </Item>
                                <Item>
                                    <Input placeholder="Password"
                                        secureTextEntry={true}
                                        onSubmitEditing={() => this.attemptSignUp()}
                                        onChangeText={(text) => this.setState({ password: text })}
                                    />
                                </Item>
                                <Item last>
                                    <Input placeholder="Confirm Password"
                                        secureTextEntry={true}
                                        onSubmitEditing={() => this.attemptSignUp()}
                                        onChangeText={(text) => this.setState({ passwordConfirmation: text })}
                                        value={this.state.passwordConfirmation}
                                    />
                                </Item>
                                <Button style={{ backgroundColor: styles.primaryCream }} light full title="Login" onPress={() => { this.attemptLogin }}>
                                    <Text style={{ fontWeight: 'bold', color: styles.primaryColor }}>Sign Up</Text>
                                </Button>
                                <Button style={{ backgroundColor: styles.primaryCream }} light full title="SignUp" onPress={() => { this.setState({ type: "login" }) }}>
                                    <Text style={{ fontWeight: 'bold', color: styles.primaryColor }}>Go to Login</Text>
                                </Button>
                            </Form>
                            : this.state.type === 'passwordResetSuccess' ?
                                <View style={{ flex: 1, paddingTop: 140, alignItems: 'center' }}>
                                    <Text style={{ color: styles.primaryColor }}>The password was successfully reset</Text>
                                    <Button style={{ backgroundColor: styles.primaryCream }} light full title="SignUp" onPress={() => { this.setState({ type: "login" }) }}>
                                        <Text style={{ fontWeight: 'bold', color: styles.primaryColor }}>Go to Login</Text>
                                    </Button>
                                </View>

                                // Password reset form
                                : <Form>
                                    <Item>
                                        <Input placeholder="Email"
                                            autoCapitalize="none"
                                            autoCorrect={false}
                                            keyboardType="email-address"
                                            onChangeText={(text) => this.setState({ username: text })}
                                        />
                                    </Item>
                                    <Button style={{ backgroundColor: styles.primaryCream }} light full title="resetPassword" onPress={() => { this.attemptPasswordReset() }}>
                                        <Text style={{ fontWeight: 'bold', color: styles.primaryColor }}>Reset Password</Text>
                                    </Button>
                                    <Button style={{ backgroundColor: styles.primaryCream }} light full title="SignUp" onPress={() => { this.setState({ type: "login" }) }}>
                                        <Text style={{ fontWeight: 'bold', color: styles.primaryColor }}>Go to Login</Text>
                                    </Button>
                                </Form>
                    }
                    {errorMessages}
                    {loadingSpinner}
                </Content>
            </Container>
        )
    }
}

export default LoginScreen;
