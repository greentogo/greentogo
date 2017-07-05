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

    render() {
        return (
            <View style={{flex: 1}}>
                <BarCodeScanner
                  onBarCodeRead={this.props.handleBarCodeRead}
                  style={StyleSheet.absoluteFill}
                />
            </View>
        );
    }
}

export default BarCodeScannerReader;
