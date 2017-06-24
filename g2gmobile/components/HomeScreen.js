import React from 'react';
import {StyleSheet, TextInput, View} from 'react-native';
import {observer} from "mobx-react";
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
import stylesheet from "../styles";

class ListMenuItem extends React.Component {
    render() {
        return (
        <ListItem icon>
            <Left>
                <Icon name={this.props.icon}/>
            </Left>
            <Body>
                <Text>{this.props.text}</Text>
            </Body>
        </ListItem>
        );
    }
}

@observer
class HomeScreen extends React.Component {
    static route = {
        navigationBar: {
            title: 'GreenToGo'
        }
    }

    render() {
        return (
            <Container style={styles.container}>
                <Content>
                    <List>
                        <ListMenuItem icon="log-out" text="Check out container" />
                        <ListMenuItem icon="log-in" text="Return container" />
                        <ListMenuItem icon="map" text="Map of participating restaurants" />
                        <ListMenuItem icon="person" text="Your account" />
                    </List>
                </Content>
            </Container>
        )
    }
}

export default HomeScreen;
