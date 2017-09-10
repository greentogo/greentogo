import React from 'react';
import { Constants } from 'expo';
import {observer, Provider} from 'mobx-react';
import {
    StyleSheet,
    Text,
    View,
} from 'react-native';
import LoginScreen from './LoginScreen';
import HomeScreen from './HomeScreen';
import MapScreen from './MapScreen';
import CheckOutScreen from './CheckOutScreen';
import styles from '../styles';
import ReturnBox from "./ReturnScreen";
import SubmissionScreen from "./SubmissionScreen";
import CheckOutSuccessScreen from "./CheckOutSuccessScreen";
import ReturnSuccessScreen from "./ReturnSuccessScreen";
import stylesheet from "../styles";
import {
    createRouter,
    NavigationProvider,
    StackNavigation
} from '@expo/ex-navigation';

const Router = createRouter(() => ({
    home: () => HomeScreen,
    map: () => MapScreen,
    checkOutBox: () => CheckOutScreen,
    returnBox: () => ReturnBox,
    submission: () => SubmissionScreen,
    checkOutSuccess: () => CheckOutSuccessScreen,
    returnSuccess: () => ReturnSuccessScreen
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
