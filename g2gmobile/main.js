import React from 'react';
import Expo from 'expo';

import App from "./components/App";
import { AppStore } from "./stores";

import { observer } from 'mobx-react';

const store = new AppStore();

@observer class GreenToGo extends React.Component {
    state = { fontsAreLoaded: false };

    async componentWillMount() {
        await Expo.Font.loadAsync({
            'Roboto': require('native-base/Fonts/Roboto.ttf'),
            'Roboto_medium': require('native-base/Fonts/Roboto_medium.ttf'),
        });
        this.setState({fontsAreLoaded: true});
    }

    render() {
        if (!this.state.fontsAreLoaded) {
             return <Expo.AppLoading/>;
        }
        return (
            <App store={store} />
        );
    }
}

Expo.registerRootComponent(GreenToGo);
