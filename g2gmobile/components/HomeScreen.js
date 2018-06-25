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

class ListMenuItem extends React.Component {
    render() {
        const onPress = this.props.onPress || function () { };
        return (
            <TouchableHighlight>
                <ListItem style={{ flex: 1, height: 100, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: styles.primaryColor, backgroundColor: styles.primaryCream }} icon onPress={onPress}>
                    <Left>
                        <Icon style={{ color: styles.primaryColor }} name={this.props.icon} />
                    </Left>
                    <Body style={{ borderBottomWidth: 0 }}>
                        <Text>{this.props.text}</Text>
                    </Body>
                </ListItem>
            </TouchableHighlight>
        );
    }
}

@inject("appStore")
@observer
class HomeScreen extends React.Component {
    constructor(props) {
        super(props)
        this.props.appStore.getUserData()
    }

    static route = {
        navigationBar: {
            renderTitle: (route, props) => <G2GTitleImage />,
            backgroundColor: '#628e86'
        }
    }
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
        this.props.navigator.push('map');
    }

    goToScanQRCode = () => {
        this.props.navigator.push('scanQRCode');
    }

    goToReturn = () => {
        this.props.navigator.push('returnBox');
    }

    goToAccount = () => {
        this.props.navigator.push('account')
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
      let availableBoxes = this.props.appStore.user.availableBoxes + "";
      let maxBoxes = this.props.appStore.user.maxBoxes + "";
      let boxesAvailableBanner = "You do not have a Subscription."
      if (this.props.appStore.user.subscriptions.length > 0){
          boxesAvailableBanner = `${availableBoxes} / ${maxBoxes} boxes available`;
      }
        return (
            <Content style={{ flex: 1, backgroundColor: styles.primaryCream }}>
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
                        icon="unlock"
                        text="Log out"
                        onPress={this.logOut}
                    />
                </List>
                <View style={{ flex: 1, alignItems: 'center' }}>
                    <Text style={{ color: styles.primaryColor, fontWeight: 'bold', fontSize: 20 }}>
                    {boxesAvailableBanner}
                    </Text>
                </View>
            </Content>
        )
    }
}

export default HomeScreen;
