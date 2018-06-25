import React from 'react';
import { Constants } from 'expo';
import {observer, Provider} from 'mobx-react';
import {
    StyleSheet,
    Text,
    View,
} from 'react-native';
import styles from '../styles';
import LoginScreen from './LoginScreen';
import HomeScreen from './HomeScreen';
import MapScreen from './MapScreen';
import ScanQRCode from './ScanQRCode';
import SubmissionScreen from "./SubmissionScreen";
import ContainerSuccessScreen from "./ContainerSuccessScreen";
import AccountScreen from "./AccountScreen";
import SubscriptionScreen from "./SubscriptionScreen"

import stylesheet from "../styles";
import {
    createRouter,
    NavigationProvider,
    StackNavigation
} from '@expo/ex-navigation';

const Router = createRouter(() => ({
    home: () => HomeScreen,
    map: () => MapScreen,
    scanQRCode: () => ScanQRCode,
    submission: () => SubmissionScreen,
    containerSuccessScreen: () => ContainerSuccessScreen,
    account: () => AccountScreen,
    subscription: () => SubscriptionScreen
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
                        <StackNavigation 
                            defaultRouteConfig={{
                                navigationBar: {
                                    backgroundColor: styles.primaryColor,
                                    tintColor: styles.primaryCream,
                                    borderTopWidth: Constants.statusBarHeight
                                }
                            }}
                            initialRoute={Router.getRoute('home')} />
                    </NavigationProvider>
                </Provider>
            );
        }
    }
}

export default App;
