import React from 'react';
import {
    StyleSheet,
    Text,
    TextInput,
    View,
} from 'react-native';

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
    Row,
} from 'native-base';

import Expo from 'expo';

import {
    createRouter,
    NavigationProvider,
    StackNavigation,
} from '@expo/ex-navigation';

const Router = createRouter(() => ({
    home: () => HomeScreen,
}));

class App extends React.Component {
    render() {
        if (true) {
            return <LoginScreen />;
        } else {
            return (
                <NavigationProvider router={Router}>
                    <StackNavigation initialRoute={Router.getRoute('home')} />
                </NavigationProvider>
            );
        }
    }
}

class HomeScreen extends React.Component {
    static route = {
        navigationBar: {
            title: 'Home',
        }
    }

    render() {
        if (true) {
            return <LoginScreen />;
        } else {
            return (
                <View style={styles.container}>
                    <Text>Open up main.js to start working on your app!</Text>
                </View>
            )
        }
    }
}

class LoginScreen extends React.Component {
    static route = {
        navigationBar: {
            title: 'Login',
        }
    }
    
    render() {
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
                            />
                        </Item>
                        <Item last>
                            <Input placeholder="Password"
                                   secureTextEntry={true} />
                        </Item>
                        <View style={stylesheet.buttonContainer}>
                            <Button light style={styles.fullWidthButton}>
                                <Text style={stylesheet.boldText}>Login</Text>
                            </Button>
                        </View>
                    </Form>
                </Content>
            </Container>
        )
    }
}

const styles = {
    buttonContainer: {
        padding: 10,
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
    },
    container: {
        flex: 1,
        backgroundColor: '#fff',
        alignItems: 'center',
        justifyContent: 'center',
    },
    fullWidthButton: {
        width: '100%',
        justifyContent: 'center',
        flex: 1,
    },
    boldText: {
        fontWeight: 'bold'
    },
    bigText: {
        fontSize: 30
    }
}

const stylesheet = StyleSheet.create(styles);

Expo.registerRootComponent(App);
