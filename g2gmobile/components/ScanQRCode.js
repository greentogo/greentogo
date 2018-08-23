import React from 'react';
import { StyleSheet, TextInput, View } from 'react-native';
import { inject, observer } from "mobx-react";
import { Permissions } from 'expo';
import BarCodeScannerReader from './subcomponents/BarCodeScannerReader';
import { Text } from 'react-native';

@inject("appStore")
@observer
class ScanQRCode extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            hasCameraPermission: false,
        }
    }

    static navigationOptions = {
        title: 'Scan QR Code',
    };

    navigateNext = (locationData) => {
        this.props.navigation.navigate('submission', { locationData: locationData });
    };

    // componentDidMount() {
    //     this.props.navigation.navigate('submission', { locationData: {
    //         code: 'GW6VRU',
    //         service: 'IN',
    //         name: "Rose's Noodles, Dumplings & Sweets"
    //     } });
    // }

    render() {
        return (
            <View style={{ flex: 1 }}>
                <BarCodeScannerReader navigateNext={this.navigateNext} />
            </View>
        );
    }
}

export default ScanQRCode;
