import React from 'react';
import {
  StyleSheet,
  TextInput,
  View,
  TouchableHighlight
} from 'react-native';
import {inject, observer} from "mobx-react";
import styles from "../styles";

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

class ListMenuItem extends React.Component {
    render() {
        const onPress = this.props.onPress || function () { };
        return (
            <TouchableHighlight>
                <ListItem icon onPress={onPress}>
                    <Left>
                        <Icon name={this.props.icon}/>
                    </Left>
                    <Body>
                        <Text>{this.props.text}</Text>
                    </Body>
                </ListItem>
            </TouchableHighlight>
        );
    }
}

@inject("appStore")
@observer
class HomeScreen extends React.Component {
    static route = {
        navigationBar: {
            title: 'GreenToGo'
        }
    }

    goToMap = () => {
        this.props.navigator.push('map');
    }

    goToCheckOut = () => {
        this.props.navigator.push('checkOutBox');
    }

    goToReturn = () => {
        this.props.navigator.push('returnBox');
    }

    logOut = () => {
        this.props.appStore.clearAuthToken()
    }

    render() {
        return (
            <Container style={styles.container}>
                <Content>
                    <List>
                        <ListMenuItem
                            icon="log-out"
                            text="Checkout container"
                            onPress={this.goToCheckOut}
                        />
                        <ListMenuItem
                            icon="log-in"
                            text="Return container"
                            onPress={this.goToReturn}
                        />
                        <ListMenuItem
                            icon="map"
                            text="Map of participating restaurants"
                            onPress={this.goToMap}
                        />
                        <ListMenuItem
                            icon="person" 
                            text="Your account"
                        />
                        <ListMenuItem
                            icon="unlock"
                            text="Log out"
                            onPress={this.logOut}
                        />
                    </List>
                </Content>
            </Container>
        )
    }
}

export default HomeScreen;
