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
import BarCodeScannerReader from './BarCodeScannerReader'
import Subscription from './SubscriptionScreen'
import { Text } from 'react-native';
import styles from "../styles";

@inject("appStore")
@observer
class AccountScreen extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            ...this.props.appStore.user,
            redirectToWeb: false,
        }
    }

    static navigationOptions = {
        title: 'Account',
    };

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
                <View style={{ flex: 1, alignItems: 'center', backgroundColor: styles.primaryCream, paddingTop: 30 }}>
                    <Text style={{ paddingTop: 10, paddingBottom: 10, color: styles.primaryColor, fontWeight: 'bold', fontSize: 20 }}>Email: {this.state.email}</Text>
                    <Text style={{ paddingTop: 5, paddingBottom: 10, color: '#0000EE', fontSize: 14 }} onPress={() => { this.setState({ redirectToWeb: 'https://app.durhamgreentogo.com/account/change_password/' }) }}>Change Password</Text>
                    {/* <Subscription /> */}
                    <Text style={{ color: styles.primaryColor, fontWeight: 'bold', fontSize: 20 }}>{this.state.availableBoxes}/ {this.state.maxBoxes} boxes available</Text>
                    <Text style={{ paddingTop: 5, paddingBottom: 10, color: '#0000EE', fontSize: 14 }} onPress={() => { this.setState({ redirectToWeb: 'https://app.durhamgreentogo.com/account/change_payment_method/' }) }}>Change your default payment method</Text>
                    {/* <View style={{ flex: 1, justifyContent: 'center', backgroundColor: styles.primaryCream, paddingTop: 30 }}>
                    <Text style={{ color: styles.primaryColor, fontWeight: 'bold', fontSize: 26 }}>You've saved</Text>
                    <View style={{ flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
                        <Text style={{ color: styles.primaryColor, fontWeight: 'bold', fontSize: 40, paddingRight: 10 }}>12</Text>
                        <Image
                            source={require('../assets/icons/GTG-Box-App.png')}
                            style={{ height: 35, width: 35 }}
                        />
                        <Text style={{ color: styles.primaryColor, fontWeight: 'bold', fontSize: 40, paddingLeft: 10 }}>s</Text>
                    </View>
                    <Text style={{ color: styles.primaryColor, fontWeight: 'bold', fontSize: 26 }}>from a landfill</Text>
                </View> */}
                </View>
            )
        }
    }
}

export default AccountScreen;
