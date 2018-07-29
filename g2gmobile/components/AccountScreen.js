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
import { Permissions } from 'expo';
import Subscription from './SubscriptionScreen'
// import { Text } from 'react-native';
import styles from "../styles";
import axios from '../apiClient';
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
import ListMenuItem from './ListMenuItem';

@inject("appStore")
@observer
class AccountScreen extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            ...this.props.appStore.user,
            redirectToWeb: false,
            totalBoxesReturned: false,
            totalUserBoxesReturned: false
        }
    }

    static navigationOptions = {
        title: 'Account',
    };

    componentWillMount() {
        let authToken = this.props.appStore.authToken;
        axios.get(`stats/${this.props.appStore.user.username}/`, {
            headers: {
                'Authorization': `Token ${authToken}`
            }
        }).then((response) => {
            if (response.data.data) {
                this.setState({ totalUserBoxesReturned: response.data.data.total_user_boxes_returned, totalBoxesReturned: response.data.data.total_boxes_returned });
            }
            console.log(response.data.data)
        }).catch((error) => {
            if (err.response.status === 401) {
                this.props.appStore.clearAuthToken();
            };
            console.log(error);
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
            console.log("Account State: ", this.state)
            console.log(this.state.username)
            return (
                <Content style={styles.container}>
                    <Text style={styles.boldCenteredText}>Email: {this.state.email}</Text>
                    <List>
                        <ListMenuItem
                            icon="log-out"
                            text="Change your default payment method"
                            onPress={() => { this.setState({ redirectToWeb: 'https://app.durhamgreentogo.com/account/change_payment_method/' }) }}
                        />
                        <ListMenuItem
                            icon="person"
                            text="View/Edit Subscriptions"
                            onPress={() => { this.setState({ redirectToWeb: 'https://app.durhamgreentogo.com/subscriptions/' }) }}
                        />
                        <ListMenuItem
                            icon="unlock"
                            text="Change Password"
                            onPress={() => { this.setState({ redirectToWeb: 'https://app.durhamgreentogo.com/account/change_password/' }) }}
                        />
                    </List>
                    {/* <Subscription /> */}
                    <Text style={{ alignSelf: 'center', color: styles.primaryColor, fontWeight: 'bold', fontSize: 20 }}>{this.state.availableBoxes}/ {this.state.maxBoxes} boxes available</Text>
                    {this.state.totalBoxesReturned &&
                        <View style={{ flex: 1, justifyContent: 'center', backgroundColor: styles.primaryCream, paddingTop: 10, }}>
                            <Text style={{ textAlign: 'center', color: styles.primaryColor, fontWeight: 'bold', fontSize: 26 }}>Our community</Text>
                            <Text style={{ textAlign: 'center', color: styles.primaryColor, fontWeight: 'bold', fontSize: 26 }}>has saved</Text>
                            <View style={{ flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
                                <Text style={{ color: styles.primaryColor, fontWeight: 'bold', fontSize: 40, paddingRight: 10 }}>{this.state.totalBoxesReturned}</Text>
                                <Image
                                    source={require('../assets/icons/GTG-Box-App.png')}
                                    style={{ height: 35, width: 35 }}
                                />
                                <Text style={{ color: styles.primaryColor, fontWeight: 'bold', fontSize: 40, paddingLeft: 10 }}>s</Text>
                            </View>
                            <Text style={{ textAlign: 'center', color: styles.primaryColor, fontWeight: 'bold', fontSize: 26 }}>from a landfill</Text>
                        </View>
                    }
                    {this.state.totalUserBoxesReturned &&
                        <View style={{ flex: 1, justifyContent: 'center', backgroundColor: styles.primaryCream, paddingTop: 10 }}>
                            <Text style={{ textAlign: 'center', color: styles.primaryColor, fontWeight: 'bold', fontSize: 26 }}>You've saved</Text>
                            <View style={{ flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
                                <Text style={{ color: styles.primaryColor, fontWeight: 'bold', fontSize: 40, paddingRight: 10 }}>{this.state.totalUserBoxesReturned}</Text>
                                <Image
                                    source={require('../assets/icons/GTG-Box-App.png')}
                                    style={{ height: 35, width: 35 }}
                                />
                                <Text style={{ color: styles.primaryColor, fontWeight: 'bold', fontSize: 40, paddingLeft: 10 }}>s</Text>
                            </View>
                        </View>
                    }
                </Content>
            )
        }
    }
}

export default AccountScreen;
