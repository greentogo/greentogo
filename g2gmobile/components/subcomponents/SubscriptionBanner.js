import React from 'react';
import {
    StyleSheet,
    TextInput,
    View,
    Button,
    Image,
    WebView,
    Linking
} from 'react-native';
import { inject, observer } from "mobx-react";
import { Text } from "native-base";
import axios from '../../apiClient';
import styles from '../../styles';

@inject("appStore")
@observer
class SubscriptionBanner extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {
        let availableBoxes = "";
        let maxBoxes = "";
        let boxesAvailableBanner = false;
        if (this.props.appStore.user) {
            if (this.props.appStore.user.availableBoxes && this.props.appStore.user.subscriptions.length > 0) {
                availableBoxes = this.props.appStore.user.availableBoxes + "";
                maxBoxes = this.props.appStore.user.maxBoxes + "";
                boxesAvailableBanner = `${availableBoxes} / ${maxBoxes} boxes available`;
            } else {
                boxesAvailableBanner = "You do not have a Subscription.";
            }
        }
        return (
            <Text style={styles.subscriptionBanner}>
                {boxesAvailableBanner && boxesAvailableBanner}
            </Text>
        )
    }
}

export default SubscriptionBanner;
