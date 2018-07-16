import React from 'react';
import { Constants } from 'expo';
import { observer, Provider } from 'mobx-react';
import styles from '../styles';
import LoginScreen from './LoginScreen';
import HomeScreen from './HomeScreen';
import MapScreen from './MapScreen';
import ScanQRCode from './ScanQRCode';
import SubmissionScreen from "./SubmissionScreen";
import ContainerSuccessScreen from "./ContainerSuccessScreen";
import AccountScreen from "./AccountScreen";
import SubscriptionScreen from "./SubscriptionScreen";

import { createStackNavigator } from 'react-navigation';

const RootStack = createStackNavigator(
    {
        home: HomeScreen,
        map: MapScreen,
        scanQRCode: ScanQRCode,
        submission: SubmissionScreen,
        containerSuccessScreen: ContainerSuccessScreen,
        account: AccountScreen,
        subscription: SubscriptionScreen
    },
    {
        initialRouteName: 'home',
        navigationOptions: {
            headerStyle: {
                backgroundColor: styles.primaryColor,
            },
            headerTintColor: '#ffffff',
            tintColor: styles.primaryCream,
            borderTopWidth: Constants.statusBarHeight,
            headerTitleStyle: {
                color: '#ffffff',
                fontWeight: 'bold',
            },
        }
    }
);

@observer
class App extends React.Component {
    render() {
        const store = this.props.store;
        if (!store.authToken) {
            return <LoginScreen store={store} />;
        } else {
            return (
                <Provider appStore={store}>
                    <RootStack />
                </Provider>
            );
        }
    }
}

export default App;
