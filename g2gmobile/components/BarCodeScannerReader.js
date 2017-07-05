import React from 'react';
import {StyleSheet, TextInput, View} from 'react-native';
import {inject, observer} from "mobx-react";
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
    }

    async componentWillMount() {
        const { status } = await Permissions.askAsync(Permissions.CAMERA);
        this.setState({hasCameraPermission: status === 'granted'});
    }

    _handleBarCodeRead = (data) => {
        let url = JSON.stringify(data.data);
        let newUrl = url.substring(0, url.length - 2);
        let locationCode = newUrl.substr(newUrl.lastIndexOf('/') + 1);
        this.props.appStore.locationCode = locationCode;
        if (this.props.appStore.action === 'checkOutBox') {
            alert("You checked out a box");
        } else {
            alert("You returned a box");
        }
    }

    render() {
        return (
            <View style={{flex: 1}}>
                <BarCodeScanner
                  onBarCodeRead={this._handleBarCodeRead}
                  style={StyleSheet.absoluteFill}
                />

          <SubmissionScreen />
            </View>
        );
    }
}

export default BarCodeScannerReader;
