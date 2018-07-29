import React from "react";
import G2GTitleImage from "./G2GTitleImage";
import { Constants } from 'expo';
import axios from '../apiClient';
import { WebView, Linking } from 'react-native';

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
            type: 'login',
            redirectToWeb: false
        }
    }

    componentDidUpdate(prevProps, prevState) {
        if (this.state.type !== 'login') {
            if (this.state.type === 'signUp') {
                this.setState({ redirectToWeb: 'https://app.durhamgreentogo.com/accounts/register/', type: 'login' })
            } else if (this.state.type === 'passwordReset') {
                this.setState({ redirectToWeb: 'https://app.durhamgreentogo.com/accounts/password/reset/', type: 'login' })
            }
        }
    }

    attemptLogin() {
        if (this.state.username && this.state.password) {
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
                    console.log(err);
                    this.props.appStore.clearAuthToken();
                })
            }).catch((error) => {
                // TODO
                // HANDLE THESE LOCALLY
                if (error.response.data.non_field_errors) {
                    this.setState({ error: error.response.data.non_field_errors, loading: false });
                } else if (error.response.data.password || error.response.data.username) {
                    let tempErrors = [];
                    if (error.response.data.username && error.response.data.username[0] === "This field may not be null.") {
                        tempErrors.push("Username cannot be empty.");
                    }
                    if (error.response.data.password && error.response.data.password[0] === "This field may not be null.") {
                        tempErrors.push("Password cannot be empty.");
                    }
                    this.setState({ error: tempErrors, loading: false });
                } else {
                    let tempErrors = ["We are sorry, we are having trouble processing your request. Please try again later."];
                    this.setState({ error: tempErrors, loading: false });
                }
            });
        } else {
            let tempErrors = [];
            if (!this.state.username) {
                tempErrors.push("Username cannot be empty.");
            }
            if (!this.state.password) {
                tempErrors.push("Password cannot be empty.");
            }
            this.setState({ error: tempErrors, loading: false });
        }
    }

    attemptSignUp() {
        // this.setState({ error: [], loading: true });

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
        // this.setState({ type: 'passwordResetSuccess' })
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
        if (this.state.redirectToWeb) {
            let uri = this.state.redirectToWeb;
            return (
                <WebView
                    ref={(ref) => { this.webview = ref; }}
                    source={{ uri }}
                    onNavigationStateChange={(event) => {
                        this.setState({ redirectToWeb: false })
                        Linking.openURL(event.url);
                        this.webview.stopLoading();
                    }}
                />
            );
        } else {
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
                                {this.state.error.username ? <Text style={styles.errorStyle}>{this.state.error.username}</Text> : <Text></Text>}
                                <Item last>
                                    <Input placeholder="Password"
                                        secureTextEntry={true}
                                        onSubmitEditing={() => this.attemptLogin()}
                                        onChangeText={(text) => this.setState({ password: text })}
                                    />
                                </Item>
                                {errorMessages}
                                {loadingSpinner}
                                {this.state.error.password ? <Text style={styles.errorStyle}>{this.state.error.password}</Text> : <Text></Text>}
                                <Button style={{ backgroundColor: styles.primaryCream }} light full title="Login" onPress={() => { this.attemptLogin() }}>
                                    <Text style={styles.boldCenteredText}>Login</Text>
                                </Button>
                                <Button style={{ backgroundColor: styles.primaryCream }} light full title="SignUp" onPress={() => { this.setState({ type: "signUp" }) }}>
                                    <Text style={styles.boldCenteredText}>Sign Up!</Text>
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
                                    {errorMessages}
                                    {loadingSpinner}
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
                                        {errorMessages}
                                        {loadingSpinner}
                                        <Button style={{ backgroundColor: styles.primaryCream }} light full title="resetPassword" onPress={() => { this.attemptPasswordReset() }}>
                                            <Text style={{ fontWeight: 'bold', color: styles.primaryColor }}>Reset Password</Text>
                                        </Button>
                                        <Button style={{ backgroundColor: styles.primaryCream }} light full title="SignUp" onPress={() => { this.setState({ type: "login" }) }}>
                                            <Text style={{ fontWeight: 'bold', color: styles.primaryColor }}>Go to Login</Text>
                                        </Button>
                                    </Form>
                        }
                    </Content>
                </Container>
            )
        }
    }
}

export default LoginScreen;
