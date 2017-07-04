import React from 'react';
import {StyleSheet, TextInput, View} from 'react-native';
import {observer} from "mobx-react";
import styles from "../styles";
import { Permissions } from 'expo';
import BarCodeScanner from './BarCodeScanner'

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
class CheckInScreen extends React.Component {
    static route = {
        navigationBar: {
            title: 'GreenToGo'
        }
    }

    state = {
      hasCameraPermission: null,
    }

    async componentWillMount() {
      const { status } = await Permissions.askAsync(Permissions.CAMERA);
      this.setState({hasCameraPermission: status === 'granted'});
    }

    _handleBarCodeRead = (data) => {
      let url = JSON.stringify(data.data);
      let locationCode = url.substr(url.lastIndexOf('/') + 1)
      alert(locationCode);
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

export default CheckInScreen;
