import React from 'react';
import {
    StyleSheet,
    Text,
    View,
} from 'react-native';

import {observer} from 'mobx-react';

import {
    createRouter,
    NavigationProvider,
    StackNavigation,
} from '@expo/ex-navigation';

import LoginScreen from './LoginScreen';
import HomeScreen from './HomeScreen';
import MapScreen from './MapScreen';
import styles from '../styles';

const Router = createRouter(() => ({
    home: () => HomeScreen,
    map: () => MapScreen
}));

@observer
class App extends React.Component {
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

export default App;
