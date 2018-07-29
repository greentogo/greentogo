import React from 'react';
import {
    StyleSheet,
    TextInput,
    View,
    Button,
    Image,
    WebView,
    Linking
} from 'react-native';
import { inject, observer } from "mobx-react";
import styles from "../styles";
import axios from '../apiClient';
import {
    Content,
    Text,
} from "native-base";

@inject("appStore")
@observer
class EditNameEmailScreen extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            ...this.props.appStore.user,
        }
    }

    static navigationOptions = {
        title: 'Edit Name and Email',
        headerTitleStyle: { width: 300 }
    };

    render() {
        return (
            <Content style={styles.container}>
                <Text style={styles.boldCenteredText}>Email: {this.state.email}</Text>
                <Text style={styles.boldCenteredText}>Name: {this.state.name}</Text>
            </Content>
        )
    }
}

export default EditNameEmailScreen;
