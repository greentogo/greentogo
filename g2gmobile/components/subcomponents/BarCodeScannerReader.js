import React from 'react';
import { StyleSheet, View } from 'react-native';
import { inject, observer } from "mobx-react";
import { Permissions, BarCodeScanner } from 'expo';
import {
    Text,
} from "native-base";
import axios from '../../apiClient';

@inject("appStore")
@observer
class BarCodeScannerReader extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            barCodeScanned: false
        }
    }

    async componentWillMount() {
        const { status } = await Permissions.askAsync(Permissions.CAMERA);
        this.setState({ hasCameraPermission: status === 'granted' });
    }

    handleBarCodeRead = (data) => {
        if (!this.state.barCodeScanned) {
            let authToken = this.props.appStore.authToken;
            let url = JSON.stringify(data.data);
            this.setState({ barCodeScanned: true }, () => {
                let locationUrl = /(\/locations\/)([A-Z0-9]{6})/.exec(url);
                if (locationUrl && locationUrl[1] && locationUrl[2]) {
                    axios.get(locationUrl[1] + locationUrl[2], {
                        headers: {
                            'Authorization': `Token ${authToken}`
                        }
                    }).then((response) => {
                        if (response.data && response.data.data && response.data.data.code){
                            this.props.navigateNext(response.data.data);
                        } else {
                            this.setState({ barCodeScanned: false });
                        }
                    }).catch((error) => {
                        axios.post('/log/', {'context': 'BarCodeScannerReader.js', 'error': error, 'message': error.message, 'stack': error.stack});
                        this.setState({ barCodeScanned: false });
                    })
                } else {
                    this.setState({ barCodeScanned: false });
                }
            });
        }
    }

    render() {
        if (this.state.hasCameraPermission) {
            return (
                <View style={{ flex: 1 }}>
                    <BarCodeScanner
                        onBarCodeRead={this.handleBarCodeRead}
                        style={StyleSheet.absoluteFill}
                    />
                </View>
            );
        } else {
            return <Text> No camera view. Please give GreenToGo permission to access your camera so we can read QR codes! </Text>
        }
    }
}

export default BarCodeScannerReader;
