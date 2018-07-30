import React from 'react';
import {
    View,
    Image,
    WebView,
    Linking
} from 'react-native';
import { inject, observer } from "mobx-react";
import styles from "../styles";
import axios from '../apiClient';
import {
    Content,
    List,
    Text
} from "native-base";
import ListMenuItem from './subcomponents/ListMenuItem';
import SubscriptionBanner from './subcomponents/SubscriptionBanner';
import CommunityBoxes from "./subcomponents/CommunityBoxes";

@inject("appStore")
@observer
class AccountScreen extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            ...this.props.appStore.user,
            redirectToWeb: false
        }
    }

    static navigationOptions = {
        title: 'Account',
    };

    goToNameAndEmail = () => {
        this.props.navigation.navigate('editnameemail');
    }

    componentWillMount() {
        let authToken = this.props.appStore.authToken;
        axios.get(`/stats/${this.props.appStore.user.username}/`, {
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
        if (this.state.redirectToWeb) {
            let uri = this.state.redirectToWeb;
            return (
                <WebView
                    ref={(ref) => { this.webview = ref; }}
                    source={{ uri }}
                    onNavigationStateChange={(event) => {
                        this.setState({ redirectToWeb: false })
                        Linking.openURL(event.url);
                        this.webview.stopLoading();
                    }}
                />
            );
        } else {
            return (
                <Content style={styles.container}>
                    <List>
                        <ListMenuItem
                            icon="person"
                            text="View/Edit Name and Email"
                            onPress={this.goToNameAndEmail}
                        />
                        <ListMenuItem
                            icon="card"
                            text="Change your default payment method"
                            onPress={() => { this.setState({ redirectToWeb: 'https://app.durhamgreentogo.com/account/change_payment_method/' }) }}
                        />
                        <ListMenuItem
                            icon="document"
                            text="View/Edit Subscriptions"
                            onPress={() => { this.setState({ redirectToWeb: 'https://app.durhamgreentogo.com/subscriptions/' }) }}
                        />
                        <ListMenuItem
                            icon="lock"
                            text="Change Password"
                            onPress={() => { this.setState({ redirectToWeb: 'https://app.durhamgreentogo.com/account/change_password/' }) }}
                        />
                    </List>
                    <SubscriptionBanner/>
                    <CommunityBoxes/>
                </Content>
            )
        }
    }
}

export default AccountScreen;
