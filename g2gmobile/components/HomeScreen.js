import React from 'react';
import {
    StyleSheet,
    View,
    TouchableHighlight
} from 'react-native';
import { inject, observer } from "mobx-react";
import styles from "../styles";
import G2GTitleImage from "./G2GTitleImage";
import {
    Header,
    Body,
    Content,
    List,
    ListItem,
    Text,
    Icon,
    Left
} from "native-base";
import axios from '../apiClient';
import ListMenuItem from './ListMenuItem';
import SubscriptionBanner from './SubscriptionBanner';


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
