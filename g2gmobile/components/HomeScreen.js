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

    componentWillMount() {
        console.log("THE APPLICATION HOME SCREEN IS BEING CONSTRUCTED");
        console.log("@@@@@@@@@@@@");
        console.log("@@@@@@@@@@@@");
        console.log("@@@@@@@@@@@@");
        console.log("@@@@@@@@@@@@");
        let authToken = this.props.appStore.authToken;
        axios.get('me/', {
            headers: {
                'Authorization': `Token ${authToken}`
            }
        }).then((response) => {
            subscriptions = response.data.data.subscriptions;
            if (response.data.data.email) {
                this.props.appStore.email = response.data.data.email
            };
            if (subscriptions.length > 0) {
                this.subscriptionChange(subscriptions[0].id);
            }
        }).catch((error) => {
            console.log('ERROR HOMESCREEN.JS');
            console.log(error);
        })
    }

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

    subscriptionChange = (subscriptionId) => {
        let boxCount;
        let selectedSubscription;
        // find the selected subscription
        subscriptions.forEach((subscription) => {
            if (subscription.id === subscriptionId) {
                selectedSubscription = subscription;
            }
        });
        switch (this.props.appStore.action) {
            case 'IN':
                if (selectedSubscription.available_boxes === selectedSubscription.max_boxes) {
                    boxCount = 0;
                } else {
                    boxCount = 1;
                }
                break;
            case 'OUT':
                if (selectedSubscription.available_boxes === 0) {
                    boxCount = 0;
                } else {
                    boxCount = 1;
                }
                break;
        }

        this.setState({
            subscriptionId,
            boxCount,
            selectedSubscription
        });
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
