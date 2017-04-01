import React from 'react';
import {
    StyleSheet,
    Text,
    View,
} from 'react-native';

import {
    createRouter,
    NavigationProvider,
    StackNavigation,
} from '@expo/ex-navigation';

import LoginScreen from "./LoginScreen";

const Router = createRouter(() => ({
    home: () => HomeScreen,
}));

class App extends React.Component {
    render() {
        if (true) {
            return <LoginScreen store={this.props.store} />;
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

export default App;
