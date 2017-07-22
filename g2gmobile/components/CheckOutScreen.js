import React from 'react';
import {StyleSheet, TextInput, View} from 'react-native';
import {inject, observer} from "mobx-react";
import { Permissions } from 'expo';
import BarCodeScannerReader from './BarCodeScannerReader';
import { Text } from 'react-native';

@inject("appStore")
@observer
class CheckOutScreen extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
        hasCameraPermission: false
    }
    this.props.appStore.action = "OUT";
  }

  static route = {
    navigationBar: {
        title: 'Checkout container'
    }
  }

  navigateNext = () => {
    this.props.navigator.push('submission');
  };

  render() {
    return (
      <View style={{flex: 1}}>
        <BarCodeScannerReader navigateNext={this.navigateNext}/>
      </View>
    );
  }
}

export default CheckOutScreen;
