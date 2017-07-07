import React from 'react';
import {
    StyleSheet,
    Text,
    View,
} from 'react-native';

import {observer, Provider} from 'mobx-react';

import {
    createRouter,
    NavigationProvider,
    StackNavigation,
} from '@expo/ex-navigation';

import LoginScreen from './LoginScreen';
import HomeScreen from './HomeScreen';
import MapScreen from './MapScreen';
import CheckOutScreen from './CheckOutScreen';
import styles from '../styles';
import ReturnBox from "./ReturnScreen";
import SubmissionScreen from "./SubmissionScreen";
import stylesheet from "../styles";

const Router = createRouter(() => ({
    home: () => HomeScreen,
    map: () => MapScreen,
    checkOutBox: () => CheckOutScreen,
    returnBox: () => ReturnBox,
    submission: () => SubmissionScreen
}));

@observer
class App extends React.Component {
    render() {
        const store = this.props.store;

        if (!store.authToken) {
            return <LoginScreen store={store} />;
        } else {
            return (
                <Provider appStore={store}>
                    <NavigationProvider router={Router}>
                        <StackNavigation initialRoute={Router.getRoute('home')} />
                    </NavigationProvider>
                </Provider>
            );
        }
    }
}

export default App;
