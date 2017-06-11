import React from 'react';
import {
    StyleSheet,
    Text,
    View,
} from 'react-native';

import {observer} from "mobx-react";

import {
    createRouter,
    NavigationProvider,
    StackNavigation,
} from '@expo/ex-navigation';

import LoginScreen from "./LoginScreen";
import styles from "../styles";

const Router = createRouter(() => ({
    home: () => HomeScreen,
}));

@observer class App extends React.Component {
    render() {
        const store = this.props.store;

        if (!store.authToken) {
            return <LoginScreen store={store} />;
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
        return (
            <View style={styles.container}>
                <Text>Open up main.js to start working on your app!</Text>
            </View>
        )
    }
}

export default App;
