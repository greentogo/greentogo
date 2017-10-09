import React from 'react';
import {
    StyleSheet,
    TextInput,
    View,
    Button,
    Image
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
            email: this.props.appStore.email || null
        }
    }

    static route = {
        navigationBar: {
            title: 'Account'
        }
    }

    render() {
        return (
            <View style={{ flex: 1, alignItems: 'center', backgroundColor: styles.primaryCream, paddingTop: 30 }}>
                <Text style={{ color: styles.primaryColor, fontWeight: 'bold', fontSize: 20 }}>damianhouse@gmail.com</Text>
                <Text style={{ color: '#0000EE', fontSize: 14 }} onPress={() => { this.setState({ type: 'passwordReset' }) }}>Reset Password</Text>
                <Subscription />
                <View style={{ flex: 1, justifyContent: 'center', backgroundColor: styles.primaryCream, paddingTop: 30 }}>
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
                </View>
            </View>
        )
    }
}

export default AccountScreen;
