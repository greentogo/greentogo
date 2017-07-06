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
        this.state = {
            barCodeScanned: false
        }
    }

    async componentWillMount() {
        const { status } = await Permissions.askAsync(Permissions.CAMERA);
        this.setState({hasCameraPermission: status === 'granted'});
    }

    handleBarCodeRead = (data) => {
        if ( !this.state.barCodeScanned ) {
            let url = JSON.stringify(data.data);
            let newUrl = url.substring(0, url.length - 2);
            let locationCode = newUrl.substr(newUrl.lastIndexOf('/') + 1);
            this.props.appStore.locationCode = locationCode;
            this.setState({barCodeScanned: true});
            this.props.navigateNext();
        }
    }

    render() {
        if ( this.state.hasCameraPermission ) {
            return (
                <View style={{flex: 1}}>
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
