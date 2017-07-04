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
      alert(JSON.stringify(data));
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
            <BarCodeScanner
              onBarCodeRead={this._handleBarCodeRead}
              style={StyleSheet.absoluteFill}
            />
          </View>
        );
      }
    }
}

export default CheckInScreen;
