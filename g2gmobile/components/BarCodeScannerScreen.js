import React from 'react';
import {StyleSheet, TextInput, View} from 'react-native';
import {observer} from "mobx-react";
import styles from "../styles";
import { Permissions, BarCodeScanner } from 'expo';

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

@observer
class BarCodeScannerScreen extends React.Component {
    constructor(props) {
      super(props)
      let state = {
        hasCameraPermission: null,
        locationCode: null
      }
    }


    static route = {
        navigationBar: {
            title: 'GreenToGo'
        }
    }

    async componentWillMount() {
      const { status } = await Permissions.askAsync(Permissions.CAMERA);
      this.setState({hasCameraPermission: status === 'granted'});
    }

    _handleBarCodeRead = (data) => {
      let url = JSON.stringify(data.data)
      let newUrl = url.substring(0, url.length - 2)
      let locationCode = newUrl.substr(newUrl.lastIndexOf('/') + 1)
      this.setState({locationCode})
      alert(JSON.stringify(this.state));
    }

    render() {
        return (
          <View style={{flex: 1}}>
            <BarCodeScanner
              onBarCodeRead={this._handleBarCodeRead}
              style={StyleSheet.absoluteFill}
            />
          </View>
        );
    }
}

export default BarCodeScannerScreen;
