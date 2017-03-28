import React from 'react';
import {
    StyleSheet,
    Text,
    TextInput,
    View,
} from 'react-native';

import { createStore, applyMiddleware, combineReducers } from 'redux';
import { Provider } from 'react-redux';
import promiseMiddleware from 'redux-promise';
import { createLogger } from 'redux-logger';

import Expo from 'expo';

import {
    createRouter,
    NavigationProvider,
    StackNavigation,
} from '@expo/ex-navigation';

import reducer from './reducer';
import stylesheet from './styles';

import App from "./components/App";
import LoginScreen from "./components/LoginScreen";

const logger = createLogger({
    colors: {
        title: false,
        prevState: false,
        action: false,
        nextState: false,
        error: false,
    }
})

const store = createStore(reducer, applyMiddleware(promiseMiddleware, logger));

class ReduxApp extends React.Component {
    render() {
        return (
            <Provider store={store}>
                <App />
            </Provider>
        )
    }
}

Expo.registerRootComponent(ReduxApp)
