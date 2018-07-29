import React from 'react';
import {
    StyleSheet,
    View,
    TouchableHighlight
} from 'react-native';
import { inject, observer } from "mobx-react";
import styles from "../styles";
import {
    Content,
    List,
} from "native-base";
import ListMenuItem from './subcomponents/ListMenuItem';
import SubscriptionBanner from './subcomponents/SubscriptionBanner';
import G2GTitleImage from "./subcomponents/G2GTitleImage";


@inject("appStore")
@observer
class HomeScreen extends React.Component {
    constructor(props) {
        super(props)
        this.props.appStore.getUserData()
        this.props.appStore.getResturantData()
    }

    static navigationOptions = {
        headerTitle: <G2GTitleImage />,
    };

    goToMap = () => {
        this.props.navigation.navigate('map');
    }

    goToScanQRCode = () => {
        this.props.navigation.navigate('scanQRCode');
    }

    goToReturn = () => {
        this.props.navigation.navigate('returnBox');
    }

    goToAccount = () => {
        this.props.navigation.navigate('account');
    }

    logOut = () => {
        this.props.appStore.clearAuthToken()
    }

    render() {
        return (
            <Content style={styles.container}>
                <List>
                    <ListMenuItem
                        icon="log-out"
                        text="Check In/Out container"
                        onPress={this.goToScanQRCode}
                    />
                    <ListMenuItem
                        icon="map"
                        text="Map of participating restaurants"
                        onPress={this.goToMap}
                    />
                    <ListMenuItem
                        icon="person"
                        text="Your account"
                        onPress={this.goToAccount}
                    />
                    <ListMenuItem
                        icon="lock"
                        text="Log out"
                        onPress={this.logOut}
                    />
                </List>
                <SubscriptionBanner/>
            </Content>
        )
    }
}

export default HomeScreen;
