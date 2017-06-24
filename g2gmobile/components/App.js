import React from 'react';
import {
    StyleSheet,
    Text,
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
} from "native-base";

import {observer} from "mobx-react";

import {
    createRouter,
    NavigationProvider,
    StackNavigation,
} from '@expo/ex-navigation';

import LoginScreen from "./LoginScreen";
import HomeScreen from "./HomeScreen";
import stylesheet from "../styles";

const Router = createRouter(() => ({
    home: () => HomeScreen,
}));

@observer class App extends React.Component {
    render() {
        const store = this.props.store;

        if (!store.authToken) {
            console.log("stylesheet.container", stylesheet)
            return (<LoginScreen store={store} />);
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
