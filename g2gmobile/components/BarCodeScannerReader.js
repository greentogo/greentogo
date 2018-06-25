import React from 'react';
import { StyleSheet, TextInput, View } from 'react-native';
import { inject, observer } from "mobx-react";
import axios from '../apiClient';
import styles from "../styles";
import { Permissions, BarCodeScanner } from 'expo';
import SubmissionScreen from './SubmissionScreen';

import {
    Container,
    Header,
    Body,
    Title,
    Content,
    Form,
    Item,
    Input,
    Button,
    List,
    ListItem,
    Text,
    Icon,
    Left,
    Right
} from "native-base";
import stylesheet from "../styles";

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
            this.setState({ barCodeScanned: true });
            let authToken = this.props.appStore.authToken;
            let url = JSON.stringify(data.data);
            url = "/locations/AY4LCB/"
            console.log("url @@@@@@@@@@@@@@@@@@@@@@@@@@@")
            console.log(url)
            let locationUrl = /(\/locations\/)([A-Z0-9]{6})/.exec(url);
            console.log("locationUrl @@@@@@@@@@@@@@@@@@@@@@@@@@@")
            console.log(locationUrl[1] + locationUrl[2])
            axios.get(locationUrl[1] + locationUrl[2], {
                headers: {
                    'Authorization': `Token ${authToken}`
                }
            }).then((response) => {
                this.props.appStore.locationCode = locationUrl[2];
                this.props.navigateNext(response.data.data);
                // this.props.store.setUserData(response.data.data);
            }).catch((err) => {
                console.log("ERROR");
                console.log(err.response);
            })
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
            return <Text> No camera view </Text>
        }
    }
}

export default BarCodeScannerReader;
