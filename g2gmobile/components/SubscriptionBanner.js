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
import styles from "../styles";
import axios from '../apiClient';
import { Text } from "native-base";

@inject("appStore")
@observer
class SubscriptionBanner extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            ...this.props.appStore.user
        }
    }

    componentWillMount() {
        let authToken = this.props.appStore.authToken;
        axios.get(`stats/${this.props.appStore.user.username}/`, {
            headers: {
                'Authorization': `Token ${authToken}`
            }
        }).then((response) => {
            if (response.data && response.data.data) {
                let userBoxes = false;
                if (response.data.data.total_user_boxes_returned && response.data.data.total_user_boxes_returned > 0){
                    userBoxes = response.data.data.total_user_boxes_returned;
                }
                this.setState({ totalUserBoxesReturned: userBoxes, totalBoxesReturned: response.data.data.total_boxes_returned });
            }
        }).catch((error) => {
            if ((error.status && error.status === 401) || (error.response && error.response.status && error.response.status === 401)) {
                this.props.appStore.clearAuthToken();
            };
        })
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
            <Text style={styles.boldCenteredText}>
                {boxesAvailableBanner && boxesAvailableBanner}
            </Text>
        )
    }
}

export default SubscriptionBanner;
