import React from 'react';
import {StyleSheet, TextInput, View} from 'react-native';
import {inject, observer} from "mobx-react";
import styles from "../styles";
import { Permissions } from 'expo';
import BarCodeScanner from './BarCodeScannerScreen'

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
class CheckOutScreen extends React.Component {
    constructor(props) {
      super(props)
      let state = {
        hasCameraPermission: null,
        checkOut: true,
        locationCode: null
      }
    }
    static route = {
        navigationBar: {
            title: 'GreenToGo Check Out Boxes'
        }
    }

    async componentWillMount() {
      const { status } = await Permissions.askAsync(Permissions.CAMERA);
      this.setState({hasCameraPermission: status === 'granted'});
    }

    render() {
      const { hasCameraPermission } = this.state;
      if (hasCameraPermission === null) {
        return <View />;
      } else if (hasCameraPermission === false) {
        return <Text>No access to camera</Text>;
      } else {
        return (
          <View style={{flex: 1}}>
            <BarCodeScanner />
          </View>
        );
      }
    }
}

export default CheckOutScreen;
