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


@inject("appStore")
@observer
class HomeScreen extends React.Component {
    constructor(props) {
        super(props)
        this.props.appStore.getUserData()
    }

    static navigationOptions = {
        headerTitle: <G2GTitleImage />,
    };

    componentWillMount() {
        let authToken = this.props.appStore.authToken;
        axios.get('me/', {
            headers: {
                'Authorization': `Token ${authToken}`
            }
        }).then((response) => {
            subscriptions = response.data.data.subscriptions;
            if (response.data.data.email) this.props.appStore.email = response.data.data.email;
            console.log(response.data.data)
            if (subscriptions.length > 0) {
                this.subscriptionChange(subscriptions[0].id);
            }
        }).catch((error) => {
            console.log('In the error! HOMESCREEN.JS');
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
                console.log(selectedSubscription);
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
        let availableBoxes = "";
        let maxBoxes = "";
        let boxesAvailableBanner = false;
        if (this.props.appStore.user) {
            availableBoxes = this.props.appStore.user.availableBoxes + "";
            maxBoxes = this.props.appStore.user.maxBoxes + "";
            if (this.props.appStore.user.subscriptions.length > 0) {
                boxesAvailableBanner = `${availableBoxes} / ${maxBoxes} boxes available`;
            } else {
                boxesAvailableBanner = "You do not have a Subscription.";
            }
        }
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
                    <Text style={styles.boldCenteredText}>
                        {boxesAvailableBanner && boxesAvailableBanner}
                    </Text>
            </Content>
        )
    }
}

export default HomeScreen;
