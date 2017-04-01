import React from 'react';
import Expo from 'expo';

import App from "./components/App";
import { AppStore } from "./stores";

const store = new AppStore();

class GreenToGo extends React.Component {
    render() {
        return (
            <App store={store} />
        )
    }
}

Expo.registerRootComponent(GreenToGo);
